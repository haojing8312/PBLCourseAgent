#!/usr/bin/env python3
"""
开发环境启动脚本
同时启动后端FastAPI和前端文件服务器
"""
import os
import subprocess
import sys
import time
import threading
import http.server
import socketserver
from pathlib import Path


def start_backend():
    """启动后端FastAPI服务"""
    print("🚀 启动后端服务...")
    os.chdir("backend")

    # 检查是否有.env文件
    if not os.path.exists(".env"):
        print("⚠️  警告：未找到.env文件，请配置OpenAI API密钥")
        print("请编辑 backend/.env 文件，设置：")
        print("OPENAI_API_KEY=your_openai_api_key_here")
        print("OPENAI_BASE_URL=your_base_url_here")
        print("")

    # 检查是否安装了uv
    try:
        subprocess.run(["uv", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ 错误：未找到uv，请先安装uv")
        print("安装命令：")
        print("Windows: powershell -ExecutionPolicy ByPass -c \"irm https://astral.sh/uv/install.ps1 | iex\"")
        print("macOS/Linux: curl -LsSf https://astral.sh/uv/install.sh | sh")
        return

    try:
        # 确保依赖已安装
        print("📦 检查并安装依赖...")
        subprocess.run(["uv", "sync"], check=True)

        # 启动服务
        print("🌟 启动FastAPI服务...")
        subprocess.run([
            "uv", "run", "uvicorn",
            "app.main:app",
            "--reload",
            "--host", "0.0.0.0",
            "--port", "48097"
        ], check=True)
    except KeyboardInterrupt:
        print("\n💤 后端服务已停止")
    except Exception as e:
        print(f"❌ 后端启动失败: {e}")
        print("请检查：")
        print("1. .env文件是否正确配置")
        print("2. 运行 'cd backend && uv sync' 安装依赖")
        print("3. Python版本是否为3.9+")


def start_frontend():
    """启动前端文件服务器"""
    print("🌐 启动前端服务...")
    time.sleep(2)  # 等待2秒让后端先启动

    frontend_dir = Path("frontend")
    os.chdir(frontend_dir)

    PORT = 3000

    class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            # 添加CORS头部
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            super().end_headers()

    try:
        with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
            print(f"✅ 前端服务运行在: http://localhost:{PORT}")
            print(f"✅ 后端API运行在: http://localhost:48097")
            print(f"📖 API文档: http://localhost:48097/docs")
            print(f"\n🎉 Project Genesis AI 开发环境已启动！")
            print(f"📝 打开浏览器访问: http://localhost:{PORT}")
            print(f"\n按 Ctrl+C 停止服务")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n💤 前端服务已停止")
    except Exception as e:
        print(f"❌ 前端启动失败: {e}")


def main():
    """主函数"""
    print("🚀 启动 Project Genesis AI 开发环境")
    print("=" * 50)

    # 检查当前目录
    if not os.path.exists("backend") or not os.path.exists("frontend"):
        print("❌ 错误：请在项目根目录运行此脚本")
        print("当前目录应包含 backend/ 和 frontend/ 文件夹")
        sys.exit(1)

    # 检查uv是否可用
    try:
        subprocess.run(["uv", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ 错误：未找到uv，请先安装uv")
        print("安装命令：")
        print("Windows: powershell -ExecutionPolicy ByPass -c \"irm https://astral.sh/uv/install.ps1 | iex\"")
        print("macOS/Linux: curl -LsSf https://astral.sh/uv/install.sh | sh")
        sys.exit(1)

    try:
        # 在新线程中启动前端
        frontend_thread = threading.Thread(target=start_frontend, daemon=True)
        frontend_thread.start()

        # 在主线程中启动后端（这样Ctrl+C能正确停止）
        start_backend()

    except KeyboardInterrupt:
        print("\n\n👋 感谢使用 Project Genesis AI！")
        print("🎓 让AI为教育赋能，让每一位教育者都能创造世界级课程！")


if __name__ == "__main__":
    main()