import json
import os
import sys
import tkinter as tk
from tkinter import filedialog

import colorama
import requests

import l

colorama.init()

RED = colorama.Fore.RED
GREEN = colorama.Fore.GREEN
YELLOW = colorama.Fore.YELLOW
BLUE = colorama.Fore.BLUE
MAGENTA = colorama.Fore.MAGENTA
CYAN = colorama.Fore.CYAN
WHITE = colorama.Fore.WHITE
RST = colorama.Style.RESET_ALL

CONFIG_FILE = "config.json"
config = {}
LATEST_INFO_FILE = "latest.json"
latest = {}
dot_minecraft_folder = ""
modpack_version = ""
feature = ""

# 加载配置文件
def load_config() -> bool:
    global config
    print(f"{YELLOW}正在尝试读取配置文件...{RST}")
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf8') as f:
                config = json.load(f)
        except PermissionError:
            print(f"{RED}无法读取配置文件 {CONFIG_FILE}：权限不足。{RST}")
            print(f"{RED}请使用管理员身份运行或将程序放置于普通文件夹下运行。")
            print(f"请不要将程序放在 C:/Windows 或 C:/Users 目录下{RST}")
        except Exception as e:
            print(f"{RED}无法读取配置文件 {CONFIG_FILE}：{e}")
            print(f"{RED}请检查配置文件格式是否正确。{RST}")
    else:
        print(f"{RED}未找到配置文件{RST}")
        try:
            print(f"{YELLOW}正在尝试创建...{RST}")
            config_contents = {
                "minecraft_directory": ""
            }
            with open(CONFIG_FILE, 'w', encoding='utf8') as f:
                json.dump(config_contents, f, indent=4)
                print(f"{GREEN}成功创建配置文件{RST}")
        except Exception as e:
            print(f"{RED}创建配置文件 {CONFIG_FILE} 失败，原因：{e}")

        try:
            with open(CONFIG_FILE, 'r', encoding='utf8') as f:
                config = json.load(f)
        except Exception as e:
            print(f"{RED}无法读取配置文件：{e}")

    if config:
        print(f"{GREEN}成功加载配置文件{RST}")
        return True
    else:
        return False
# 联机获取信息
def load_latest_info_file() -> int:
    global latest
    def request_file() -> bool:
        url = "https://raw.githubusercontent.com/Block-Bring/Bring-Craft-Modpack/refs/heads/main/migrator/latest.json"
        request_headers = {
            'User-Agent': 'Bring-Migrator/1.9.2 (https://github.com/Block-Bring/Bring-Craft-Modpack)'
        }
        try:
            print(f"{YELLOW}正在尝试下载最新信息文件...{RST}")
            response = requests.get(url, headers=request_headers, timeout=10)
            if response.status_code == 200:
                with open(LATEST_INFO_FILE, 'wb') as file:
                    file.write(response.content)
                print(f"{GREEN}成功下载最新信息文件{RST}")
                return True
            else:
                print(f"{RED}下载最新信息文件失败，状态码：{response.status_code}{RST}")
                return False
        except TimeoutError:
            print(f"{RED}下载最新信息文件失败：连接超时（timeout=10）{RST}")
            return False
        except Exception as exception:
            print(f"在尝试下载最新信息文件时出错：{exception}")
            return False
    if request_file():
        if os.path.exists(LATEST_INFO_FILE):
            try:
                print(f"{YELLOW}正在尝试读取最新信息文件...{RST}")
                with open(LATEST_INFO_FILE, 'r', encoding='utf-8') as f:
                    latest = json.load(f)
            except Exception as e:
                print(f"{RED}无法读取最新信息文件：{e}")
                return 0
            print(f"{GREEN}成功加载最新信息文件{RST}")
            return 1
        else:
            print(f"{RED}最新信息文件不存在{RST}")
            return 0
    else:
        if os.path.exists(LATEST_INFO_FILE):
            try:
                print(f"{YELLOW}正在读取已有的最新信息文件...{RST}")
                with open(LATEST_INFO_FILE, 'r', encoding='utf-8') as f:
                    latest = json.load(f)
                print(f"{YELLOW}警告：读取的信息文件可能不是最新的，请仔细甄别！{RST}")
            except Exception as e:
                print(f"{RED}无法读取已有的最新信息文件：{e}")
                return 0
        print(f"{RED}无法下载最新信息文件{RST}")
        return 0

