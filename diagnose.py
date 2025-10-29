#!/usr/bin/env python3
"""
系统诊断脚本
"""
import sys

print("🔍 系统诊断开始...")
print("=" * 60)

# 检查Python版本
print(f"Python版本: {sys.version}")

# 检查关键依赖
dependencies = [
    'flask',
    'flask_socketio',
    'socketio',
    'eventlet',
    'cv2',
    'ultralytics',
    'dashscope'
]

print("\n📦 依赖包检查:")
for dep in dependencies:
    try:
        if dep == 'cv2':
            import cv2
            print(f"✅ OpenCV: {cv2.__version__}")
        elif dep == 'flask_socketio':
            import flask_socketio
            try:
                version = flask_socketio.__version__
            except AttributeError:
                version = "已安装（版本未知）"
            print(f"✅ Flask-SocketIO: {version}")
        elif dep == 'socketio':
            import socketio
            try:
                version = socketio.__version__
            except AttributeError:
                version = "已安装（版本未知）"
            print(f"✅ python-socketio: {version}")
        else:
            module = __import__(dep)
            version = getattr(module, '__version__', '未知')
            print(f"✅ {dep}: {version}")
    except ImportError as e:
        print(f"❌ {dep}: 未安装")

# 检查端口
print("\n🔌 端口检查:")
import socket
def check_port(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0

port = 5000
if check_port(port):
    print(f"⚠️  端口 {port} 已被占用")
else:
    print(f"✅ 端口 {port} 可用")

# 测试Flask-SocketIO
print("\n🧪 测试Flask-SocketIO:")
try:
    from flask import Flask
    from flask_socketio import SocketIO
    
    test_app = Flask(__name__)
    test_socketio = SocketIO(test_app, cors_allowed_origins="*")
    
    print("✅ Flask-SocketIO初始化成功")
    
    @test_socketio.on('connect')
    def test_connect():
        print("测试连接成功")
    
    print("✅ 事件处理器注册成功")
    
except Exception as e:
    print(f"❌ Flask-SocketIO测试失败: {e}")

print("\n" + "=" * 60)
print("诊断完成")
print("\n💡 建议:")
print("1. 如果有依赖未安装，运行: pip install -r requirements.txt")
print("2. 如果端口被占用，修改config.py中的PORT值")
print("3. 如果Flask-SocketIO有问题，尝试: pip install --upgrade flask-socketio")