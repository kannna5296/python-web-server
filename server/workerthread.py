import os
import traceback
from datetime import datetime, timezone
from socket import socket
from typing import Tuple
from utils import log

class WorkerThread:
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
        self.address = address

    def run(self) -> None:  # Javaでいうvoidみたいなこと
        try:
            request = self.client_socket.recv(4096)  # データを4096バイトずつ受け取る

            # クライアントから送られてきたデータをファイルに書き出す
            with open("server_recv.txt", "wb") as f:
                f.write(request)

            # リクエスト全体を
            # 1. リクエストライン(1行目)
            # 2. リクエストヘッダー(2行目〜空行)
            # 3. リクエストボディ(空行〜)にパースする
            request_line, remain = request.split(b"\r\n", maxsplit=1)
            request_header, request_body = remain.split(b"\r\n\r\n", maxsplit=1)

            method, path, http_version = request_line.decode().split(" ")

            log("path: " + path)
            relative_path = path.lstrip("/")
            log("relative_path: " + relative_path)

            # デフォルトパス指定
            if not relative_path:
                relative_path = "index.html"
            static_file_path = os.path.join(self.STATIC_ROOT, relative_path)
            log("static_file_path: " + static_file_path)

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

            if "." in path:
                ext = path.rsplit(".", maxsplit=1)[-1]
            else:
                ext = ""
            content_type = self.MIME_TYPES.get(ext, "application/octet-stream")

            # レスポンスヘッダーを生成
            response_header = ""
            response_header += f"Date: {datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')}\r\n"
            response_header += "Host: HenaServer/0.1\r\n"
            response_header += f"Content-Length: {len(response_body)}\r\n"
            response_header += "Connection: Close\r\n"
            response_header += f"Content-Type: {content_type}\r\n"

            # ヘッダーとボディを空行でくっつけた上でbytesに変換し、レスポンス全体を生成する
            response = (
                response_line + response_header + "\r\n"
            ).encode() + response_body

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
            self.client_socket.close()
