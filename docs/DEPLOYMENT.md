# 部署指南

## 本地部署

### 环境要求
- Python 3.8+
- 摄像头设备
- 阿里云百炼API密钥

### 快速开始

1. **克隆项目**
```bash
git clone <repository-url>
cd smart_vision_assistant
```

2. **运行安装脚本**
```bash
python install.py
```

3. **配置API密钥**
```bash
cp config_template.py config.py
# 编辑 config.py，填入您的API密钥
```

4. **启动应用**
```bash
python run.py
```

5. **访问应用**
打开浏览器访问: http://localhost:5000

### 手动安装

1. **创建虚拟环境**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境变量**
```bash
export DASHSCOPE_API_KEY="your-api-key"
```

4. **启动应用**
```bash
python app.py
```

## Docker 部署

### 创建 Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 创建必要目录
RUN mkdir -p static/captures logs

EXPOSE 5000

CMD ["python", "run.py", "--host", "0.0.0.0"]
```

### 构建和运行
```bash
# 构建镜像
docker build -t smart-vision-assistant .

# 运行容器
docker run -p 5000:5000 \
  -e DASHSCOPE_API_KEY="your-api-key" \
  --device=/dev/video0:/dev/video0 \
  smart-vision-assistant
```

## 云服务器部署

### 使用 Nginx 反向代理

1. **安装 Nginx**
```bash
sudo apt update
sudo apt install nginx
```

2. **配置 Nginx**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /socket.io/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

3. **使用 Supervisor 管理进程**
```ini
[program:smart_vision_assistant]
command=/path/to/venv/bin/python /path/to/app/run.py
directory=/path/to/app
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/smart_vision_assistant.log
environment=DASHSCOPE_API_KEY="your-api-key"
```

## 性能优化

### 1. 视频流优化
- 调整帧率和分辨率
- 使用硬件加速
- 优化图像压缩质量

### 2. 模型优化
- 使用量化模型
- 批处理检测
- 异步处理

### 3. 网络优化
- 启用 gzip 压缩
- 使用 CDN
- 优化 WebSocket 连接

## 监控和日志

### 日志配置
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
```

### 健康检查
```python
@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })
```

## 故障排除

### 常见问题

1. **摄像头无法访问**
   - 检查摄像头权限
   - 确认摄像头索引
   - 检查是否被其他程序占用

2. **API调用失败**
   - 验证API密钥
   - 检查网络连接
   - 查看API配额

3. **模型加载失败**
   - 检查磁盘空间
   - 验证模型文件
   - 查看内存使用

### 调试模式
```bash
python run.py --debug
```

### 查看日志
```bash
tail -f logs/app.log
```