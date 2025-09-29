#!/usr/bin/env python3
"""
快速启动脚本 - 使用uv环境管理
适用于已配置好uv和.env的开发环境
"""
import os
import subprocess
import sys
import time
import threading
import http.server
import socketserver
from pathlib import Path


def start_backend_uv():
    """使用uv启动后端服务"""
    print("🚀 启动后端服务 (uv)...")
    os.chdir("backend")

    try:
        # 直接使用uv运行，假设依赖已安装
        subprocess.run([
            "uv", "run", "uvicorn",
            "app.main:app",
            "--reload",
            "--host", "0.0.0.0",
            "--port", "8000"
        ], check=True)
    except KeyboardInterrupt:
        print("\n💤 后端服务已停止")
    except Exception as e:
        print(f"❌ 后端启动失败: {e}")
        print("请先运行: cd backend && uv sync")


def start_frontend():
    """启动前端文件服务器"""
    print("🌐 启动前端服务...")
    time.sleep(2)  # 等待后端启动

    frontend_dir = Path("frontend")
    os.chdir(frontend_dir)

    PORT = 3000

    class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            super().end_headers()

    try:
        with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
            print(f"✅ 前端服务: http://localhost:{PORT}")
            print(f"✅ 后端API: http://localhost:8000")
            print(f"📖 API文档: http://localhost:8000/docs")
            print(f"\n🎉 Project Genesis AI 就绪！")
            print(f"🎯 快速测试: curl http://localhost:8000/health")
            print(f"\n按 Ctrl+C 停止服务")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n💤 前端服务已停止")
    except Exception as e:
        print(f"❌ 前端启动失败: {e}")


def main():
    """主函数"""
    print("⚡ Project Genesis AI - 快速启动")
    print("=" * 40)

    # 检查目录
    if not os.path.exists("backend/pyproject.toml"):
        print("❌ 错误：请在项目根目录运行，且确保已设置uv环境")
        print("运行: cd backend && uv sync")
        sys.exit(1)

    try:
        # 启动前端（后台）
        frontend_thread = threading.Thread(target=start_frontend, daemon=True)
        frontend_thread.start()

        # 启动后端（主线程）
        start_backend_uv()

    except KeyboardInterrupt:
        print("\n\n👋 项目已停止")


if __name__ == "__main__":
    main()