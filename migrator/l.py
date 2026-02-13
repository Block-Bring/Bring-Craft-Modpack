import os

# 简化设置标题
def title(line_title: str):
    os.system(f"title {line_title}")

# 简化清除命令行
def clear():
    if os.name == 'nt':
        os.system('cls')
    elif os.name == 'posix':
        os.system('clear')

if __name__ == "__main__":
    # 不进行任何操作
    title("Fast Execute")
