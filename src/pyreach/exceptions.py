class HTTPServerError(RuntimeError):
    """Rased when the API responds with a 5xx status code"""

    pass


class HTTPClientError(RuntimeError):
    """Rased when the API responds with a 4xx status code"""

    pass


class HTTPRateLimitError(HTTPClientError):
    """Rased when the API responds with a 429 status code"""

    pass


class HTTPUnknownError(RuntimeError):
    """Rased when the API responds with a non-OK status code that isn't otherwise handled"""

    pass
