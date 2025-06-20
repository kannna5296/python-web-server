import socket
from utils import log

class TCPClient:
    """
    TCP通信を行うクライアント
    """
    def request(self):
        log("サーバ起動します")

        try: 
            client_socket = socket.socket()
            client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            log("サーバと接続します")
            client_socket.connect(("127.0.0.1", 80))
            log("サーバとの接続が完了しました")

            # サーバにリクエストする内容をファイルから取る
            with open("client_send.txt", "rb") as f:
                request = f.read()

            client_socket.send(request)

            response = client_socket.recv(4096)

            # サーバから来たレスポンスをファイルに書き込む
            with open("client_recv.txt", "wb") as f:
                f.write(response)

        finally:
            client_socket.close()
            log("クライアントを停止します。")

if __name__ == '__main__':
    client = TCPClient()
    client.request()