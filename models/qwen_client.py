"""
阿里云百炼Qwen3-VL-Plus客户端
"""
import dashscope
import base64
import json
from config import Config
from io import BytesIO
import cv2
import numpy as np

class QwenVLClient:
    def __init__(self):
        """初始化Qwen客户端"""
        dashscope.api_key = Config.DASHSCOPE_API_KEY
        self.model = Config.QWEN_MODEL
        
    def encode_image(self, image):
        """
        将OpenCV图像编码为base64字符串
        
        Args:
            image: OpenCV图像 (numpy array)
            
        Returns:
            str: base64编码的图像字符串
        """
        try:
            # 将图像编码为JPEG格式
            _, buffer = cv2.imencode('.jpg', image)
            # 转换为base64
            image_base64 = base64.b64encode(buffer).decode('utf-8')
            return f"data:image/jpeg;base64,{image_base64}"
        except Exception as e:
            print(f"图像编码失败: {e}")
            return None
    
    def analyze_image(self, image, question="请描述这张图片的内容", detection_info=None):
        """
        分析图像并回答问题
        
        Args:
            image: OpenCV图像
            question: 用户问题
            detection_info: YOLO检测信息
            
        Returns:
            str: AI回答
        """
        try:
            # 编码图像
            image_base64 = self.encode_image(image)
            if not image_base64:
                return "图像处理失败，无法分析"
            
            # 构建提示词
            prompt = self._build_prompt(question, detection_info)
            
            # 调用API
            messages = [
                {
                    "role": "system",
                    "content": Config.SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": [
                        {"text": prompt},
                        {"image": image_base64}
                    ]
                }
            ]
            
            response = dashscope.MultiModalConversation.call(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            if response.status_code == 200:
                raw_content = response.output.choices[0].message.content
                # 解析并提取文本内容
                return self._extract_text_from_response(raw_content)
            else:
                return f"API调用失败: {response.message}"
                
        except Exception as e:
            print(f"图像分析失败: {e}")
            return f"分析过程中出现错误: {str(e)}"
    
    def _extract_text_from_response(self, content):
        """
        从API响应中提取纯文本
        
        Args:
            content: API返回的内容（可能是字符串或JSON数组）
            
        Returns:
            str: 提取的纯文本
        """
        try:
            # 如果已经是字符串，直接返回
            if isinstance(content, str):
                # 尝试解析JSON
                try:
                    import json
                    parsed = json.loads(content)
                    if isinstance(parsed, list) and len(parsed) > 0:
                        # 提取第一个元素的text字段
                        if isinstance(parsed[0], dict) and 'text' in parsed[0]:
                            return parsed[0]['text']
                    return content
                except (json.JSONDecodeError, KeyError, IndexError):
                    # 不是JSON格式，直接返回原字符串
                    return content
            
            # 如果是列表
            elif isinstance(content, list) and len(content) > 0:
                if isinstance(content[0], dict) and 'text' in content[0]:
                    return content[0]['text']
                return str(content[0])
            
            # 如果是字典
            elif isinstance(content, dict):
                if 'text' in content:
                    return content['text']
                return str(content)
            
            # 其他情况，转换为字符串
            return str(content)
            
        except Exception as e:
            print(f"提取文本失败: {e}")
            return str(content)
    
    def _build_prompt(self, question, detection_info):
        """
        构建包含检测信息的提示词
        
        Args:
            question: 用户问题
            detection_info: 检测信息
            
        Returns:
            str: 完整提示词
        """
        prompt = f"用户问题: {question}\n\n"
        
        if detection_info and detection_info.get("objects"):
            prompt += "目标检测结果:\n"
            for i, obj in enumerate(detection_info["objects"], 1):
                prompt += f"{i}. {obj['class']} (置信度: {obj['confidence']:.2f})\n"
            prompt += f"\n总共检测到 {len(detection_info['objects'])} 个物体。\n\n"
        
        prompt += "请结合图像内容和检测结果，用中文回答用户的问题。"
        return prompt
    
    def get_scene_description(self, image, detection_info=None):
        """
        获取场景描述
        
        Args:
            image: OpenCV图像
            detection_info: 检测信息
            
        Returns:
            str: 场景描述
        """
        question = "请详细描述这个场景，包括环境、物体、人物活动等信息。"
        return self.analyze_image(image, question, detection_info)
    
    def check_safety(self, image, detection_info=None):
        """
        安全检查
        
        Args:
            image: OpenCV图像
            detection_info: 检测信息
            
        Returns:
            dict: 安全检查结果
        """
        question = "请分析这个场景是否存在安全隐患，如果有请详细说明。"
        response = self.analyze_image(image, question, detection_info)
        
        # 简单的关键词检测来判断是否有安全问题
        danger_keywords = ["危险", "隐患", "不安全", "风险", "注意", "小心"]
        has_danger = any(keyword in response for keyword in danger_keywords)
        
        return {
            "has_danger": has_danger,
            "description": response,
            "level": "高" if "严重" in response or "紧急" in response else "中" if has_danger else "低"
        }
    
    def answer_question(self, image, question, detection_info=None):
        """
        回答关于图像的问题
        
        Args:
            image: OpenCV图像
            question: 用户问题
            detection_info: 检测信息
            
        Returns:
            str: AI回答
        """
        return self.analyze_image(image, question, detection_info)