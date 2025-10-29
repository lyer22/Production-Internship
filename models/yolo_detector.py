"""
YOLO目标检测器
"""
import cv2
import numpy as np
from ultralytics import YOLO
from config import Config
import threading
import queue

class YOLODetector:
    def __init__(self):
        """初始化YOLO检测器"""
        self.model = None
        self.is_loaded = False
        self.detection_queue = queue.Queue(maxsize=10)
        self.load_model()
    
    def load_model(self):
        """加载YOLO模型"""
        try:
            print("正在加载YOLO模型...")
            self.model = YOLO(Config.YOLO_MODEL_PATH)
            self.is_loaded = True
            print("YOLO模型加载成功!")
        except Exception as e:
            print(f"YOLO模型加载失败: {e}")
            self.is_loaded = False
    
    def detect_objects(self, frame):
        """
        检测图像中的物体
        
        Args:
            frame: OpenCV图像帧
            
        Returns:
            dict: 检测结果
        """
        if not self.is_loaded:
            return {"objects": [], "annotated_frame": frame}
        
        try:
            # 运行检测
            results = self.model(
                frame,
                conf=Config.CONFIDENCE_THRESHOLD,
                iou=Config.IOU_THRESHOLD,
                verbose=False
            )
            
            # 解析检测结果
            objects = []
            annotated_frame = frame.copy()
            
            if results and len(results) > 0:
                result = results[0]
                
                # 绘制检测框和标签
                if result.boxes is not None:
                    boxes = result.boxes.xyxy.cpu().numpy()
                    confidences = result.boxes.conf.cpu().numpy()
                    class_ids = result.boxes.cls.cpu().numpy().astype(int)
                    
                    for i, (box, conf, class_id) in enumerate(zip(boxes, confidences, class_ids)):
                        x1, y1, x2, y2 = map(int, box)
                        
                        # 获取类别名称
                        class_name = Config.COCO_CLASSES[class_id] if class_id < len(Config.COCO_CLASSES) else f"class_{class_id}"
                        
                        # 添加到对象列表
                        objects.append({
                            "class": class_name,
                            "confidence": float(conf),
                            "bbox": [x1, y1, x2, y2],
                            "center": [(x1 + x2) // 2, (y1 + y2) // 2]
                        })
                        
                        # 绘制边界框
                        color = self._get_color(class_id)
                        cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
                        
                        # 绘制标签
                        label = f"{class_name}: {conf:.2f}"
                        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
                        cv2.rectangle(annotated_frame, (x1, y1 - label_size[1] - 10), 
                                    (x1 + label_size[0], y1), color, -1)
                        cv2.putText(annotated_frame, label, (x1, y1 - 5), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            
            return {
                "objects": objects,
                "annotated_frame": annotated_frame,
                "object_count": len(objects)
            }
            
        except Exception as e:
            print(f"检测过程中出错: {e}")
            return {"objects": [], "annotated_frame": frame, "object_count": 0}
    
    def _get_color(self, class_id):
        """根据类别ID生成颜色"""
        np.random.seed(class_id)
        return tuple(map(int, np.random.randint(0, 255, 3)))
    
    def get_detection_summary(self, objects):
        """
        生成检测结果摘要
        
        Args:
            objects: 检测到的对象列表
            
        Returns:
            str: 检测摘要
        """
        if not objects:
            return "未检测到任何物体"
        
        # 统计各类物体数量
        class_counts = {}
        for obj in objects:
            class_name = obj["class"]
            class_counts[class_name] = class_counts.get(class_name, 0) + 1
        
        # 生成摘要
        summary_parts = []
        for class_name, count in class_counts.items():
            if count == 1:
                summary_parts.append(f"1个{class_name}")
            else:
                summary_parts.append(f"{count}个{class_name}")
        
        return f"检测到: {', '.join(summary_parts)}"
    
    def is_model_ready(self):
        """检查模型是否准备就绪"""
        return self.is_loaded