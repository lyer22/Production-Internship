"""
配置文件 - 智能视觉分析助手
"""
import os

class Config:
    # Flask配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'smart-vision-assistant-2024'
    DEBUG = True
    HOST = '127.0.0.1'
    PORT = 5000
    
    # 阿里云百炼API配置
    DASHSCOPE_API_KEY = os.environ.get('DASHSCOPE_API_KEY') or 'sk-585c0caca85045f3b0dfa14b004bba5e'
    QWEN_MODEL = 'qwen-vl-plus'
    
    # YOLO模型配置
    YOLO_MODEL_PATH = 'yolov8n.pt'  # 将自动下载
    CONFIDENCE_THRESHOLD = 0.5
    IOU_THRESHOLD = 0.45
    
    # 视频处理配置
    CAMERA_INDEX = 0  # 默认摄像头
    FRAME_WIDTH = 1280  # 提升到720p
    FRAME_HEIGHT = 720
    FPS = 30
    
    # 视频流优化配置
    STREAM_FPS = 20  # 流传输帧率（可以低于摄像头FPS以节省带宽）
    STREAM_QUALITY = 85  # JPEG质量 (1-100)，提高质量
    MAX_FRAME_WIDTH = 1280  # 最大传输宽度
    MAX_FRAME_HEIGHT = 720  # 最大传输高度
    
    # 检测类别 (COCO数据集)
    COCO_CLASSES = [
        'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck',
        'boat', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench',
        'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra',
        'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
        'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove',
        'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup',
        'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange',
        'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
        'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse',
        'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink',
        'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier',
        'toothbrush'
    ]
    
    # 系统提示词
    SYSTEM_PROMPT = """你是一个智能视觉分析助手，能够理解图像内容并回答相关问题。
    你的任务是：
    1. 分析用户提供的图像内容
    2. 识别图像中的物体、人物、场景等
    3. 回答用户关于图像的问题
    4. 提供有用的观察和建议
    
    请用简洁、准确的中文回答用户的问题。"""