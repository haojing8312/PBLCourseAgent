#!/usr/bin/env python
"""
用户管理脚本

用法:
    python scripts/manage_users.py add <username> <password>  # 添加用户
    python scripts/manage_users.py list                       # 列出所有用户
    python scripts/manage_users.py remove <username>          # 删除用户
    python scripts/manage_users.py hash <password>            # 生成密码哈希
"""
import json
import os
import sys

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 用户配置文件路径
USERS_FILE = os.path.join(os.path.dirname(__file__), "../users.json")


def load_users() -> dict:
    """加载用户配置"""
    if not os.path.exists(USERS_FILE):
        return {"users": []}
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"加载用户配置失败: {e}")
        return {"users": []}


def save_users(data: dict):
    """保存用户配置"""
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"配置已保存到: {USERS_FILE}")


def add_user(username: str, password: str):
    """添加新用户"""
    data = load_users()

    # 检查用户是否已存在
    if any(u["username"] == username for u in data["users"]):
        print(f"错误: 用户 '{username}' 已存在")
        return False

    # 添加用户
    password_hash = pwd_context.hash(password)
    data["users"].append({
        "username": username,
        "password_hash": password_hash
    })

    save_users(data)
    print(f"用户 '{username}' 添加成功")
    return True


def list_users():
    """列出所有用户"""
    data = load_users()
    users = data.get("users", [])

    if not users:
        print("暂无用户")
        return

    print(f"共 {len(users)} 个用户:")
    for user in users:
        print(f"  - {user['username']}")


def remove_user(username: str):
    """删除用户"""
    data = load_users()

    original_count = len(data["users"])
    data["users"] = [u for u in data["users"] if u["username"] != username]

    if len(data["users"]) == original_count:
        print(f"错误: 用户 '{username}' 不存在")
        return False

    save_users(data)
    print(f"用户 '{username}' 已删除")
    return True


def hash_password(password: str):
    """生成密码哈希"""
    hashed = pwd_context.hash(password)
    print(f"密码哈希: {hashed}")
    return hashed


def print_usage():
    """打印用法说明"""
    print(__doc__)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    command = sys.argv[1]

    if command == "add":
        if len(sys.argv) != 4:
            print("用法: python manage_users.py add <username> <password>")
            sys.exit(1)
        add_user(sys.argv[2], sys.argv[3])

    elif command == "list":
        list_users()

    elif command == "remove":
        if len(sys.argv) != 3:
            print("用法: python manage_users.py remove <username>")
            sys.exit(1)
        remove_user(sys.argv[2])

    elif command == "hash":
        if len(sys.argv) != 3:
            print("用法: python manage_users.py hash <password>")
            sys.exit(1)
        hash_password(sys.argv[2])

    else:
        print(f"未知命令: {command}")
        print_usage()
        sys.exit(1)
