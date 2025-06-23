from typing import Optional, Union, List

from henango.http.cookie import Cookie


class HttpResponse:
    status_code: int
    headers: dict
    cookies: List[Cookie]
    content_type: Optional[str]
    body: Union[bytes, str]

    def __init__(
        self,
        status_code: int = 200,
        headers: dict = {},
        cookies: List[Cookie] = [],
        content_type: Optional[str] = None,
        body: Union[bytes, str] = b"",
    ):
        self.status_code = status_code
        self.headers = headers
        self.content_type = content_type
        self.body = body
        self.cookies = cookies
