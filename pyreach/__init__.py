import requests
import logging
from tenacity import *

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


class Reach:
    def __init__(self, client_id, api_key, api_secret, page_size=200) -> None:
        self.base_url = f"https://{client_id}.reachapp.co"
        self.http_auth = (api_key, api_secret)
        self.page_size = page_size

    @retry(
        reraise=True,
        retry=(
            retry_if_exception_type(HTTPServerError)
            | retry_if_exception_type(HTTPRateLimitError)
        ),
        wait=wait_exponential(multiplier=1, min=1, max=16),
        stop=stop_after_attempt(RETRY_ATTEMPTS),
    )
    def _get_page(self, endpoint, api_version=DEFAULT_API_VERSION, params=None):
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
            log.warning("Rate limited, retrying if able.")
            # log.debug(response.text)
        elif int(response.status_code / 100) == 4:
            log.error("Something is wrong with the request")
            raise HTTPClientError(response.text)
        elif int(response.status_code / 100) == 5:
            log.warning("Something is wrong with the server, retrying if able")
            # log.debug(response.text)
            raise HTTPServerError(response.text)
        else:
            log.error("Something is wrong, and I'm not sure what")
            raise HTTPUnknownError(response.text)

    def _get(self, endpoint, api_version=DEFAULT_API_VERSION, **kwargs):
        output_list = list()
        this_page = 1
        while True:
            params = {**kwargs, "per_page": self.page_size, "page": this_page}
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
                    "No more pages to get.  Exiting loop and returning records to caller."
                )
                break

        return output_list

    def dispatcher(self, object_name):
        function_map = {
            "albums": self.get_albums,
            "campaigns": self.get_campaigns,
            "custom_forms": self.get_custom_forms,
            "donation_categories": self.get_donation_categories,
            "donations": self.get_donations,
            "events": self.get_events,
            "groups": self.get_groups,
            "group_supporters": self.get_group_supporters,
            "pages": self.get_pages,
            "places": self.get_places,
            "products": self.get_products,
            "projects": self.get_projects,
            "sponsorship_supporters": self.get_sponsorship_supporters,
            "sponsorships": self.get_sponsorships,
            "supporters": self.get_supporters,
            "trips": self.get_trips,
            "trip_supporters": self.get_trip_supporters,
            "uploads": self.get_uploads,
            "videos": self.get_videos,
        }
        return function_map[object_name]

    def get_object(self, object, api_version=DEFAULT_API_VERSION, **kwargs):
        response = self._get(object, api_version, **kwargs)
        return response

    def get_albums(self, api_version=DEFAULT_API_VERSION, **kwargs):
        response = self.get_object("albums", api_version, **kwargs)
        return response

    def get_campaigns(self, api_version=DEFAULT_API_VERSION, **kwargs):
        response = self.get_object("campaigns", api_version, **kwargs)
        return response

    def get_custom_forms(self, api_version=DEFAULT_API_VERSION, **kwargs):
        response = self.get_object("custom_forms", api_version, **kwargs)
        return response

    def get_donation_categories(self, api_version=DEFAULT_API_VERSION, **kwargs):
        response = self.get_object("donation_categories", api_version, **kwargs)
        return response

    def get_donations(self, api_version=DEFAULT_API_VERSION, **kwargs):
        response = self.get_object("donations", api_version, **kwargs)
        return response

    def get_events(self, api_version=DEFAULT_API_VERSION, **kwargs):
        response = self.get_object("events", api_version, **kwargs)
        return response

    # TODO: event_registrations

    def get_groups(self, api_version=DEFAULT_API_VERSION, **kwargs):
        response = self.get_object("groups", api_version, **kwargs)
        return response

    # TODO: group_supporters
    def get_group_supporters(self, api_version=DEFAULT_API_VERSION, **kwargs):
        groups = self.get_groups(api_version=api_version, **kwargs)
        response_list = []
        for group in groups:
            response = self.get_object(
                f'groups/{group["id"]}/supporters', api_version, **kwargs
            )
            # Add group_id to each record
            enriched_response = [{"group_id": group["id"], **r} for r in response]
            response_list.extend(enriched_response)
        return response_list

    def get_pages(self, api_version=DEFAULT_API_VERSION, **kwargs):
        response = self.get_object("pages", api_version, **kwargs)
        return response

    def get_places(self, api_version=DEFAULT_API_VERSION, **kwargs):
        response = self.get_object("places", api_version, **kwargs)
        return response

    # TODO: place albums
    # TODO: place messages
    # TODO: place sponsorships

    def get_products(self, api_version=DEFAULT_API_VERSION, **kwargs):
        response = self.get_object("products", api_version, **kwargs)
        return response

    def get_projects(self, api_version=DEFAULT_API_VERSION, **kwargs):
        response = self.get_object("projects", api_version, **kwargs)
        return response

    def get_sponsorship_supporters(self, api_version=DEFAULT_API_VERSION, **kwargs):
        response = self.get_object("sponsorship_supporters", api_version, **kwargs)
        return response

    def get_sponsorships(self, api_version=DEFAULT_API_VERSION, **kwargs):
        response = self.get_object("sponsorships", api_version, **kwargs)
        return response

    # TODO: sponsorship_sponsors
    # TODO: sponsorship_albums
    # TODO: sponsorship_messages
    # TODO: sponsorship_custom_tables?

    def get_supporters(self, api_version=DEFAULT_API_VERSION, **kwargs):
        response = self.get_object("supporters", api_version, **kwargs)
        return response

    def get_trips(self, api_version=DEFAULT_API_VERSION, **kwargs):
        response = self.get_object("trips", api_version, **kwargs)
        return response

    # TODO: trip_supporters
    def get_trip_supporters(self, api_version=DEFAULT_API_VERSION, **kwargs):
        trips = self.get_trips(api_version=api_version, **kwargs)
        response_list = []
        for trip in trips:
            response = self.get_object(
                f'trips/{trip["id"]}/supporters', api_version, **kwargs
            )
            # Add trip_id to each record
            enriched_response = [{"trip_id": trip["id"], **r} for r in response]
            response_list.extend(enriched_response)
        return response_list

    def get_uploads(self, api_version=DEFAULT_API_VERSION, **kwargs):
        response = self.get_object("uploads", api_version, **kwargs)
        return response

    def get_users(self, api_version=DEFAULT_API_VERSION, **kwargs):
        response = self.get_object("user", **kwargs)
        return response

    # TODO: user_campaigns?
    # TODO: user_conversations
    # TODO: user_conversation_messages
    # TODO: user_donations?
    # TODO: user_sponsorship_supporters?

    def get_videos(self, api_version=DEFAULT_API_VERSION, **kwargs):
        response = self.get_object("videos", api_version, **kwargs)
        return response


if __name__ == "__main__":
    pass
