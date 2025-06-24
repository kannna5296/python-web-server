import textwrap
from datetime import datetime
from pprint import pformat
from urllib.parse import parse_qs
from multipart import MultipartParser
import io
import re
import json

from henango.http.cookie import Cookie
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
        # 追加課題: multipart/form-dataの送信を可視化してみる
        # 実務でどう使うかは謎
        content_type = request.headers.get("Content-Type", "")
        if content_type.startswith("multipart/form-data"):
            # boundary抽出
            boundary_match = re.search(r"boundary=(.+)", content_type)
            if not boundary_match:
                context = {"parameters": "boundary not found", "files": ""}
            else:
                boundary = boundary_match.group(1)
                stream = io.BytesIO(request.body)
                params = {}
                files = {}
                for part in MultipartParser(stream, boundary):
                    if part is None:
                        continue
                    if getattr(part, "filename", None):
                        raw_preview = getattr(part, "raw", b"")[:100]
                        try:
                            preview_str = raw_preview.decode("utf-8")
                        except Exception:
                            preview_str = repr(raw_preview)
                        files[getattr(part, "name", "")] = {
                            "filename": getattr(part, "filename", ""),
                            "content_type": dict(getattr(part, "headerlist", [])).get(
                                "Content-Type", ""
                            ),
                            "size": getattr(part, "size", 0),
                            "preview": preview_str,
                        }
                    else:
                        params[getattr(part, "name", "")] = getattr(part, "value", "")
                context = {
                    "parameters": pformat(params),
                    "files": json.dumps(files, ensure_ascii=False, indent=2),
                }
        else:
            context = {
                "parameters": pformat(parse_qs(request.body.decode())),
                "files": "",
            }
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

        cookies = [
            Cookie(name="username", value=username, max_age=30),
            Cookie(name="email", value=email, max_age=30),
        ]

        return HttpResponse(
            status_code=302, headers={"Location": "/welcome"}, cookies=cookies
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
