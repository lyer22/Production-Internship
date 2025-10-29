#!/usr/bin/env python3
"""
智能视觉分析助手演示脚本
用于展示系统功能，无需真实摄像头和API密钥
"""
import cv2
import numpy as np
import time
import threading
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import base64
from datetime import datetime

# 创建演示应用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'demo-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

class DemoVideoGenerator:
    """演示视频生成器"""
    
    def __init__(self):
        self.is_running = False
        self.frame_count = 0
        
    def generate_demo_frame(self):
        """生成演示帧"""
        # 创建基础画布
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        frame[:] = (50, 50, 50)  # 深灰色背景
        
        # 添加动态元素
        t = time.time()
        
        # 移动的圆形（模拟人）
        x = int(320 + 200 * np.sin(t * 0.5))
        y = int(240 + 100 * np.cos(t * 0.3))
        cv2.circle(frame, (x, y), 30, (0, 255, 0), -1)
        cv2.putText(frame, 'Person', (x-30, y-40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # 静态矩形（模拟车辆）
        cv2.rectangle(frame, (100, 350), (200, 400), (255, 0, 0), -1)
        cv2.putText(frame, 'Car', (110, 340), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # 另一个移动物体（模拟自行车）
        x2 = int(500 + 80 * np.sin(t * 0.8))
        y2 = 200
        cv2.rectangle(frame, (x2-20, y2-10), (x2+20, y2+10), (0, 255, 255), -1)
        cv2.putText(frame, 'Bicycle', (x2-30, y2-20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        # 添加时间戳
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, f"DEMO - {timestamp}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # 添加帧计数
        cv2.putText(frame, f"Frame: {self.frame_count}", (10, 460), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        self.frame_count += 1
        return frame
    
    def get_demo_detection_info(self):
        """获取演示检测信息"""
        return {
            "object_count": 3,
            "objects": [
                {"class": "person", "confidence": 0.95, "bbox": [290, 210, 350, 270]},
                {"class": "car", "confidence": 0.88, "bbox": [100, 350, 200, 400]},
                {"class": "bicycle", "confidence": 0.82, "bbox": [460, 190, 520, 210]}
            ]
        }

# 全局变量
demo_generator = DemoVideoGenerator()
is_demo_running = False

def demo_video_thread():
    """演示视频线程"""
    global is_demo_running
    
    while is_demo_running:
        try:
            # 生成演示帧
            frame = demo_generator.generate_demo_frame()
            detection_info = demo_generator.get_demo_detection_info()
            
            # 转换为base64
            _, buffer = cv2.imencode('.jpg', frame)
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            frame_data_url = f"data:image/jpeg;base64,{frame_base64}"
            
            # 发送到前端
            socketio.emit('video_frame', {
                'frame': frame_data_url,
                'detection_info': detection_info,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
            time.sleep(1.0 / 15)  # 15 FPS
            
        except Exception as e:
            print(f"演示视频线程错误: {e}")
            time.sleep(1)

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/camera/start', methods=['POST'])
def start_demo_camera():
    """启动演示摄像头"""
    global is_demo_running
    
    if not is_demo_running:
        is_demo_running = True
        thread = threading.Thread(target=demo_video_thread)
        thread.daemon = True
        thread.start()
    
    return jsonify({"success": True, "message": "演示摄像头启动成功"})

@app.route('/api/camera/stop', methods=['POST'])
def stop_demo_camera():
    """停止演示摄像头"""
    global is_demo_running
    is_demo_running = False
    return jsonify({"success": True, "message": "演示摄像头已停止"})

@app.route('/api/camera/info', methods=['GET'])
def demo_camera_info():
    """获取演示摄像头信息"""
    return jsonify({
        "success": True,
        "data": {
            "available": True,
            "width": 640,
            "height": 480,
            "fps": 15.0,
            "camera_index": "DEMO"
        }
    })

@app.route('/api/detection/summary', methods=['GET'])
def demo_detection_summary():
    """获取演示检测摘要"""
    return jsonify({
        "success": True,
        "summary": "检测到: 1个person, 1个car, 1个bicycle",
        "object_count": 3,
        "objects": demo_generator.get_demo_detection_info()["objects"]
    })

@socketio.on('connect')
def handle_connect():
    """客户端连接"""
    print('演示客户端已连接')
    emit('status', {'message': '演示模式连接成功'})

@socketio.on('ask_question')
def handle_demo_question(data):
    """处理演示问题"""
    question = data.get('question', '')
    
    # 模拟AI回答
    demo_answers = {
        "这个场景中有什么？": "在这个演示场景中，我看到了一个人在移动，一辆静止的汽车，以及一辆正在行驶的自行车。这是一个典型的城市交通场景。",
        "有什么安全隐患吗？": "从当前场景来看，人员和车辆都保持着安全距离，没有发现明显的安全隐患。建议继续保持警惕。",
        "统计一下物体数量": "当前场景中检测到3个物体：1个人、1辆汽车和1辆自行车。",
        "场景描述": "这是一个动态的城市交通演示场景，包含了行人、车辆等常见的交通元素，用于展示智能视觉分析系统的检测能力。"
    }
    
    # 查找最匹配的回答
    answer = "这是一个演示场景，展示了智能视觉分析系统的基本功能。系统可以检测和识别场景中的各种物体，并提供相应的分析和建议。"
    
    for key, value in demo_answers.items():
        if key in question or any(word in question for word in key.split()):
            answer = value
            break
    
    # 模拟处理时间
    time.sleep(1)
    
    emit('ai_response', {
        'question': question,
        'answer': answer,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@socketio.on('analyze_scene')
def handle_demo_scene_analysis():
    """处理演示场景分析"""
    # 模拟处理时间
    time.sleep(2)
    
    emit('scene_analysis', {
        'description': '这是一个动态的城市交通演示场景。场景中包含一个移动的行人，一辆静止的红色汽车，以及一辆正在行驶的黄色自行车。整体环境光线适中，视野清晰，适合进行目标检测和分析。',
        'safety': {
            'has_danger': False,
            'level': '低',
            'description': '当前场景安全状况良好。所有交通参与者都保持着适当的距离，没有发现碰撞风险或其他安全隐患。建议继续监控以确保安全。'
        },
        'detection_summary': '检测到: 1个person, 1个car, 1个bicycle',
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@socketio.on('capture_image')
def handle_demo_capture():
    """处理演示截图"""
    # 生成当前帧
    frame = demo_generator.generate_demo_frame()
    
    # 转换为base64
    _, buffer = cv2.imencode('.jpg', frame)
    image_base64 = base64.b64encode(buffer).decode('utf-8')
    image_data_url = f"data:image/jpeg;base64,{image_base64}"
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"demo_capture_{timestamp}.jpg"
    
    emit('image_captured', {
        'filename': filename,
        'image': image_data_url,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

def main():
    """主函数"""
    print("🎬 智能视觉分析助手 - 演示模式")
    print("=" * 50)
    print("📋 演示功能:")
    print("   ✅ 模拟视频流")
    print("   ✅ 目标检测演示")
    print("   ✅ AI问答演示")
    print("   ✅ 场景分析演示")
    print("   ✅ 截图功能演示")
    print("=" * 50)
    print("🌐 访问地址: http://localhost:5000")
    print("💡 提示: 这是演示模式，不需要真实摄像头和API密钥")
    print("按 Ctrl+C 停止演示")
    print("=" * 50)
    
    try:
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n👋 演示已停止")

if __name__ == '__main__':
    main()