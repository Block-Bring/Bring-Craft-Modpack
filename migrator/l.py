import os
from urllib.parse import urlparse
# 简化设置标题
def title(line_title: str):
    os.system(f'title {line_title}' if os.name == 'nt' else None)

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def pause():
    input("按 Enter 键继续...")

def stop():
    input("按 Enter 键结束")

def is_url(string):
    try:
        result = urlparse(string)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


if __name__ == "__main__":
    # 不进行任何操作
    title("Fast Execute")
