import os
import traceback
from datetime import datetime, timezone
from socket import socket
from typing import Tuple
from mylog import log
from threading import Thread


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
        super().__init__()

        self.client_socket = client_socket
        self.client_address = address

    def run(self) -> None:  # Javaでいうvoidみたいなこと
        try:
            request = self.client_socket.recv(4096)  # データを4096バイトずつ受け取る

            # クライアントから送られてきたデータをファイルに書き出す
            with open("server_recv.txt", "wb") as f:
                f.write(request)

            # リクエストパース
            method, path, http_version, request_header, request_body = (
                self.parse_request(request)
            )

            # 静的ファイルのパスを取得
            static_file_path = self.get_static_file(path)

            # レスポンスライン、ボディ生成
            response_line, response_body = self.create_response_body(static_file_path)

            # レスポンスヘッダ生成
            response_header = self.create_response_header(path, len(response_body))

            # ヘッダーとボディを空行でくっつけた上でbytesに変換し、レスポンス全体を生成する
            response = (
                response_line + response_header + "\r\n"
            ).encode() + response_body.encode()

            # ソケット通信はバイト単位でデータを送受信する必要がある
            # クライアントへレスポンスを送信する
            self.client_socket.send(response)

        except Exception:
            # リクエストの処理中に例外が発生した場合はコンソールにエラーログを出力し、
            # 処理を続行する
            print("=== リクエストの処理中にエラーが発生しました ===")
            traceback.print_exc()  # スタックトレース

        finally:
            # 例外が発生した場合も、発生しなかった場合も、TCP通信のcloseは行う
            print(f"=== Worker: クライアントとの通信を終了します remote_address: {self.client_address} ===")
            self.client_socket.close()

    def parse_request(self, request: bytes) -> Tuple[str, str, str, bytes, bytes]:
        request_line, remain = request.split(b"\r\n", maxsplit=1)
        request_header, request_body = remain.split(b"\r\n\r\n", maxsplit=1)
        method, path, http_version = request_line.decode().split(" ")

        return method, path, http_version, request_header, request_body

    def get_static_file(self, path) -> str:
        log("path: " + path)
        relative_path = path.lstrip("/")
        log("relative_path: " + relative_path)

        # デフォルトパス指定
        if not relative_path:
            relative_path = "index.html"
        static_file_path = os.path.join(self.STATIC_ROOT, relative_path)
        log("static_file_path: " + static_file_path)

        return static_file_path

    def create_response_body(self, static_file_path) -> Tuple[str, str]:
        try:
            # ファイルからレスポンスボディを生成　バイナリ、読み取り専用モード
            with open(static_file_path, "rb") as f:
                response_body = f.read()
            # レスポンスラインを生成
            response_line = "HTTP/1.1 200 OK\r\n"
        except OSError:
            log("ファイルが見つかりませんでした")
            # ファイルが見つからなかった場合は404を返す
            response_body = b"<html><body><h1>404 Not Found</h1></body></html>"
            response_line = "HTTP/1.1 404 Not Found\r\n"

        return response_line, response_body.decode()

    def create_response_header(self, path, content_length) -> str:
        if "." in path:
            ext = path.rsplit(".", maxsplit=1)[-1]
        else:
            # パスが空または拡張子がない場合はhtmlとして扱う
            ext = "html" if not path or path == "/" else ""
        content_type = self.MIME_TYPES.get(ext, "application/octet-stream")

        # レスポンスヘッダーを生成
        response_header = ""
        response_header += f"Date: {datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')}\r\n"
        response_header += "Host: HenaServer/0.1\r\n"
        response_header += f"Content-Length: {content_length}\r\n"
        response_header += "Connection: Close\r\n"
        response_header += f"Content-Type: {content_type}\r\n"

        return response_header
