#!/usr/bin/env python3
"""
智能视觉分析助手安装脚本
"""
import os
import sys
import subprocess
import platform

def run_command(command, description):
    """运行命令并显示进度"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✅ {description}完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description}失败: {e.stderr}")
        return False

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ 需要Python 3.8或更高版本")
        print(f"   当前版本: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}")
    return True

def install_dependencies():
    """安装依赖包"""
    print("🔧 开始安装依赖包...")
    
    # 升级pip
    if not run_command(f"{sys.executable} -m pip install --upgrade pip", "升级pip"):
        return False
    
    # 安装基础依赖
    basic_deps = [
        "flask==2.3.3",
        "flask-socketio==5.3.6",
        "numpy==1.24.3",
        "pillow==10.0.1",
        "requests==2.31.0",
        "python-socketio==5.9.0",
        "eventlet==0.33.3"
    ]
    
    for dep in basic_deps:
        if not run_command(f"{sys.executable} -m pip install {dep}", f"安装 {dep.split('==')[0]}"):
            return False
    
    # 安装OpenCV
    opencv_cmd = f"{sys.executable} -m pip install opencv-python==4.8.1.78"
    if not run_command(opencv_cmd, "安装 OpenCV"):
        return False
    
    # 安装YOLO
    yolo_cmd = f"{sys.executable} -m pip install ultralytics==8.0.196"
    if not run_command(yolo_cmd, "安装 YOLO"):
        return False
    
    # 安装阿里云SDK
    dashscope_cmd = f"{sys.executable} -m pip install dashscope==1.14.1"
    if not run_command(dashscope_cmd, "安装 DashScope SDK"):
        return False
    
    return True

def setup_directories():
    """创建项目目录"""
    directories = [
        "static/css",
        "static/js", 
        "static/images",
        "static/captures",
        "templates",
        "models",
        "utils",
        "logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("✅ 项目目录结构已创建")

def download_yolo_model():
    """下载YOLO模型"""
    print("🤖 准备YOLO模型...")
    try:
        from ultralytics import YOLO
        model = YOLO('yolov8n.pt')  # 这会自动下载模型
        print("✅ YOLO模型准备完成")
        return True
    except Exception as e:
        print(f"⚠️  YOLO模型下载可能需要在首次运行时进行: {e}")
        return True  # 不阻止安装继续

def create_config_template():
    """创建配置文件模板"""
    config_content = '''"""
配置文件模板 - 请根据实际情况修改
"""
import os

class Config:
    # Flask配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    DEBUG = True
    HOST = '0.0.0.0'
    PORT = 5000
    
    # 阿里云百炼API配置 - 请替换为您的API密钥
    DASHSCOPE_API_KEY = os.environ.get('DASHSCOPE_API_KEY') or 'your-dashscope-api-key-here'
    QWEN_MODEL = 'qwen-vl-plus'
    
    # YOLO模型配置
    YOLO_MODEL_PATH = 'yolov8n.pt'
    CONFIDENCE_THRESHOLD = 0.5
    IOU_THRESHOLD = 0.45
    
    # 视频处理配置
    CAMERA_INDEX = 0
    FRAME_WIDTH = 640
    FRAME_HEIGHT = 480
    FPS = 30
'''
    
    if not os.path.exists('config.py'):
        with open('config_template.py', 'w', encoding='utf-8') as f:
            f.write(config_content)
        print("✅ 配置文件模板已创建 (config_template.py)")
        print("   请复制为 config.py 并填入您的API密钥")

def main():
    print("🚀 智能视觉分析助手安装程序")
    print("=" * 50)
    
    # 检查Python版本
    if not check_python_version():
        sys.exit(1)
    
    # 显示系统信息
    print(f"💻 操作系统: {platform.system()} {platform.release()}")
    print(f"🏗️  架构: {platform.machine()}")
    
    # 创建目录结构
    setup_directories()
    
    # 安装依赖
    if not install_dependencies():
        print("❌ 依赖安装失败，请检查网络连接和权限")
        sys.exit(1)
    
    # 下载YOLO模型
    download_yolo_model()
    
    # 创建配置模板
    create_config_template()
    
    print("=" * 50)
    print("🎉 安装完成!")
    print("\n📋 下一步:")
    print("1. 配置API密钥:")
    print("   - 复制 config_template.py 为 config.py")
    print("   - 在 config.py 中填入您的阿里云百炼API密钥")
    print("2. 运行应用:")
    print("   python run.py")
    print("3. 访问:")
    print("   http://localhost:5000")
    print("\n📚 更多信息请查看 README.md")

if __name__ == '__main__':
    main()