# 判断是否是有效的目录
def is_valid_minecraft_directory(directory: str) -> bool:
    # 如在
    if not os.path.exists(directory):
        return False
    # 是不是 .minecraft
    if os.path.basename(directory) != ".minecraft":
        return False
    # 有没有这些
    required_files = ["launcher_profiles.json"]
    required_dirs = ["versions", "libraries", "assets"]
    if not all(os.path.exists(os.path.join(directory, f)) for f in required_files):
        return False
    if not all(os.path.exists(os.path.join(directory, d)) for d in required_dirs):
        return False
    return True


def select_minecraft_directory(initialize):
    l.c()
    l.t("Bring Migrator - 目录选择")
    if initialize:
        print(f"{RED}Minecraft 目录无效{RST}")
    else:
        print("更改 Minecraft 目录")
    print(f"请选择你的 Minecraft 目录")

    def select():
        while True:  # ① 用循环代替递归
            print(f"{YELLOW}正在启动文件资源管理器 Dialog{RST}")
            root = tk.Tk()
            root.withdraw()
            select_operate = filedialog.askdirectory()
            directory = os.path.join(select_operate)
            root.destroy()

            # ② 处理用户取消（点了取消或关闭窗口）
            if not directory:
                print("已取消选择。")
                return False  # 保持与原退出逻辑一致

            if is_valid_minecraft_directory(directory):
                print(f"已选择目录：{directory}")
                return confirm_directory(directory)
            else:
                print(f"{RED}Minecraft 目录无效{RST}")
                print("请选择接下来的操作：")
                print("[1] 重新选择目录")
                print("[2] 退出程序")

                # ③ 防止空格、空输入，并循环直到输入正确
                while True:
                    choice = input("请输入你的选择：").strip()
                    if choice == "1":
                        break  # 跳出内层循环，外层 while True 自动重试
                    elif choice == "2":
                        return False
                    else:
                        print(f"{RED}无效的选择，请输入1或2{RST}")

    def confirm_directory(directory):
        config["minecraft_directory"] = directory
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as file:
                json.dump(config, file, indent=4)
            print(f"{GREEN}更改完成。请手动重新启动程序。{RST}")
        except Exception as exception:
            print(f"{RED}保存到配置文件 {CONFIG_FILE} 时出错：{exception}{RST}")
            return False
        return True

    return select()

def features(is_latest: bool) -> int:
    l.c()
    l.t("Bring Migrator - 操作选择")
    print(f"当前 Minecraft 目录：{GREEN}{dot_minecraft_folder}{RST}")
    if is_latest:
        print(f"Bring Craft 版本：{GREEN}{modpack_version}{RST}")
    else:
        print(f"Bring Craft 版本：{YELLOW}{modpack_version}（可能过期）{RST}")
    print(f"=========================================")
    print(f"           {YELLOW}选择需要执行的操作{RST}")
    print("")
    print(f"   [{GREEN}1{RST}] 迁移 Minecraft 个性化设置")
    print(f"   [{GREEN}2{RST}] 重新设置 .minecraft 文件夹")
    print(f"   [{GREEN}3{RST}] 退出")
    print("")
    print(f"=========================================")
    print("")

    OPERATION_MAP = {"1": 1, "2": 2, "3": 3}
    def operating():
        while True:
            operate = input("请输入操作序号：").strip()
            if operate in OPERATION_MAP:
                return OPERATION_MAP[operate]
            print(f"{RED}无效的操作序号{RST}")
    return operating()


def main() -> bool:
    global modpack_version, dot_minecraft_folder, feature
    # 设置窗口标题，使用了 l.py 缩写，名称的扩写为 line.title()
    l.t("Bring Migrator - 初始化")
    loading_config = load_config()
    loading_latest = load_latest_info_file()
    if loading_config and loading_latest in (1, 2):
        # 整合包版本定义
        modpack_version = latest["version"]
        if is_valid_minecraft_directory(config["minecraft_directory"]):
            # .minecraft 文件夹
            dot_minecraft_folder = os.path.join(config["minecraft_directory"])
            if loading_latest == 1:
                feature = features(True)
            elif loading_latest == 2:
                feature = features(False)
            else:
                return False
            if feature == 1:
                pass
            elif feature == 2:
                select_minecraft_directory(False)
            elif feature == 3:
                pass
        else:
            select_minecraft_directory(True)
    else:
        print(f"{RED}无法初始化程序{RST}")
        return False
    return True

if __name__ == "__main__":
    if main():
        l.t("Bring Migrator - 正常退出")
        print(f"{GREEN}程序正常退出{RST}")
        input("按 Enter 键结束")
        sys.exit(True)
    else:
        l.t("Bring Migrator - 异常退出")
        print(f"{RED}程序异常退出{RST}")
        input("按 Enter 键结束")
        sys.exit(False)
