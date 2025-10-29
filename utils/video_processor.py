"""
视频处理工具
"""
import cv2
import threading
import queue
import time
import numpy as np
from config import Config

class VideoProcessor:
    def __init__(self, camera_index=None):
        """
        初始化视频处理器
        
        Args:
            camera_index: 摄像头索引，默认使用配置文件中的值
        """
        self.camera_index = camera_index or Config.CAMERA_INDEX
        self.cap = None
        self.is_running = False
        self.frame_queue = queue.Queue(maxsize=5)
        self.latest_frame = None
        self.frame_lock = threading.Lock()
        
    def start_capture(self):
        """开始视频捕获"""
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            if not self.cap.isOpened():
                print(f"无法打开摄像头 {self.camera_index}")
                return False
            
            # 设置摄像头参数（高分辨率）
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, Config.FRAME_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, Config.FRAME_HEIGHT)
            self.cap.set(cv2.CAP_PROP_FPS, Config.FPS)
            
            # 优化设置
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # 减少缓冲延迟
            self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))  # 使用MJPEG编码
            
            # 验证实际设置的分辨率
            actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = self.cap.get(cv2.CAP_PROP_FPS)
            
            print(f"✅ 摄像头配置: {actual_width}x{actual_height} @ {actual_fps}fps")
            
            self.is_running = True
            
            # 启动捕获线程
            self.capture_thread = threading.Thread(target=self._capture_loop)
            self.capture_thread.daemon = True
            self.capture_thread.start()
            
            print("视频捕获已启动")
            return True
            
        except Exception as e:
            print(f"启动视频捕获失败: {e}")
            return False
    
    def stop_capture(self):
        """停止视频捕获"""
        self.is_running = False
        if hasattr(self, 'capture_thread'):
            self.capture_thread.join(timeout=2)
        
        if self.cap:
            self.cap.release()
            self.cap = None
        
        print("视频捕获已停止")
    
    def _capture_loop(self):
        """视频捕获循环"""
        print("摄像头捕获循环已启动")
        frame_count = 0
        
        while self.is_running and self.cap and self.cap.isOpened():
            try:
                ret, frame = self.cap.read()
                if ret:
                    frame_count += 1
                    with self.frame_lock:
                        self.latest_frame = frame.copy()
                    
                    # 将帧放入队列（非阻塞）
                    try:
                        self.frame_queue.put_nowait(frame)
                    except queue.Full:
                        # 队列满时丢弃最旧的帧
                        try:
                            self.frame_queue.get_nowait()
                            self.frame_queue.put_nowait(frame)
                        except queue.Empty:
                            pass
                    
                    # 每100帧打印一次状态
                    if frame_count % 100 == 0:
                        print(f"已捕获 {frame_count} 帧")
                        
                else:
                    print("无法读取视频帧")
                    break
                    
                time.sleep(1.0 / Config.FPS)
                
            except Exception as e:
                print(f"视频捕获循环出错: {e}")
                break
        
        print("摄像头捕获循环已停止")
    
    def get_latest_frame(self):
        """
        获取最新的视频帧
        
        Returns:
            numpy.ndarray: 最新的视频帧，如果没有则返回None
        """
        with self.frame_lock:
            if self.latest_frame is not None:
                return self.latest_frame.copy()
        return None
    
    def get_frame_from_queue(self):
        """
        从队列中获取视频帧
        
        Returns:
            numpy.ndarray: 视频帧，如果队列为空则返回None
        """
        try:
            return self.frame_queue.get_nowait()
        except queue.Empty:
            return None
    
    def is_camera_available(self):
        """检查摄像头是否可用"""
        return self.cap is not None and self.cap.isOpened() and self.is_running
    
    def get_camera_info(self):
        """
        获取摄像头信息
        
        Returns:
            dict: 摄像头信息
        """
        if not self.cap:
            return {"available": False}
        
        try:
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            
            return {
                "available": True,
                "width": width,
                "height": height,
                "fps": fps,
                "camera_index": self.camera_index
            }
        except Exception as e:
            print(f"获取摄像头信息失败: {e}")
            return {"available": False, "error": str(e)}
    
    def resize_frame(self, frame, width=None, height=None):
        """
        调整帧大小
        
        Args:
            frame: 输入帧
            width: 目标宽度
            height: 目标高度
            
        Returns:
            numpy.ndarray: 调整大小后的帧
        """
        if width is None and height is None:
            return frame
        
        h, w = frame.shape[:2]
        
        if width is None:
            width = int(w * height / h)
        elif height is None:
            height = int(h * width / w)
        
        return cv2.resize(frame, (width, height))
    
    def frame_to_bytes(self, frame, format='.jpg', quality=90):
        """
        将帧转换为字节数据
        
        Args:
            frame: OpenCV帧
            format: 图像格式
            quality: JPEG质量 (1-100)
            
        Returns:
            bytes: 图像字节数据
        """
        try:
            if format == '.jpg':
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
            else:
                encode_param = []
            
            _, buffer = cv2.imencode(format, frame, encode_param)
            return buffer.tobytes()
        except Exception as e:
            print(f"帧转换为字节失败: {e}")
            return None