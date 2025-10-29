# 使用指南

## 📚 目录
1. [快速开始](#快速开始)
2. [功能使用](#功能使用)
3. [配置优化](#配置优化)
4. [常见问题](#常见问题)
5. [高级功能](#高级功能)

## 快速开始

### 1. 环境准备
```bash
# 检查Python版本（需要3.8+）
python --version

# 安装依赖
pip install -r requirements.txt

# 系统诊断
python diagnose.py
```

### 2. 配置API密钥
编辑 `config.py` 文件：
```python
# 阿里云百炼API配置
DASHSCOPE_API_KEY = 'sk-your-actual-api-key-here'
```

获取API密钥：
1. 访问 [阿里云百炼平台](https://dashscope.aliyun.com/)
2. 注册/登录账号
3. 创建API密钥
4. 复制密钥到config.py

### 3. 启动应用
```bash
# 方式1: 使用启动脚本（推荐）
python start_app.py
# 选择模式1（完整功能）

# 方式2: 直接启动
python app.py

# 方式3: 演示模式（无需API密钥）
python demo.py
```

### 4. 访问界面
- **本地访问**: http://localhost:5000
- **局域网访问**: http://你的IP:5000
- **推荐浏览器**: Chrome, Edge, Firefox

## 功能使用

### 🎥 视频流控制

#### 启动摄像头
1. 点击界面顶部的 **"启动"** 按钮
2. 等待摄像头初始化（约1-2秒）
3. 视频流开始显示，YOLO自动检测物体
4. 观察右侧统计信息：
   - 检测对象数量
   - 实时帧率（FPS）
   - 摄像头状态

#### 停止摄像头
1. 点击 **"停止"** 按钮
2. 视频流停止，资源释放
3. 可以随时重新启动

#### 性能监控
- **帧率显示**: 实时FPS，正常应在15-20之间
- **对象计数**: 当前画面检测到的物体数量
- **检测结果**: 底部显示所有检测到的物体和置信度

### AI智能问答
1. 在右侧问答区域输入问题
2. 点击发送按钮或按Enter键
3. AI会基于当前视频内容回答问题
4. 可以使用预设问题快速询问

### 场景分析
1. 点击"分析"按钮进行场景分析
2. 系统会提供场景描述和安全评估
3. 分析结果包括检测摘要和安全等级

### 截图功能
1. 点击"截图"按钮捕获当前画面
2. 截图会显示在弹窗中
3. 可以下载保存截图

## 常见问题

### Q: 摄像头无法启动
A: 
- 检查摄像头是否被其他程序占用
- 确认摄像头权限设置
- 尝试更改config.py中的CAMERA_INDEX值

### Q: AI回答错误或无响应
A: 
- 检查API密钥是否正确配置
- 确认网络连接正常
- 查看控制台错误信息

### Q: 检测效果不佳
A: 
- 调整config.py中的CONFIDENCE_THRESHOLD值
- 确保光线充足
- 检查摄像头清晰度

### Q: 系统运行缓慢
A: 
- 降低视频分辨率和帧率
- 关闭其他占用资源的程序
- 考虑使用更强的硬件

## 高级配置

### 修改检测参数
编辑 `config.py`:
```python
# 置信度阈值（0-1）
CONFIDENCE_THRESHOLD = 0.5

# IoU阈值（0-1）  
IOU_THRESHOLD = 0.45

# 视频参数
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FPS = 30
```

### 自定义系统提示词
修改 `config.py` 中的 `SYSTEM_PROMPT`:
```python
SYSTEM_PROMPT = """你是一个专业的视觉分析助手..."""
```

### 更换YOLO模型
```python
# 在config.py中修改
YOLO_MODEL_PATH = 'yolov8s.pt'  # 使用更大的模型获得更好效果
```

## 开发和扩展

### 添加新功能
1. 在相应模块中添加功能代码
2. 更新API路由（如需要）
3. 修改前端界面
4. 添加测试用例

### 自定义检测类别
修改 `config.py` 中的 `COCO_CLASSES` 列表，或训练自定义YOLO模型。

### 集成其他AI模型
参考 `models/qwen_client.py` 的实现方式，创建新的AI客户端。

## 性能优化建议

1. **硬件优化**
   - 使用GPU加速（需要CUDA支持）
   - 增加内存容量
   - 使用SSD存储

2. **软件优化**
   - 调整视频参数
   - 使用模型量化
   - 启用多线程处理

3. **网络优化**
   - 使用本地部署减少延迟
   - 优化图像压缩
   - 启用缓存机制

## 故障排除

### 查看日志
```bash
# 查看应用日志
tail -f logs/app.log

# 启用调试模式
python run.py --debug
```

### 系统检查
```bash
# 运行系统检查
python test_system.py --check

# 运行完整测试
python test_system.py --all
```

### 重置配置
```bash
# 恢复默认配置
cp config_template.py config.py
```

## 技术支持

如遇到问题，请：
1. 查看本文档的常见问题部分
2. 运行系统检查脚本
3. 查看应用日志文件
4. 提供详细的错误信息和系统环境