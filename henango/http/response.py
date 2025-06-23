from typing import Optional


class HttpResponse:
    status_code: int
    content_type: Optional[str]
    body: bytes

    def __init__(
        self, status_code: int, content_type: Optional[str] = None, body: bytes = b""
    ):
        self.status_code = status_code
        self.content_type = content_type
        self.body = body
