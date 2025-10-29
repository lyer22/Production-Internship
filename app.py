"""
智能视觉分析助手 - Flask主应用
"""
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import cv2
import base64
import time
import json
from datetime import datetime

# 导入eventlet但不monkey_patch（避免递归错误）
import eventlet

# 导入自定义模块
from config import Config
from models.yolo_detector import YOLODetector
from models.qwen_client import QwenVLClient
from utils.video_processor import VideoProcessor
from utils.image_utils import resize_image, add_timestamp, image_to_base64

# 初始化Flask应用
app = Flask(__name__)
app.config.from_object(Config)
# 移除async_mode参数，让Flask-SocketIO自动选择最佳模式
socketio = SocketIO(app, cors_allowed_origins="*")

# 全局变量
video_processor = None
yolo_detector = None
qwen_client = None
is_processing = False
current_frame = None
detection_results = None

def initialize_components():
    """初始化系统组件"""
    global video_processor, yolo_detector, qwen_client
    
    print("正在初始化系统组件...")
    
    # 初始化视频处理器
    video_processor = VideoProcessor()
    
    # 初始化YOLO检测器
    yolo_detector = YOLODetector()
    
    # 初始化Qwen客户端
    qwen_client = QwenVLClient()
    
    print("系统组件初始化完成!")

def video_stream_greenthread():
    """视频流处理greenthread - 使用eventlet"""
    global is_processing, current_frame, detection_results
    
    print("🎥 视频流greenthread已启动（eventlet模式）")
    frame_count = 0
    last_log_time = time.time()
    
    while True:
        try:
            # 每5秒打印一次状态
            if time.time() - last_log_time > 5:
                print(f"📊 状态: 摄像头可用={video_processor.is_camera_available() if video_processor else False}, 帧数={frame_count}")
                last_log_time = time.time()
            
            if video_processor and video_processor.is_camera_available():
                frame = video_processor.get_latest_frame()
                
                if frame is not None:
                    current_frame = frame.copy()
                    frame_count += 1
                    
                    # 执行目标检测
                    if yolo_detector and yolo_detector.is_model_ready():
                        detection_results = yolo_detector.detect_objects(frame)
                        annotated_frame = detection_results.get('annotated_frame', frame)
                    else:
                        annotated_frame = frame
                        detection_results = {"objects": [], "object_count": 0}
                    
                    # 添加时间戳
                    timestamped_frame = add_timestamp(annotated_frame)
                    
                    # 调整图像大小（使用配置的最大尺寸）
                    display_frame = resize_image(
                        timestamped_frame, 
                        max_width=Config.MAX_FRAME_WIDTH, 
                        max_height=Config.MAX_FRAME_HEIGHT
                    )
                    
                    # 转换为base64并发送（使用配置的质量）
                    frame_base64 = image_to_base64(display_frame, quality=Config.STREAM_QUALITY)
                    if frame_base64:
                        try:
                            # 使用eventlet的方式发送
                            with app.app_context():
                                socketio.emit('video_frame', {
                                    'frame': frame_base64,
                                    'detection_info': {
                                        'object_count': detection_results.get('object_count', 0),
                                        'objects': detection_results.get('objects', [])
                                    },
                                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                }, namespace='/')
                            
                            # 每30帧打印一次状态
                            if frame_count % 30 == 0:
                                print(f"📹 已发送 {frame_count} 帧, 帧大小: {len(frame_base64)} 字节")
                        except Exception as e:
                            print(f"❌ WebSocket发送失败: {e}")
                    else:
                        if frame_count % 30 == 0:
                            print(f"❌ 帧转换失败")
            else:
                # 摄像头未启动时等待
                eventlet.sleep(0.5)
            
            eventlet.sleep(1.0 / Config.STREAM_FPS)  # 使用配置的流帧率
            
        except Exception as e:
            print(f"❌ 视频流处理错误: {e}")
            import traceback
            traceback.print_exc()
            eventlet.sleep(1)

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/camera/start', methods=['POST'])
def start_camera():
    """启动摄像头"""
    global video_greenthread
    try:
        if video_processor.start_capture():
            # 启动视频流greenthread（如果还没启动）
            if video_greenthread is None:
                video_greenthread = eventlet.spawn(video_stream_greenthread)
                print("✅ 视频流greenthread已启动")
            return jsonify({"success": True, "message": "摄像头启动成功"})
        else:
            return jsonify({"success": False, "message": "摄像头启动失败"})
    except Exception as e:
        return jsonify({"success": False, "message": f"启动摄像头时出错: {str(e)}"})

@app.route('/api/camera/stop', methods=['POST'])
def stop_camera():
    """停止摄像头"""
    try:
        video_processor.stop_capture()
        return jsonify({"success": True, "message": "摄像头已停止"})
    except Exception as e:
        return jsonify({"success": False, "message": f"停止摄像头时出错: {str(e)}"})

