from operator import add
import socket
from typing import Required



def log(msg, *args):
  PRE_SUFFIX = "=="
  formatted = msg.format(*args)
  print(f"{PRE_SUFFIX} {formatted} {PRE_SUFFIX}")

class TCPServer:
  def serve(self):

    log("サーバ起動します")
    try:
      server_socket = socket.socket()
      server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

      server_socket.bind(("localhost", 8080))
      server_socket.listen(10)

      log("クライアントからの接続を待ちます")
      (client_socket, address) = server_socket.accept()
      log("クライアントからの接続が完了しました remote_address: {}", address)

      request = client_socket.recv(4096)

      # ログ追記
      with open("server_recv.txt", "wb") as f:
        f.write(request)

      # 返事は特にせずに通信終了
      client_socket.close()
    finally:
      log("サーバ停止しました")

if __name__ == "__main__":
  server = TCPServer()
  server.serve()