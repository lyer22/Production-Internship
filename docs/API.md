# API 文档

## REST API 接口

### 摄像头控制

#### 启动摄像头
```
POST /api/camera/start
```

**响应:**
```json
{
    "success": true,
    "message": "摄像头启动成功"
}
```

#### 停止摄像头
```
POST /api/camera/stop
```

**响应:**
```json
{
    "success": true,
    "message": "摄像头已停止"
}
```

#### 获取摄像头信息
```
GET /api/camera/info
```

**响应:**
```json
{
    "success": true,
    "data": {
        "available": true,
        "width": 640,
        "height": 480,
        "fps": 30.0,
        "camera_index": 0
    }
}
```

### 检测结果

#### 获取检测摘要
```
GET /api/detection/summary
```

**响应:**
```json
{
    "success": true,
    "summary": "检测到: 1个person, 2个chair",
    "object_count": 3,
    "objects": [
        {
            "class": "person",
            "confidence": 0.85,
            "bbox": [100, 50, 200, 300],
            "center": [150, 175]
        }
    ]
}
```

## WebSocket 事件

### 客户端发送事件

#### 询问问题
```javascript
socket.emit('ask_question', {
    question: "这个场景中有什么？"
});
```

#### 场景分析
```javascript
socket.emit('analyze_scene');
```

#### 截图
```javascript
socket.emit('capture_image');
```

### 服务器发送事件

#### 视频帧更新
```javascript
socket.on('video_frame', (data) => {
    // data.frame: base64编码的图像
    // data.detection_info: 检测信息
    // data.timestamp: 时间戳
});
```

#### AI回答
```javascript
socket.on('ai_response', (data) => {
    // data.question: 用户问题
    // data.answer: AI回答
    // data.timestamp: 时间戳
});
```

#### 场景分析结果
```javascript
socket.on('scene_analysis', (data) => {
    // data.description: 场景描述
    // data.safety: 安全评估
    // data.detection_summary: 检测摘要
});
```

#### 截图结果
```javascript
socket.on('image_captured', (data) => {
    // data.filename: 文件名
    // data.image: base64图像
    // data.timestamp: 时间戳
});
```

## 错误处理

所有API响应都包含 `success` 字段：
- `true`: 操作成功
- `false`: 操作失败，查看 `message` 字段获取错误信息

WebSocket事件可能包含 `error` 字段表示错误信息。