#!/usr/bin/env python3
"""
项目完整性验证脚本
"""
import os
import sys

def check_file_exists(filepath, description):
    """检查文件是否存在"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} (缺失)")
        return False

def check_directory_exists(dirpath, description):
    """检查目录是否存在"""
    if os.path.exists(dirpath) and os.path.isdir(dirpath):
        print(f"✅ {description}: {dirpath}")
        return True
    else:
        print(f"❌ {description}: {dirpath} (缺失)")
        return False

def main():
    print("🔍 智能视觉分析助手 - 项目完整性检查")
    print("=" * 60)
    
    all_good = True
    
    # 检查核心文件
    core_files = [
        ("app.py", "Flask主应用"),
        ("config.py", "配置文件"),
        ("requirements.txt", "依赖列表"),
        ("run.py", "启动脚本"),
        ("demo.py", "演示脚本"),
        ("install.py", "安装脚本"),
        ("test_system.py", "测试脚本"),
        ("README.md", "项目说明"),
        ("USAGE.md", "使用指南")
    ]
    
    print("\n📄 核心文件检查:")
    for filepath, description in core_files:
        if not check_file_exists(filepath, description):
            all_good = False
    
    # 检查模型模块
    model_files = [
        ("models/__init__.py", "模型模块初始化"),
        ("models/yolo_detector.py", "YOLO检测器"),
        ("models/qwen_client.py", "Qwen客户端")
    ]
    
    print("\n🤖 模型模块检查:")
    for filepath, description in model_files:
        if not check_file_exists(filepath, description):
            all_good = False
    
    # 检查工具模块
    util_files = [
        ("utils/__init__.py", "工具模块初始化"),
        ("utils/video_processor.py", "视频处理器"),
        ("utils/image_utils.py", "图像工具")
    ]
    
    print("\n🛠️ 工具模块检查:")
    for filepath, description in util_files:
        if not check_file_exists(filepath, description):
            all_good = False
    
    # 检查前端文件
    frontend_files = [
        ("templates/index.html", "主页模板"),
        ("static/css/style.css", "样式文件"),
        ("static/js/app.js", "前端脚本")
    ]
    
    print("\n🎨 前端文件检查:")
    for filepath, description in frontend_files:
        if not check_file_exists(filepath, description):
            all_good = False
    
    # 检查文档
    doc_files = [
        ("docs/API.md", "API文档"),
        ("docs/DEPLOYMENT.md", "部署文档")
    ]
    
    print("\n📚 文档检查:")
    for filepath, description in doc_files:
        if not check_file_exists(filepath, description):
            all_good = False
    
    # 检查目录结构
    directories = [
        ("static/captures", "截图目录"),
        ("static/images", "图片目录"),
        ("docs", "文档目录")
    ]
    
    print("\n📁 目录结构检查:")
    for dirpath, description in directories:
        if not check_directory_exists(dirpath, description):
            all_good = False
    
    # 检查Python语法
    print("\n🐍 Python语法检查:")
    python_files = [
        "app.py", "config.py", "run.py", "demo.py", "install.py", "test_system.py",
        "models/yolo_detector.py", "models/qwen_client.py",
        "utils/video_processor.py", "utils/image_utils.py"
    ]
    
    for filepath in python_files:
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    compile(f.read(), filepath, 'exec')
                print(f"✅ 语法检查通过: {filepath}")
            except SyntaxError as e:
                print(f"❌ 语法错误: {filepath} - {e}")
                all_good = False
            except Exception as e:
                print(f"⚠️  检查警告: {filepath} - {e}")
    
    print("\n" + "=" * 60)
    if all_good:
        print("🎉 项目完整性检查通过！")
        print("\n📋 下一步:")
        print("1. 运行安装脚本: python install.py")
        print("2. 配置API密钥: 编辑 config.py")
        print("3. 启动应用: python run.py")
        print("4. 或运行演示: python demo.py")
    else:
        print("❌ 项目存在问题，请检查缺失的文件")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())