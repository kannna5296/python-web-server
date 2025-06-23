import textwrap
from datetime import datetime
from pprint import pformat
from urllib.parse import parse_qs

from henango.http.request import HttpRequest
from henango.http.response import HttpResponse
from templates.renderer import render


def now(request: HttpRequest) -> HttpResponse:

    context = {"now": datetime.now()}
    body = render("now.html", context)
    content_type = "text/html, charset=UTF-8"

    return HttpResponse(body=body, content_type=content_type, status_code=200)


def show_request(request: HttpRequest) -> HttpResponse:
    html = f"""\
        <html>
        <body>
            <h1>Request Line:</h1>
            <p>
                {request.method} {request.path} {request.http_version}
            </p>
            <h1>Headers:</h1>
            <pre>{pformat(request.headers)}</pre>
            <h1>Body:</h1>
            <pre>{request.body.decode("utf-8", "ignore")}</pre>
            
        </body>
        </html>
    """
    body = textwrap.dedent(html).encode()

    # Content-Typeを指定
    content_type = "text/html, charset=UTF-8"

    return HttpResponse(body=body, content_type=content_type, status_code=200)


def parameters(request: HttpRequest) -> HttpResponse:
    """
    POSTパラメータを表示するHTMLを表示する
    """

    # GETリクエストの場合は、405を返す
    if request.method == "GET":
        body = b"<html><body><h1>405 Method Not Allowed</h1></body></html>"
        content_type = "text/html; charset=UTF-8"
        status_code = 405

    elif request.method == "POST":
        post_params = parse_qs(request.body.decode())
        html = f"""\
            <html>
            <body>
                <h1>Parameters:</h1>
                <pre>{pformat(post_params)}</pre>                        
            </body>
            </html>
        """
        body = textwrap.dedent(html).encode()
        content_type = "text/html; charset=UTF-8"
        status_code = 200

    return HttpResponse(body=body, content_type=content_type, status_code=status_code)


def user_profile(request: HttpRequest) -> HttpResponse:
    user_id = request.params["user_id"]
    html = f"""\
        <html>
        <body>
            <h1>プロフィール</h1>
            <p>ID: {user_id}
        </body>
        </html>
    """
    body = textwrap.dedent(html).encode()
    content_type = "text/html; charset=UTF-8"
    status_code = 200

    return HttpResponse(body=body, content_type=content_type, status_code=status_code)
