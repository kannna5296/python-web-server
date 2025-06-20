from operator import add
import socket
from typing import Required
from utils import log


# ソケット通信(=トランスポート層)
# TCP/IPで言うと
#   TCP/UDPを使うところ
#   インターネット層(IP)の一個上
#   アプリケーション層(HTTP,SNTPとか)の一個下
class TCPServer:
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

            log("クライアントからの接続を待ちます")
            # 接続完了したsocketインスタンスと、クライアントのaddressがもらえる
            (client_socket, address) = server_socket.accept()
            log("クライアントからの接続が完了しました remote_address: {}", address)

            request = client_socket.recv(4096)  # データを4096バイトずつ受け取る

            # クライアントから送られてきたデータをファイルに書き出す
            with open("server_recv.txt", "wb") as f:
                f.write(request)

            # クライアントへ送信するレスポンスデータをファイルから取得する
            with open("server_send.txt", "rb") as f:
                response = f.read()

            # クライアントへレスポンスを送信する
            client_socket.send(response)

            # 通信を終了させる
            client_socket.close()
        finally:
            log("サーバ停止しました")


if __name__ == "__main__":
    server = TCPServer()
    server.serve()