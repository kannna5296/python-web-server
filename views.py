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
        email = post_params["email"][0]

        return HttpResponse(
            status_code=302,
            headers={"Location": "/welcome"},
            cookies={"username": username, "email": email},
        )
    else:
        body = b"<html><body><h1>405 Method Not Allowed</h1></body></html>"
        return HttpResponse(body=body, status_code=405)


def welcome(request: HttpRequest) -> HttpResponse:
    if "username" not in request.cookies:
        return HttpResponse(status_code=302, headers={"Location": "/login"})

    # Welcome画面を表示
    username = request.cookies["username"]
    email = request.cookies["email"]
    body = render("welcome.html", context={"username": username, "email": email})

    return HttpResponse(body=body)
