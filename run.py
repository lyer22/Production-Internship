#!/usr/bin/env python3
"""
智能视觉分析助手启动脚本
"""
import os
import sys
import argparse
from app import app, socketio, initialize_components
from config import Config

def check_dependencies():
    """检查依赖包"""
    required_packages = [
        'flask', 'flask_socketio', 'cv2', 'ultralytics', 
        'numpy', 'PIL', 'dashscope'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            if package == 'cv2':
                import cv2
            elif package == 'PIL':
                from PIL import Image
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ 缺少以下依赖包:")
        for pkg in missing_packages:
            print(f"   - {pkg}")
        print("\n请运行以下命令安装依赖:")
        print("pip install -r requirements.txt")
        return False
    
    print("✅ 所有依赖包已安装")
    return True

def check_api_key():
    """检查API密钥配置"""
    if Config.DASHSCOPE_API_KEY == 'your-dashscope-api-key-here':
        print("⚠️  警告: 请在config.py中配置您的阿里云百炼API密钥")
        print("   或设置环境变量: DASHSCOPE_API_KEY")
        return False
    
    print("✅ API密钥已配置")
    return True

def create_directories():
    """创建必要的目录"""
    directories = [
        'static/captures',
        'static/images',
        'logs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("✅ 目录结构已创建")

def main():
    parser = argparse.ArgumentParser(description='智能视觉分析助手')
    parser.add_argument('--host', default=Config.HOST, help='服务器地址')
    parser.add_argument('--port', type=int, default=Config.PORT, help='端口号')
    parser.add_argument('--debug', action='store_true', help='调试模式')
    parser.add_argument('--skip-checks', action='store_true', help='跳过依赖检查')
    
    args = parser.parse_args()
    
    print("🚀 智能视觉分析助手启动中...")
    print("=" * 50)
    
    # 检查系统环境
    if not args.skip_checks:
        if not check_dependencies():
            sys.exit(1)
        
        if not check_api_key():
            print("   系统将以演示模式运行（AI功能受限）")
    
    # 创建目录
    create_directories()
    
    # 初始化组件
    try:
        initialize_components()
    except Exception as e:
        print(f"❌ 组件初始化失败: {e}")
        sys.exit(1)
    
    print("=" * 50)
    print(f"🌐 服务器地址: http://{args.host}:{args.port}")
    print("📱 支持功能:")
    print("   - 实时视频流处理")
    print("   - YOLO目标检测")
    print("   - AI智能问答")
    print("   - 场景分析")
    print("   - 安全监控")
    print("=" * 50)
    print("按 Ctrl+C 停止服务器")
    
    try:
        # 启动应用
        socketio.run(
            app,
            host=args.host,
            port=args.port,
            debug=args.debug,
            allow_unsafe_werkzeug=True
        )
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()