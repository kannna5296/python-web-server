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
    return HttpResponse(body=body)

def show_request(request: HttpRequest) -> HttpResponse:
    context = {
        "now": datetime.now(),
        "method": request.method,
        "path": request.path,
        "http_version": request.http_version,
        "headers": pformat(request.headers),
        "body": request.body.decode("utf-8", "ignore")
        }
    body = render("show_request.html", context)
    return HttpResponse(body=body)


def parameters(request: HttpRequest) -> HttpResponse:
    """
    POSTパラメータを表示するHTMLを表示する
    """
    if request.method == "POST":
        context = {"parameters": pformat(parse_qs(request.body.decode()))}
        body = render("parameters.html", context)
        return HttpResponse(body=body)
    else:
        body = b"<html><body><h1>405 Method Not Allowed</h1></body></html>"
        return HttpResponse(body=body, status_code=405)


def user_profile(request: HttpRequest) -> HttpResponse:
    context = {"user_id": request.params["user_id"]}
    body = render("user_profile.html", context)
    return HttpResponse(body=body)
