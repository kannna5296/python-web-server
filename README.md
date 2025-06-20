ちなみに、httpdというのはApacheのことです。製品名とプログラム名が違ってややこしいですが、そういうものです。

下記のように、何か1行でも表示されればApacheは起動しています。

```
$ ps -u root | grep httpd
    0 47333 ??         0:00.25 /usr/sbin/httpd -D FOREGROUND
```

## Pythonファイルオープンモードまとめ

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

### 例
```python
# テキストファイルに追記
with open("log.txt", "a") as f:
    f.write("新しい行\n")

# バイナリファイルに追記
with open("data.bin", "ab") as f:
    f.write(b"追加データ")
```

## ソケット通信の基礎まとめ

### ソケットとは？
- アプリケーションがネットワーク通信を行うための"窓口"となる仕組み。
- Pythonでは `socket.socket()` で作成し、TCP/UDPなどの通信プロトコルを利用できる。

### ネットワーク階層とソケットの位置づけ

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

### 主なソケットオプションの階層
| レベル（level）              | 意味・用途                           | 例・備考                       |
|-----------------------------|--------------------------------------|-------------------------------|
| `socket.SOL_SOCKET`         | ソケット全体のオプション             | `SO_REUSEADDR`, `SO_KEEPALIVE` など |
| `socket.IPPROTO_TCP`        | TCPプロトコル固有のオプション         | `TCP_NODELAY` など             |
| `socket.IPPROTO_IP`         | IPプロトコル固有のオプション          | `IP_TTL` など                  |
| `socket.IPPROTO_UDP`        | UDPプロトコル固有のオプション         | UDP用のオプション              |
| `socket.IPPROTO_IPV6`       | IPv6プロトコル固有のオプション        | IPv6用のオプション             |

### 例：アドレス再利用オプションの設定
```python
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
```
- `SOL_SOCKET` … ソケット全体のオプション
- `SO_REUSEADDR` … アドレス再利用
- `1` … 有効化

### 参考
- [Python公式: socket — 低レベルのネットワークインターフェース](https://docs.python.org/ja/3/library/socket.html)

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