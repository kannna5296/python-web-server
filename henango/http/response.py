from typing import Optional, Union


class HttpResponse:
    status_code: int
    content_type: Optional[str]
    body: Union[bytes, str]

    def __init__(
        self, status_code: int, content_type: Optional[str] = None, body: Union[bytes, str] = b""
    ):
        self.status_code = status_code
        self.content_type = content_type
        self.body = body
