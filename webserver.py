from operator import add
import socket
import datetime
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

                        # レスポンスボディを生成
            response_body = "<html><body><h1>It works!</h1></body></html>"

            # レスポンスラインを生成
            response_line = "HTTP/1.1 200 OK\r\n"
            # レスポンスヘッダーを生成
            response_header = ""
            response_header += f"Date: {datetime.datetime.now(datetime.timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')}\r\n"
            response_header += "Host: HenaServer/0.1\r\n"
            response_header += f"Content-Length: {len(response_body.encode())}\r\n"
            response_header += "Connection: Close\r\n"
            response_header += "Content-Type: text/html\r\n"

            # ヘッダーとボディを空行でくっつけた上でbytesに変換し、レスポンス全体を生成する
            response = (response_line + response_header + "\r\n" + response_body).encode()

            # クライアントへレスポンスを送信する
            client_socket.send(response)

            # 通信を終了させる
            client_socket.close()
        finally:
            log("サーバ停止しました")


if __name__ == "__main__":
    server = TCPServer()
    server.serve()