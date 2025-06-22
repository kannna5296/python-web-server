import os
import textwrap
import traceback
import re
from datetime import datetime, timezone
from socket import socket
from typing import Optional, Tuple
from mylog import log
from threading import Thread
from pprint import pformat


class WorkerThread(Thread):
    """
    WEBサーバが期待される挙動をするスレッドを定義
    """

    # 実行ファイルのあるディレクトリ
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # 静的配信するファイルを置くディレクトリ
    STATIC_ROOT = os.path.join(BASE_DIR, "static")

    # 拡張子とMIME Typeの対応
    MIME_TYPES = {
        "html": "text/html",
        "css": "text/css",
        "png": "image/png",
        "jpg": "image/jpg",
        "gif": "image/gif",
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
            request = self.client_socket.recv(4096)  # データを4096バイトずつ受け取る

            # クライアントから送られてきたデータをファイルに書き出す
            with open("server_recv.txt", "wb") as f:
                f.write(request)

            # リクエストパース
            method, path_string, http_version, request_header, request_body = (
                self.parse_http_request(request)
            )

            response_body: bytes
            content_type: Optional[str]
            response_line: str
            # pathが/nowのときは、現在時刻を表示するHTMLを生成する
            if path_string == "/now":
                html = f"""\
                    <html>
                    <body>
                        <h1>Now: {datetime.now()}</h1>
                    </body>
                    </html>
                """
                response_body = textwrap.dedent(html).encode()

                # Content-Typeを指定
                content_type = "text/html"

                # レスポンスラインを生成
                response_line = "HTTP/1.1 200 OK\r\n"

            # pathが/show_requestのときは、HTTPリクエストの内容を表示するHTMLを生成する
            elif path_string == "/show_request":
                html = f"""\
                    <html>
                    <body>
                        <h1>Request Line:</h1>
                        <p>
                            {method} {path_string} {http_version}
                        </p>
                        <h1>Headers:</h1>
                        <pre>{pformat(request_header)}</pre>
                        <h1>Body:</h1>
                        <pre>{request_body.decode("utf-8", "ignore")}</pre>
                        
                    </body>
                    </html>
                """
                response_body = textwrap.dedent(html).encode()

                # Content-Typeを指定
                content_type = "text/html"

                # レスポンスラインを生成
                response_line = "HTTP/1.1 200 OK\r\n"
            # pathがそれ以外のときは、静的ファイルからレスポンスを生成す
            else:
                try:
                    response_body = self.get_static_file_content(path_string)

                    # Content-Typeを指定
                    content_type = None

                    # レスポンスラインを生成
                    response_line = "HTTP/1.1 200 OK\r\n"

                except OSError:
                    # レスポンスを取得できなかった場合は、ログを出力して404を返す
                    traceback.print_exc()

                    response_body = b"<html><body><h1>404 Not Found</h1></body></html>"
                    content_type = "text/html"
                    response_line = "HTTP/1.1 404 Not Found\r\n"
            
            # レスポンスヘッダーを生成
            response_header = self.build_response_header(path_string, response_body, content_type)

            # レスポンス全体を生成する
            response = (response_line + response_header + "\r\n").encode() + response_body

            # ソケット通信はバイト単位でデータを送受信する必要がある
            # クライアントへレスポンスを送信する
            self.client_socket.send(response)

        except Exception:
            # リクエストの処理中に例外が発生した場合はコンソールにエラーログを出力し、
            # 処理を続行する
            log("リクエストの処理中にエラーが発生しました")
            traceback.print_exc()  # スタックトレース

        finally:
            # 例外が発生した場合も、発生しなかった場合も、TCP通信のcloseは行う
            log("クライアントとの通信を終了します remote_address: {}", self.client_address)
            self.client_socket.close()

    def parse_http_request(self, request: bytes) -> Tuple[str, str, str, dict, bytes]:
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

        return method, path, http_version, headers, request_body

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

        # pathの先頭の/を削除し、相対パスにしておく
        relative_path = path.lstrip("/")
        # デフォルトパス指定
        if not relative_path:
            relative_path = "index.html"
        # ファイルのpathを取得
        static_file_path = os.path.join(self.STATIC_ROOT, relative_path)

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
        
    def build_response_header(self, path_string: str, response_body: bytes, content_type: Optional[str]) -> str:
        """
        HTTPレスポンスヘッダーを生成する

        Args:
            path: リクエストパス（MIMEタイプの判定に使用）
            content_length: レスポンスボディの長さ

        Returns:
            str: 生成されたHTTPレスポンスヘッダー
        """
        if path_string in ("", "/", "/now", "/show_request"):
            ext = "html"
        else:
            ext = path_string.rsplit(".", maxsplit=1)[-1] if "." in path_string else ""
        content_type = self.MIME_TYPES.get(ext, "application/octet-stream")

        # レスポンスヘッダーを生成
        response_header = ""
        response_header += f"Date: {datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')}\r\n"
        response_header += "Host: HenaServer/0.1\r\n"
        response_header += f"Content-Length: {len(response_body)}\r\n"
        response_header += "Connection: Close\r\n"
        response_header += f"Content-Type: {content_type}\r\n"

        return response_header