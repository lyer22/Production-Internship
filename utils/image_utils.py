"""
图像处理工具函数
"""
import cv2
import numpy as np
import base64
from PIL import Image
import io

def resize_image(image, max_width=800, max_height=600):
    """
    调整图像大小，保持宽高比
    
    Args:
        image: OpenCV图像
        max_width: 最大宽度
        max_height: 最大高度
        
    Returns:
        numpy.ndarray: 调整后的图像
    """
    h, w = image.shape[:2]
    
    # 计算缩放比例
    scale_w = max_width / w
    scale_h = max_height / h
    scale = min(scale_w, scale_h, 1.0)  # 不放大图像
    
    if scale < 1.0:
        new_w = int(w * scale)
        new_h = int(h * scale)
        return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
    
    return image

def enhance_image(image, brightness=0, contrast=1.0, saturation=1.0):
    """
    增强图像质量
    
    Args:
        image: OpenCV图像
        brightness: 亮度调整 (-100 到 100)
        contrast: 对比度调整 (0.5 到 3.0)
        saturation: 饱和度调整 (0.0 到 2.0)
        
    Returns:
        numpy.ndarray: 增强后的图像
    """
    # 亮度调整
    if brightness != 0:
        image = cv2.convertScaleAbs(image, alpha=1, beta=brightness)
    
    # 对比度调整
    if contrast != 1.0:
        image = cv2.convertScaleAbs(image, alpha=contrast, beta=0)
    
    # 饱和度调整
    if saturation != 1.0:
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        hsv[:, :, 1] = cv2.multiply(hsv[:, :, 1], saturation)
        image = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    
    return image

def add_timestamp(image, timestamp_str=None):
    """
    在图像上添加时间戳
    
    Args:
        image: OpenCV图像
        timestamp_str: 时间戳字符串，如果为None则使用当前时间
        
    Returns:
        numpy.ndarray: 添加时间戳的图像
    """
    if timestamp_str is None:
        from datetime import datetime
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 复制图像以避免修改原图
    img_with_timestamp = image.copy()
    
    # 设置字体和位置
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.6
    color = (255, 255, 255)  # 白色
    thickness = 2
    
    # 获取文本大小
    text_size = cv2.getTextSize(timestamp_str, font, font_scale, thickness)[0]
    
    # 在右下角添加黑色背景
    h, w = img_with_timestamp.shape[:2]
    x = w - text_size[0] - 10
    y = h - 10
    
    cv2.rectangle(img_with_timestamp, (x - 5, y - text_size[1] - 5), 
                  (w, h), (0, 0, 0), -1)
    
    # 添加时间戳文本
    cv2.putText(img_with_timestamp, timestamp_str, (x, y - 5), 
                font, font_scale, color, thickness)
    
    return img_with_timestamp

def image_to_base64(image, format='JPEG', quality=90):
    """
    将OpenCV图像转换为base64字符串
    
    Args:
        image: OpenCV图像
        format: 图像格式 ('JPEG', 'PNG')
        quality: JPEG质量 (1-100)
        
    Returns:
        str: base64编码的图像字符串
    """
    try:
        # 转换BGR到RGB
        if len(image.shape) == 3:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            image_rgb = image
        
        # 转换为PIL图像
        pil_image = Image.fromarray(image_rgb)
        
        # 保存到字节流
        buffer = io.BytesIO()
        if format.upper() == 'JPEG':
            pil_image.save(buffer, format='JPEG', quality=quality)
        else:
            pil_image.save(buffer, format=format)
        
        # 编码为base64
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return f"data:image/{format.lower()};base64,{image_base64}"
        
    except Exception as e:
        print(f"图像转base64失败: {e}")
        return None
        return None