@app.route('/api/camera/info', methods=['GET'])
def camera_info():
    """获取摄像头信息"""
    try:
        info = video_processor.get_camera_info()
        return jsonify({"success": True, "data": info})
    except Exception as e:
        return jsonify({"success": False, "message": f"获取摄像头信息失败: {str(e)}"})

@app.route('/api/detection/summary', methods=['GET'])
def detection_summary():
    """获取检测摘要"""
    try:
        if detection_results and detection_results.get('objects'):
            summary = yolo_detector.get_detection_summary(detection_results['objects'])
            return jsonify({
                "success": True, 
                "summary": summary,
                "object_count": detection_results.get('object_count', 0),
                "objects": detection_results.get('objects', [])
            })
        else:
            return jsonify({
                "success": True, 
                "summary": "未检测到任何物体",
                "object_count": 0,
                "objects": []
            })
    except Exception as e:
        return jsonify({"success": False, "message": f"获取检测摘要失败: {str(e)}"})

@socketio.on('connect')
def handle_connect():
    """客户端连接"""
    print('客户端已连接')
    emit('status', {'message': '连接成功'})

@socketio.on('disconnect')
def handle_disconnect():
    """客户端断开连接"""
    print('客户端已断开连接')

@socketio.on('ask_question')
def handle_question(data):
    """处理用户问题"""
    try:
        print(f"📥 收到问题请求: {data}")
        question = data.get('question', '')
        
        if not question:
            print("❌ 问题为空")
            emit('ai_response', {'error': '问题不能为空'})
            return
        
        if current_frame is None:
            print("❌ 当前没有视频帧")
            emit('ai_response', {'error': '当前没有可用的视频帧'})
            return
        
        print(f"🤖 开始调用AI模型分析问题: {question}")
        
        # 使用Qwen分析当前帧
        response = qwen_client.answer_question(
            current_frame, 
            question, 
            detection_results
        )
        
        print(f"✅ AI回答生成成功: {response[:100]}...")
        
        response_data = {
            'question': question,
            'answer': response,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        print(f"📤 发送AI回答到前端")
        emit('ai_response', response_data)
        
    except Exception as e:
        print(f"❌ 处理问题时出错: {e}")
        import traceback
        traceback.print_exc()
        emit('ai_response', {'error': f'处理问题时出错: {str(e)}'})

@socketio.on('analyze_scene')
def handle_scene_analysis():
    """场景分析"""
    try:
        print("🔍 开始场景分析...")
        
        if current_frame is None:
            print("❌ 当前没有视频帧")
            emit('scene_analysis', {'error': '当前没有可用的视频帧'})
            return
        
        print("🤖 调用AI进行场景描述...")
        # 获取场景描述
        description = qwen_client.get_scene_description(current_frame, detection_results)
        
        print("🛡️ 进行安全检查...")
        # 安全检查
        safety_check = qwen_client.check_safety(current_frame, detection_results)
        
        print("✅ 场景分析完成")
        
        emit('scene_analysis', {
            'description': description,
            'safety': safety_check,
            'detection_summary': yolo_detector.get_detection_summary(
                detection_results.get('objects', []) if detection_results else []
            ),
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
    except Exception as e:
        print(f"❌ 场景分析时出错: {e}")
        import traceback
        traceback.print_exc()
        emit('scene_analysis', {'error': f'场景分析时出错: {str(e)}'})

@socketio.on('capture_image')
def handle_capture():
    """捕获当前图像"""
    try:
        if current_frame is None:
            emit('image_captured', {'error': '当前没有可用的视频帧'})
            return
        
        # 保存图像
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"capture_{timestamp}.jpg"
        
        # 添加时间戳到图像
        timestamped_frame = add_timestamp(current_frame)
        cv2.imwrite(f"static/captures/{filename}", timestamped_frame)
        
        # 转换为base64用于显示
        image_base64 = image_to_base64(timestamped_frame)
        
        emit('image_captured', {
            'filename': filename,
            'image': image_base64,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
    except Exception as e:
        print(f"捕获图像时出错: {e}")
        emit('image_captured', {'error': f'捕获图像时出错: {str(e)}'})

# 全局视频流greenthread
video_greenthread = None

if __name__ == '__main__':
    # 初始化系统组件
    initialize_components()
    
    # 不在启动时启动视频流线程，等待摄像头启动后再启动
    # 这样可以避免WebSocket连接问题
    
    # 创建必要的目录
    import os
    os.makedirs('static/captures', exist_ok=True)
    
    print(f"智能视觉分析助手启动中...")
    print(f"访问地址: http://{Config.HOST}:{Config.PORT}")
    print("💡 提示: 点击'启动'按钮后视频流将开始传输")
    
    # 启动Flask应用
    print("🚀 启动SocketIO服务器...")
    socketio.run(
        app, 
        host=Config.HOST, 
        port=Config.PORT, 
        debug=False,
        allow_unsafe_werkzeug=True
    )