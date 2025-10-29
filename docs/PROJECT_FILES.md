# 项目文件说明

## 📋 文件清单

### 📄 核心应用文件

#### 主程序
- **app.py** (400+ 行)
  - Flask主应用和路由定义
  - WebSocket事件处理
  - 视频流greenthread管理
  - eventlet异步架构

#### 配置文件
- **config.py** (80+ 行)
  - API密钥配置
  - 视频参数设置（720p@20fps）
  - YOLO检测参数
  - 系统提示词

#### 依赖管理
- **requirements.txt**
  - Flask 2.3.3
  - Flask-SocketIO 5.3.6
  - OpenCV 4.8+
  - Ultralytics YOLOv8
  - DashScope SDK
  - eventlet 0.33+

### 启动脚本
- **start_app.py** - 智能启动脚本，提供多种启动模式
- **run.py** - 简单启动脚本
- **demo.py** - 演示模式（无需摄像头和API）

### 工具脚本
- **install.py** - 自动安装脚本
- **diagnose.py** - 系统诊断工具
- **test_system.py** - 系统测试套件
- **verify_project.py** - 项目完整性验证

## 📂 目录结构

### models/ - AI模型模块
- **yolo_detector.py** - YOLO目标检测器
- **qwen_client.py** - 阿里云Qwen API客户端

### utils/ - 工具函数
- **video_processor.py** - 视频流处理
- **image_utils.py** - 图像处理工具

### templates/ - HTML模板
- **index.html** - 主页面

### static/ - 静态资源
- **css/style.css** - 样式文件
- **js/app.js** - 前端JavaScript
- **captures/** - 截图保存目录
- **images/** - 图片资源

### docs/ - 文档
- **API.md** - API文档
- **DEPLOYMENT.md** - 部署指南

## 📄 文档文件
- **README.md** - 项目说明
- **USAGE.md** - 使用指南
- **.gitignore** - Git忽略文件

## 🗑️ 可删除的文件
以下文件是开发过程中的测试文件，可以安全删除：
- test_*.py
- *_test.py
- *.jpg (测试图片)
- __pycache__/ (Python缓存)

## 📦 自动生成的文件
- **yolov8n.pt** - YOLO模型文件（首次运行时自动下载）
- **logs/** - 日志目录
- **__pycache__/** - Python缓存目录