import os
import traceback

import settings
from henango.http.request import HttpRequest
from henango.http.response import HttpResponse


def static(request: HttpRequest) -> HttpResponse:

    try:
        default_static_root = os.path.join(os.path.dirname(__file__), "../../static")
        static_root = getattr(settings, "STATIC_ROOT", default_static_root)

        # pathの先頭の/を削除し、相対パスにしておく
        relative_path = request.path.lstrip("/")
        # デフォルトパス指定
        if not relative_path:
            relative_path = "index.html"
        # ファイルのpathを取得
        static_file_path = os.path.join(static_root, relative_path)

        with open(static_file_path, "rb") as f:
            response_body = f.read()

        content_type = None
        return HttpResponse(
            body=response_body, content_type=content_type, status_code=200
        )

    except OSError:
        # レスポンスを取得できなかった場合は、ログを出力して404を返す
        traceback.print_exc()

        response_body = b"<html><body><h1>404 Not Found</h1></body></html>"
        content_type = "text/html;"
        return HttpResponse(
            body=response_body, content_type=content_type, status_code=200
        )
