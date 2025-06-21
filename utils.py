def log(msg, *args):
    """
    見やすくログを出すメソッド。プレースホルダ対応。
    """
    PRE_SUFFIX = "=="
    formatted = msg.format(*args)
    print(f"{PRE_SUFFIX} {formatted} {PRE_SUFFIX}")
