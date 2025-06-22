import os
import socket
import datetime
import traceback
from utils import log
from workerthread import WorkerThread


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

    # 拡張子とMIME Typeの対応
    MIME_TYPES = {
        "html": "text/html",
        "css": "text/css",
        "png": "image/png",
        "jpg": "image/jpg",
        "gif": "image/gif",
    }

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
                log("クライアントからの接続を待ちます")
                # 接続完了したsocketインスタンスと、クライアントのaddressがもらえる
                (client_socket, address) = server_socket.accept()
                log(
                    "クライアントからの接続が完了しました remote_address: {}",
                    address,
                )

                thread = WorkerThread(client_socket, address)
                thread.start()
        finally:
            log("サーバ停止しました")


if __name__ == "__main__":
    server = WebServer()
    server.serve()
