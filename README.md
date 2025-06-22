## プロジェクト開始手順（コマンドまとめ）

1. リポジトリをクローン
```sh
git clone <リポジトリURL>
cd server-python
```

2. Python仮想環境の作成・有効化
```sh
python3 -m venv .venv
source .venv/bin/activate
```

3. 依存パッケージのインストール（requirements.txt）
```sh
pip install -r requirements.txt
```

4. コード自動整形の実行
```sh
black .
```

---

- 依存パッケージは requirements.txt で管理しています。
- 必要に応じてパッケージを追加してください。
- VSCode等のエディタ連携もおすすめです。

## 学び・気づきメモ

### HTTPサーバー関連
- ちなみに、httpdというのはApacheのことです。

### Pythonファイルオープンモードまとめ
| モード | 意味 | 例 | 備考 |
|--------|------|----|------|
| "r"  | 読み込み専用（テキスト） | open("file.txt", "r") | デフォルト。ファイルが無いとエラー |
| "w"  | 書き込み専用（テキスト） | open("file.txt", "w") | ファイルが無ければ新規作成、あれば上書き |
| "a"  | 追記（テキスト）         | open("file.txt", "a") | ファイルが無ければ新規作成、あれば末尾に追加 |
| "rb" | 読み込み専用（バイナリ） | open("file.bin", "rb")| バイナリファイル用（画像・音声など） |
| "wb" | 書き込み専用（バイナリ） | open("file.bin", "wb")| バイナリファイル用。上書き保存 |
| "ab" | 追記（バイナリ）         | open("file.bin", "ab")| バイナリファイル用。末尾に追加 |

- `b` が付くと「バイナリモード」→ バイト列（bytes型）で読み書きする場合に使う
- `a` は「append（追記）」の意味→ 既存ファイルの末尾にデータを追加したいときに使う

#### 例
```python
# テキストファイルに追記
with open("log.txt", "a") as f:
    f.write("新しい行\n")

# バイナリファイルに追記
with open("data.bin", "ab") as f:
    f.write(b"追加データ")
```

### ソケット通信の基礎まとめ

#### ソケットとは？
- アプリケーションがネットワーク通信を行うための"窓口"となる仕組み。
- Pythonでは `socket.socket()` で作成し、TCP/UDPなどの通信プロトコルを利用できる。

#### ネットワーク階層とソケットの位置づけ

```
アプリケーション
   ↑
ソケット（socket）
   ↑
トランスポート層（TCP/UDP）
   ↑
ネットワーク層（IP/IPv6）
   ↑
物理層・データリンク層
```
- ソケットはTCP/UDP/IPなど下位プロトコルをまとめて扱う"上位の概念"

#### 主なソケットオプションの階層
| レベル（level）              | 意味・用途                           | 例・備考                       |
|-----------------------------|--------------------------------------|-------------------------------|
| `socket.SOL_SOCKET`         | ソケット全体のオプション             | `SO_REUSEADDR`, `SO_KEEPALIVE` など |
| `socket.IPPROTO_TCP`        | TCPプロトコル固有のオプション         | `TCP_NODELAY` など             |
| `socket.IPPROTO_IP`         | IPプロトコル固有のオプション          | `IP_TTL` など                  |
| `socket.IPPROTO_UDP`        | UDPプロトコル固有のオプション         | UDP用のオプション              |
| `socket.IPPROTO_IPV6`       | IPv6プロトコル固有のオプション        | IPv6用のオプション             |

#### 例：アドレス再利用オプションの設定
```python
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
```
- `SOL_SOCKET` … ソケット全体のオプション
- `SO_REUSEADDR` … アドレス再利用
- `1` … 有効化

### ソケット通信とバイト列
- ソケット通信は**バイト単位**でデータを送受信する必要がある
- `client_socket.send()` には必ず**バイト列（bytes型）**を渡す必要がある
- 文字列（str）は直接送信できず、`encode()` でバイト列に変換してから送信する

### encode() と decode() の役割
- **encode()**: 文字列（str）→ バイト列（bytes）への変換
  - 例: `"Hello".encode()` → `b'Hello'`
  - ネットワーク送信時に必要
