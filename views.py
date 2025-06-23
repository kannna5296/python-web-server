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
        "body": request.body.decode("utf-8", "ignore"),
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


def set_cookie(request: HttpRequest) -> HttpResponse:
    return HttpResponse(headers={"Set-Cookie": "username=TARO"})


def login(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        body = render("login.html", {})
        return HttpResponse(body=body)

    elif request.method == "POST":
        post_params = parse_qs(request.body.decode())
        username = post_params["username"][0]

        headers = {"Location": "/welcome", "Set-Cookie": f"username={username}"}
        return HttpResponse(status_code=302, headers=headers)
    else:
        body = b"<html><body><h1>405 Method Not Allowed</h1></body></html>"
        return HttpResponse(body=body, status_code=405)


def welcome(request: HttpRequest) -> HttpResponse:
    cookie_header = request.headers.get("Cookie", None)

    if not cookie_header:
        return HttpResponse(status_code=302, headers={"Location": "/login"})

    cookie_strings = cookie_header.split("; ")
    cookies = {}
    for cookie_string in cookie_strings:
        name, value = cookie_string.split("=", maxsplit=1)
        cookies[name] = value

    if "username" not in cookies:
        return HttpResponse(status_code=302, headers={"Location": "/login"})

    # Welcome画面を表示
    body = render("welcome.html", context={"username": cookies["username"]})

    return HttpResponse(body=body)
