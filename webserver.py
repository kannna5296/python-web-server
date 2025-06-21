import os
import socket
import datetime
import traceback
from utils import log


# ソケット通信(=トランスポート層)
# TCP/IPで言うと
#   TCP/UDPを使うところ
#   インターネット層(IP)の一個上
#   アプリケーション層(HTTP,SNTPとか)の一個下
class WebServer:
    """
    WEBサーバを表す
    """

    # 実行ファイルのあるディレクトリ
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # 静的配信するファイルを置くディレクトリ
    STATIC_ROOT = os.path.join(BASE_DIR, "static")

    def serve(self):
        log("サーバ起動します")
        try:
            server_socket = socket.socket()

            # 1引数...どのレイヤのものか？ SOL_SOCKETだとソケット自体に関するオプション
            # 2個目...付け足したいオプション
            # 3個目...true or false
            # socket.SO_REUSEADDR: 待ち状態中のポートが存在してもbindする
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            server_socket.bind(("localhost", 8080))
            server_socket.listen(10)  # 10は同時接続数みたいなもん

            while True:
                try:
                    log("クライアントからの接続を待ちます")
                    # 接続完了したsocketインスタンスと、クライアントのaddressがもらえる
                    (client_socket, address) = server_socket.accept()
                    log(
                        "クライアントからの接続が完了しました remote_address: {}",
                        address,
                    )

                    request = client_socket.recv(4096)  # データを4096バイトずつ受け取る

                    # クライアントから送られてきたデータをファイルに書き出す
                    with open("server_recv.txt", "wb") as f:
                        f.write(request)

                    # リクエスト全体を
                    # 1. リクエストライン(1行目)
                    # 2. リクエストヘッダー(2行目〜空行)
                    # 3. リクエストボディ(空行〜)
                    # にパースする
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
                        response_body = (
                            b"<html><body><h1>404 Not Found</h1></body></html>"
                        )
                        response_line = "HTTP/1.1 404 Not Found\r\n"

                    # レスポンスヘッダーを生成
                    response_header = ""
                    response_header += f"Date: {datetime.datetime.now(datetime.timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')}\r\n"
                    response_header += "Host: HenaServer/0.1\r\n"
                    response_header += f"Content-Length: {len(response_body)}\r\n"
                    response_header += "Connection: Close\r\n"
                    response_header += "Content-Type: text/html\r\n"

                    # ヘッダーとボディを空行でくっつけた上でbytesに変換し、レスポンス全体を生成する
                    response = (
                        response_line + response_header + "\r\n"
                    ).encode() + response_body

                    # ソケット通信はバイト単位でデータを送受信する必要がある
                    # クライアントへレスポンスを送信する
                    client_socket.send(response)

                except Exception:
                    # リクエストの処理中に例外が発生した場合はコンソールにエラーログを出力し、
                    # 処理を続行する
                    print("=== リクエストの処理中にエラーが発生しました ===")
                    traceback.print_exc() #スタックトレース

                finally:
                    # 例外が発生した場合も、発生しなかった場合も、TCP通信のcloseは行う
                    client_socket.close()
        finally:
            log("サーバ停止しました")


if __name__ == "__main__":
    server = WebServer()
    server.serve()
