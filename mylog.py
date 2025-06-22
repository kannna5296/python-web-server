import os

def log(msg, *args):
    """
    見やすくログを出すメソッド。プレースホルダ対応。
    """
    PRE_SUFFIX = "=="
    # 実行中のファイル名を取得
    current_file = os.path.basename(__file__)
    formatted = msg.format(*args)
    print(f"[{current_file}] {PRE_SUFFIX} {formatted} {PRE_SUFFIX}")
