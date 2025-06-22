import os
import inspect

def log(msg, *args):
    """
    見やすくログを出すメソッド。プレースホルダ対応。
    """
    PRE_SUFFIX = "=="
    # 呼び出し元のファイル名を取得
    caller_file = os.path.basename(inspect.stack()[1].filename)
    formatted = msg.format(*args)
    print(f"[{caller_file}] {PRE_SUFFIX} {formatted} {PRE_SUFFIX}")
