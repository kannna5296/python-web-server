class HttpRequest:
    path: str
    method: str
    http_version: str
    headers: dict
    cookies: dict
    body: bytes
    params: dict

    def __init__(
        self,
        path: str = "",
        method: str = "",
        http_version: str = "",
        headers: dict = {},
        body: bytes = b"",
        params: dict = {},
        cookies: dict = {},
    ):
        self.path = path
        self.method = method
        self.http_version = http_version
        self.headers = headers
        self.body = body
        self.params = params
        self.cookies = cookies
