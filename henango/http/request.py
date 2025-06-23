class HttpRequest:
    path: str
    method: str
    http_version: str
    headers: dict
    body: bytes

    def __init__(
        self,
        path: str = "",
        method: str = "",
        http_version: str = "",
        headers: dict = {},
        body: bytes = b"",
    ):
        self.path = path
        self.method = method
        self.http_version = http_version
        self.headers = headers
        self.body = body
