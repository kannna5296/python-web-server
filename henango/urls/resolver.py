from typing import Callable, Optional

from henango.http.request import HttpRequest
from henango.http.response import HttpResponse
from urls import url_patterns


class UrlResolver:
    def resolve(
        self, request: HttpRequest
    ) -> Optional[Callable[[HttpRequest], HttpResponse]]:
        for url_pattern in url_patterns:
            match = url_pattern.match(request.path)
            if match:
                request.params.update(match.groupdict())
                return url_pattern.view

        return None
