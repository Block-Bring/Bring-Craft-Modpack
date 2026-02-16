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
new_version = ""
old_version = ""

# 加载配置文件
def load_config() -> bool:
    global config
    print(f"{YELLOW}正在尝试读取配置文件...{RST}")
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
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
            with open(CONFIG_FILE, 'w', encoding='utf-8') as file:
                json.dump(config_contents, file, indent=4) # type: ignore
                print(f"{GREEN}成功创建配置文件{RST}")
        except Exception as e:
            print(f"{RED}创建配置文件 {CONFIG_FILE} 失败，原因：{e}")

        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as file:
                config = json.load(file)
        except Exception as e:
            print(f"{RED}无法读取配置文件：{e}")

    if config:
        print(f"{GREEN}成功加载配置文件{RST}")
        return True
    else:
        return False
# 联机获取信息
def load_latest_info_file() -> int:
    def request_file() -> bool:
        url = "https://raw.githubusercontent.com/Block-Bring/Bring-Craft-Modpack/refs/heads/main/migrator/latest.json"
        request_headers = {
            'User-Agent': 'Bring-Migrator/1.10 (https://github.com/Block-Bring/Bring-Craft-Modpack)'
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
    def read_latest_file(is_latest):
        global latest
        if os.path.exists(LATEST_INFO_FILE):
            try:
                if is_latest:
                    print(f"{YELLOW}正在尝试读取最新信息文件...{RST}")
                else:
                    print(f"{YELLOW}正在尝试读取已有的最新信息文件...{RST}")
                with open(LATEST_INFO_FILE, 'r', encoding='utf-8') as file:
                    latest = json.load(file)
                if is_latest:
                    print(f"{GREEN}成功加载最新信息文件{RST}")
                    return 1
                else:
                    print(f"{GREEN}成功加载已有的最新信息文件{RST}")
                    return 2
            except Exception as exception:
                print(f"{RED}无法读取最新信息文件：{exception}")
                return 0
        else:
            print(f"{RED}最新信息文件不存在{RST}")
            return 0

    if request_file():
        return read_latest_file(True)
    else:
        return read_latest_file(False)

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
    l.clear()
    l.title("Bring Migrator - 目录选择")

    print(f"{RED}Minecraft 目录无效{RST}" if initialize else f"{GREEN}选择 Minecraft 目录{RST}")
    print(f"请选择你的 Minecraft 目录")

    def select():
        while True:  # ① 用循环代替递归
            print(f"{YELLOW}正在启动文件资源管理器 Dialog{RST}")
            root = tk.Tk()
            root.withdraw()
            select_operate = filedialog.askdirectory()
            selected_directory = select_operate
            directory = os.path.normpath(selected_directory)
            root.destroy()

            # ② 处理用户取消（点了取消或关闭窗口）
            if not selected_directory:
                print("已取消选择。")
                return "back" if not initialize else False  # 保持与原退出逻辑一致

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
                json.dump(config, file, indent=4) # type: ignore
            print(f"{GREEN}更改完成。请手动重新启动程序。{RST}")
        except Exception as exception:
            print(f"{RED}保存到配置文件 {CONFIG_FILE} 时出错：{exception}{RST}")
            return False
        return True

    return select()

def choose_version():
    global old_version, new_version
    """
    选择原 Minecraft 版本与新 Minecraft 版本，并筛选有 mods 文件夹的版本。
    """
    l.title("Bring Migrator - 配置迁移")
    versions_dir = os.path.normpath(os.path.join(dot_minecraft_folder, "versions"))
    if not os.path.exists(versions_dir):
        print(f"{RED}未找到 versions 文件夹{RST}")
        return None, None

    # 获取所有版本文件夹
    version_folders = [
        item for item in os.listdir(versions_dir)
        if os.path.isdir(os.path.join(versions_dir, item))
    ]

    # 筛选包含 mods 文件夹的版本
    # 此处第一个 version 省略了 valid_versions.append(version) 的操作
    # 第二个 version 是 for 循环的一个临时变量，循环取出 version_folders 列表中的元素赋给 version
    # 下面那行就是 for 循环中，如果本次循环中的 version 满足条件，则将 version 添加到 valid_versions 列表中
    # 循环结束后，valid_versions 列表中就会有所有满足条件的版本
    # ^^^^ 布灵的学习笔记 ^^^^
    valid_versions = [
        version for version in version_folders
        if os.path.exists(os.path.join(versions_dir, version, "mods"))
    ]

    if not valid_versions:
        print(f"{RED}未找到包含 mods 文件夹的版本{RST}")
        return None, None

    # 此处 Python 自动拆分了元组，第一个值自动对应了 enumerate 的 0 索引，第二个值对应了 enumerate 的 1 索引
    # ^^^^  布灵的学习笔记 ^^^^
    print(f"=========================================")
    print(f"      {YELLOW}迁移 Minecraft 个性化设置{RST}")
    print("")
    print(f"  [{YELLOW}0{RST}] 返回")
    for i, version in enumerate(valid_versions, start=1):
        print(f"  [{GREEN}{i}{RST}] {version}")
    max_int = len(valid_versions)
    print(f"  [{RED}{max_int+1}{RST}] 退出")
    print("")
    print(f"=========================================")

    def select_version(message, old_version_int, is_new_version):
        while True:
            try:
                choice = int(input(message).strip())
                if 1 <= choice <= max_int:
                    if not is_new_version:
                        return choice
                    else:
                        if choice == old_version_int:
                            print(f"{RED}请选择与旧版本实例不同的版本实例{RST}")
                        else:
                            return choice
                elif choice == max_int+1:
                    return "exit"
                elif choice == 0:
                    return "back"
                else:
                    print(f"{RED}无效的选择，请输入 1-{max_int}{RST}")
            except ValueError:
                print(f"{RED}无效的选择，请输入数字{RST}")

    old_version_choice = select_version("请选择旧版本实例：", None, False)
    if old_version_choice == "exit":
        return "exit"
    elif old_version_choice == "back":
        return "back"
    else:
        old_version_name = valid_versions[old_version_choice-1]
    old_version = os.path.join(versions_dir, old_version_name)
    new_version_choice = select_version("请选择新版本实例：", old_version_choice, True)
    if new_version_choice == "exit":
        return "exit"
    elif new_version_choice == "back":
        return "back"
    else:
        new_version_name = valid_versions[new_version_choice-1]
    new_version = os.path.join(versions_dir, new_version_name)
    print(f"已选的旧 Minecraft 实例：{GREEN}{old_version_name}{RST}\n已选的新 Minecraft 实例：{GREEN}{new_version_name}{RST}\n")

def migrate():
    l.clear()
    choose_ver = choose_version()
    if choose_ver == "exit":
        pass
    elif choose_ver == "back":
        return "back"
    elif choose_ver:
        pass
    return True

def features(latest_is_latest: bool) -> int:
    l. clear()
    l. title("Bring Migrator - 操作选择")
    print(f"当前 Minecraft 目录：{GREEN}{dot_minecraft_folder}{RST}")
    if latest_is_latest:
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
    l.title("Bring Migrator - 初始化")
    loading_config = load_config()
    loading_latest = load_latest_info_file()

    if loading_config and loading_latest in (1, 2):
        # 整合包版本定义
        modpack_version = latest["version"]
        if is_valid_minecraft_directory(config["minecraft_directory"]):
            # .minecraft 文件夹
            dot_minecraft_folder = os.path.join(config["minecraft_directory"])

            LOADING_LATEST_MAP = {1: True, 2: False}
            FEATURES_MAP = {1: lambda: migrate(), 2: lambda: select_minecraft_directory(False), 3: lambda: True}
            while True:
                if loading_latest in LOADING_LATEST_MAP:
                    feature = features(LOADING_LATEST_MAP[loading_latest])
                else:
                    return False
                if feature in FEATURES_MAP:
                    action = FEATURES_MAP[feature]
                    result = action()
                    if result == "back":
                        pass
                    else:
                        return result
        else:
            return select_minecraft_directory(True)
    else:
        print(f"{RED}无法初始化程序{RST}")
        return False

if __name__ == "__main__":
    if main():
        l.title("Bring Migrator - 正常退出")
        print(f"{GREEN}程序正常退出{RST}")
        input("按 Enter 键结束")
        sys.exit(True)
    else:
        l.title("Bring Migrator - 异常退出")
        print(f"{RED}程序异常退出{RST}")
        input("按 Enter 键结束")
        sys.exit(False)
