import os

# 简化设置标题
def title(line_title: str):
    os.system(f'title {line_title}' if os.name == 'nt' else None)

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    # 不进行任何操作
    title("Fast Execute")