- **decode()**: バイト列（bytes）→ 文字列（str）への変換
  - 例: `b'Hello'.decode()` → `'Hello'`
  - ネットワーク受信時に必要

### ファイル操作とバイト列
- `"rb"` モード: バイト列（bytes）で読み込み
- `"wb"` モード: バイト列（bytes）で書き込み
- 画像・音声・ネットワークデータなどはバイト列で扱う

### 実装例
```python
# 送信時（文字列 → バイト列）
response = "HTTP/1.1 200 OK\r\n".encode()
client_socket.send(response)

# 受信時（バイト列 → 文字列）
request = client_socket.recv(4096)  # bytes型
method, path, http_version = request.decode().split(" ")  # str型に変換
```

### Pythonモジュール・ライブラリまとめ

#### re（正規表現）
- Pythonの正規表現を扱うためのモジュール
- 文字列のパターンマッチング、検索、置換などに使用
- 例: `re.split(r": *", header_row, maxsplit=1)` → `:` とその後の空白で文字列を分割

#### textwrap
- テキストの整形を行うモジュール
- `textwrap.dedent()` でインデントを削除

#### pprint
- データ構造を見やすく出力するモジュール
- `pformat()` で辞書やリストを整形して文字列として取得

#### traceback
- 例外の詳細情報（スタックトレース）を扱うモジュール
- `traceback.print_exc()` で現在の例外の詳細を出力

### application/x-www-form-urlencoded について
- Webフォームのデータ送信でよく使われるMIMEタイプ（Content-Type）
- キーと値のペアを「key1=value1&key2=value2」のような形式でエンコードして送信
- スペースは「+」、日本語などはURLエンコード（%E3%81%82 など）される
- POSTリクエストのボディや、GETリクエストのクエリパラメータで使われる
- Pythonでデコードするには `urllib.parse.parse_qs()` などが便利
- formタグでenctypeを指定しなかった場合こうなる

#### 例
```
name=Alice&message=Hello+World%21
```
- 上記は「name: Alice」「message: Hello World!」を表す

### multipart/form-data について
- ファイルアップロードや複数種類のデータ送信に使われるMIMEタイプ（Content-Type）
- フォームの`<input type="file">`でファイルを送信する場合は自動的にこの形式になる
- データは「パート（区切り）」ごとに分かれて送信され、各パートにヘッダーとボディがある
- テキストデータもファイルも同じリクエストで送れる
- 境界線（boundary）で各パートを区切る
- Pythonでパースするには `cgi.FieldStorage` や `requests` ライブラリ、`werkzeug` などが便利

#### 例（イメージ）
```
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="name"

Alice
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="file"; filename="hello.txt"
Content-Type: text/plain

Hello, world!
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```
- 上記は「name: Alice」と「file: hello.txt（内容: Hello, world!）」を同時に送信している例

### urllib について
- Python標準ライブラリの1つで、URLの操作やHTTP通信を行うためのモジュール群
- サブモジュールとして `urllib.request`（HTTPリクエスト送信）、`urllib.parse`（URLの分解・組み立て・エンコード/デコード）、`urllib.error`（エラー処理）、`urllib.robotparser`（robots.txt解析）などがある
- Web APIとの連携や、クエリパラメータのパース・生成、URLエンコード/デコードなどに便利

#### 主な使い方例
- `urllib.request.urlopen(url)` でHTTPリクエストを送信
- `urllib.parse.urlencode(dict)` で辞書をクエリ文字列に変換
- `urllib.parse.parse_qs(query)` でクエリ文字列を辞書に変換
- `urllib.parse.quote(string)` でURLエンコード、`unquote(string)` でデコード

#### 例
```python
from urllib.parse import urlencode, parse_qs, quote, unquote

params = {'name': 'Alice', 'message': 'Hello World!'}
query = urlencode(params)  # 'name=Alice&message=Hello+World%21'
parsed = parse_qs(query)   # {'name': ['Alice'], 'message': ['Hello World!']}
encoded = quote('こんにちは')  # '%E3%81%93%E3%82%93%E3%81%AB%E3%81%A1%E3%81%AF'
decoded = unquote(encoded) # 'こんにちは'
```

