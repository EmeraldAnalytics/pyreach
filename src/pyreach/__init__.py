import requests
import logging
from tenacity import *
from typing import Any, Dict, List, Optional

from pyreach.exceptions import (
    HTTPServerError,
    HTTPClientError,
    HTTPRateLimitError,
    HTTPUnknownError,
)

log_config = {
    "format": "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(funcName)s - %(message)s",
    "datefmt": "%Y-%m-%d %H:%M:%S",
}
logging.basicConfig(**log_config)
log = logging.getLogger()
log.setLevel(logging.INFO)
log.info("Script started")

DATE_FMT = "%Y-%m-%d"
RETRY_ATTEMPTS = 10
DEFAULT_API_VERSION = 2


class BaseResource:
    """Base class for all API resources"""

    def __init__(self, client: "Reach", endpoint: str):
        self.client = client
        self.endpoint = endpoint

    def get_all(
        self, api_version: int = DEFAULT_API_VERSION, **kwargs
    ) -> List[Dict[str, Any]]:
        return self.client.get_object(self.endpoint, api_version, **kwargs)


class NestedResource(BaseResource):
    """Base class for nested resources that require parent ID"""

    def __init__(
        self,
        client: "Reach",
        parent_endpoint: str,
        child_endpoint: str,
        parent_id_field: str,
    ):
        super().__init__(client, f"{parent_endpoint}/{{parent_id}}/{child_endpoint}")
        self.parent_endpoint = parent_endpoint
        self.child_endpoint = child_endpoint
        self.parent_id_field = parent_id_field

    def get_all(
        self, api_version: int = DEFAULT_API_VERSION, **kwargs
    ) -> List[Dict[str, Any]]:
        parents = self.client.get_object(self.parent_endpoint, api_version, **kwargs)
        response_list = []
        for parent in parents:
            response = self.client.get_object(
                self.endpoint.format(parent_id=parent["id"]), api_version, **kwargs
            )
            enriched_response = [
                {self.parent_id_field: parent["id"], **r} for r in response
            ]
            response_list.extend(enriched_response)
        return response_list


class Reach:
    def __init__(
        self, client_id: str, api_key: str, api_secret: str, page_size: int = 200
    ) -> None:
        self.base_url = f"https://{client_id}.reachapp.co"
        self.http_auth = (api_key, api_secret)
        self.page_size = page_size

        # Initialize resource classes
        self._init_resources()

    def _init_resources(self) -> None:
        """Initialize all resource classes"""
        # Simple resources
        self.albums = BaseResource(self, "albums")
        self.campaigns = BaseResource(self, "campaigns")
        self.custom_forms = BaseResource(self, "custom_forms")
        self.donation_categories = BaseResource(self, "donation_categories")
        self.donations = BaseResource(self, "donations")
        self.events = BaseResource(self, "events")
        self.groups = BaseResource(self, "groups")
        self.pages = BaseResource(self, "pages")
        self.places = BaseResource(self, "places")
        self.products = BaseResource(self, "products")
        self.projects = BaseResource(self, "projects")
        self.sponsorship_supporters = BaseResource(self, "sponsorship_supporters")
        self.sponsorships = BaseResource(self, "sponsorships")
        self.supporters = BaseResource(self, "supporters")
        self.trips = BaseResource(self, "trips")
        self.uploads = BaseResource(self, "uploads")
        self.videos = BaseResource(self, "videos")

        # Nested resources
        self.group_supporters = NestedResource(self, "groups", "supporters", "group_id")
        self.trip_supporters = NestedResource(self, "trips", "supporters", "trip_id")

    @retry(
        reraise=True,
        retry=retry_if_exception_type(
            (HTTPServerError, HTTPClientError, HTTPRateLimitError, HTTPUnknownError)
        ),
        wait=wait_exponential(multiplier=1, min=1, max=16),
        stop=stop_after_attempt(RETRY_ATTEMPTS),
    )
    def _get_page(
        self,
        endpoint: str,
        api_version: int = DEFAULT_API_VERSION,
        params: Optional[Dict] = None,
    ) -> requests.Response:
        headers = {
            "Content-type": "application/json",
        }
        url = f"{self.base_url}/api/v{api_version}/{endpoint}"
        log.info(f"GET from {url}")
        log.info(f"Params: {params}")
        response = requests.get(
            url=url, headers=headers, auth=self.http_auth, params=params
        )
        if response.ok:
            return response
        elif response.status_code == 429:
            log.warning("Rate limited.")
            raise HTTPRateLimitError(response.text)
        elif int(response.status_code / 100) == 4:
            log.error("Something is wrong with the request")
            raise HTTPClientError(response.text)
        elif int(response.status_code / 100) == 5:
            log.warning("Something is wrong with the server")
            raise HTTPServerError(response.text)
        else:
            log.error("Something is wrong, and I'm not sure what")
            raise HTTPUnknownError(response.text)

    def _get(
        self, endpoint: str, api_version: int = DEFAULT_API_VERSION, **kwargs
    ) -> List[Dict[str, Any]]:
        output_list = list()
        this_page = 1
        while True:
            params = {"per_page": self.page_size, "page": this_page, **kwargs}
            response = self._get_page(endpoint, api_version, params=params)
            log.info(f"{len(response.json())} records returned on page {this_page}")
            output_list.extend(response.json())
            if len(response.json()) == self.page_size:
                log.info(
                    "More pages to get. Incrementing this_page and re-entering loop"
                )
                this_page += 1
            else:
                log.info(
                    "No more pages to get. Exiting loop and returning records to caller."
                )
                break
        return output_list

    def get_object(
        self, object: str, api_version: int = DEFAULT_API_VERSION, **kwargs
    ) -> List[Dict[str, Any]]:
        return self._get(object, api_version, **kwargs)

    def get_users(
        self, api_version: int = DEFAULT_API_VERSION, **kwargs
    ) -> List[Dict[str, Any]]:
        return self.get_object("user", **kwargs)


if __name__ == "__main__":
    pass
