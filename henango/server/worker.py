import os
import traceback
import re

from datetime import datetime, timezone
from socket import socket
from typing import Optional, Tuple
from henango.http.request import HttpRequest
from henango.http.response import HttpResponse
from mylog import log
from threading import Thread
from settings import STATIC_ROOT
import settings
from urls import URL_VIEW


class Worker(Thread):
    """
    WEBサーバが期待される挙動をするスレッドを定義
    """

    # 拡張子とMIME Typeの対応
    MIME_TYPES = {
        "html": "text/html; charset=UTF-8",
        "css": "text/css",
        "png": "image/png",
        "jpg": "image/jpg",
        "gif": "image/gif",
    }

    # ステータスコードとステータスラインの対応
    STATUS_LINES = {
        200: "200 OK",
        404: "404 Not Found",
        405: "405 Method Not Allowed",
    }

    def __init__(self, client_socket: socket, address: Tuple[str, int]):
        """
        ワーカースレッドを初期化する

        Args:
            client_socket: クライアントとの通信を行うソケット
            address: クライアントのアドレス情報 (IP, ポート)
        """
        super().__init__()

        self.client_socket = client_socket
        self.client_address = address

    def run(self) -> None:
        """
        ワーカースレッドのメイン処理を実行する

        クライアントからのリクエストを受信し、適切なレスポンスを返す。
        例外が発生した場合でもクライアントとの接続は確実にクローズする。
        """
        try:
            request_bytes = self.client_socket.recv(
                4096
            )  # データを4096バイトずつ受け取る

            # クライアントから送られてきたデータをファイルに書き出す
            with open("server_recv.txt", "wb") as f:
                f.write(request_bytes)

            # HTTPリクエストをパースする
            request = self.parse_http_request(request_bytes)

            # for-elseとやらがあるPython
            for url_pattern, view in URL_VIEW.items():
                match = self.url_match(url_pattern, request.path)
                # マッチするやつがあればviewパッケージからレスポンス生成
                if match:
                    request.params.update(match.groupdict())
                    response = view(request)
                    break
            # マッチするやつない場合は静的ファイルを探す
            else:
                try:
                    response_body = self.get_static_file_content(request.path)
                    content_type = None
                    response = HttpResponse(
                        body=response_body, content_type=content_type, status_code=200
                    )
                # それでもない場合は404
                except OSError:
                    # レスポンスを取得できなかった場合は、ログを出力して404を返す
                    traceback.print_exc()

                    response_body = b"<html><body><h1>404 Not Found</h1></body></html>"
                    content_type = "text/html;"
                    response = HttpResponse(
                        body=response_body, content_type=content_type, status_code=404
                    )

            # レスポンスラインを生成
            response_line = self.build_response_line(response)

            # レスポンスヘッダーを生成
            response_header = self.build_response_header(response, request)

            # レスポンス全体を生成する
            response_bytes = (
                response_line + response_header + "\r\n"
            ).encode() + response.body

            # ソケット通信はバイト単位でデータを送受信する必要がある
            # クライアントへレスポンスを送信する
            self.client_socket.send(response_bytes)

        except Exception:
            # リクエストの処理中に例外が発生した場合はコンソールにエラーログを出力し、
            # 処理を続行する
            log("リクエストの処理中にエラーが発生しました")
            traceback.print_exc()  # スタックトレース

        finally:
            # 例外が発生した場合も、発生しなかった場合も、TCP通信のcloseは行う
            log(
                "クライアントとの通信を終了します remote_address: {}",
                self.client_address,
            )
            self.client_socket.close()

    def parse_http_request(self, request: bytes) -> HttpRequest:
        """
        HTTPリクエストをパースして各要素を抽出する

        Args:
            request: クライアントから受信したHTTPリクエスト（バイト列）

        Returns:
            Tuple[str, str, str, dict, bytes]:
            (HTTPメソッド, パス, HTTPバージョン, リクエストヘッダー, リクエストボディ)
        """

        request_line, remain = request.split(b"\r\n", maxsplit=1)
        request_header, request_body = remain.split(b"\r\n\r\n", maxsplit=1)

        # リクエストラインを文字列に変換してパースする
        method, path, http_version = request_line.decode().split(" ")

        # リクエストヘッダーを辞書にパースする
        headers = {}
        for header_row in request_header.decode().split("\r\n"):
            key, value = re.split(r": *", header_row, maxsplit=1)
            headers[key] = value

        return HttpRequest(
            method=method,
            path=path,
            http_version=http_version,
            headers=headers,
            body=request_body,
        )

    def get_static_file_content(self, path: str) -> bytes:
        """
        リクエストパスから静的ファイルの絶対パスを取得する

        Args:
            path: リクエストのパス（例: "/index.html", "/css/style.css"）

        Returns:
            str: 静的ファイルの絶対パス
        """
        """
        リクエストpathから、staticファイルの内容を取得する
        """
        default_static_root = os.path.join(os.path.dirname(__file__), "../../static")
        static_root = getattr(settings, "STATIC_ROOT", default_static_root)

        # pathの先頭の/を削除し、相対パスにしておく
        relative_path = path.lstrip("/")
        # デフォルトパス指定
        if not relative_path:
            relative_path = "index.html"
        # ファイルのpathを取得
        static_file_path = os.path.join(static_root, relative_path)

        with open(static_file_path, "rb") as f:
            return f.read()

    def create_response_body(self, path_string: str) -> Tuple[str, str]:
        """
        静的ファイルからレスポンスボディを生成する

        Args:
            static_file_path: 静的ファイルの絶対パス

        Returns:
            Tuple[str, str]: (HTTPステータスライン, レスポンスボディ)
            ファイルが見つからない場合は404エラーページを返す
        """
        try:
            # ファイルからレスポンスボディを生成　バイナリ、読み取り専用モード
            with open(path_string, "rb") as f:
                response_body = f.read()
            # レスポンスラインを生成
            response_line = "HTTP/1.1 200 OK\r\n"
        except OSError:
            log("ファイルが見つかりませんでした")
            # ファイルが見つからなかった場合は404を返す
            response_body = b"<html><body><h1>404 Not Found</h1></body></html>"
            response_line = "HTTP/1.1 404 Not Found\r\n"

        return response_line, response_body.decode()

    def build_response_line(self, response: HttpResponse) -> str:
        """
        レスポンスラインを構築する
        """
        status_line = self.STATUS_LINES[response.status_code]
        return f"HTTP/1.1 {status_line}"

    def build_response_header(
        self, response: HttpResponse, request: HttpRequest
    ) -> str:
        """
        HTTPレスポンスヘッダーを生成する

        Args:
            path: リクエストパス（MIMEタイプの判定に使用）
            content_length: レスポンスボディの長さ

        Returns:
            str: 生成されたHTTPレスポンスヘッダー
        """
        # Content-Typeが指定されていない場合はpathから特定する
        if response.content_type is None:
            # pathから拡張子を取得
            if "." in request.path:
                ext = request.path.rsplit(".", maxsplit=1)[-1]
            else:
                ext = ""
            # 拡張子からMIME Typeを取得
            # 知らない対応していない拡張子の場合はoctet-streamとする
            response.content_type = self.MIME_TYPES.get(ext, "application/octet-stream")

        # レスポンスヘッダーを生成
        response_header = ""
        response_header += f"Date: {datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')}\r\n"
        response_header += "Host: HenaServer/0.1\r\n"
        response_header += f"Content-Length: {len(response.body)}\r\n"
        response_header += "Connection: Close\r\n"
        response_header += f"Content-Type: {response.content_type}\r\n"

        return response_header

    def url_match(self, url_pattern: str, path: str) -> Optional[re.Match]:
        # URLパターンを正規表現パターンに変換する
        # ex) '/user/<user_id>/profile' => '/user/(?P<user_id>[^/]+)/profile'
        re_pattern = re.sub(r"<(.+?)>", r"(?P<\1>[^/]+)", url_pattern)
        return re.match(re_pattern, path)
