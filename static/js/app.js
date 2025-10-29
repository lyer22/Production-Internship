// 智能视觉分析助手 - 工作版本 v5.0
console.log('=== 加载 app_working.js v5.0 ===');

class SmartVisionApp {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.frameCount = 0;
        this.lastFrameTime = Date.now();
        this.fpsInterval = null;
        
        console.log('SmartVisionApp 初始化');
        this.init();
    }
    
    init() {
        console.log('开始初始化...');
        this.initSocket();
        this.bindEvents();
        this.startFPSCounter();
        console.log('初始化完成');
    }
    
    initSocket() {
        console.log('初始化Socket连接...');
        console.log('当前URL:', window.location.href);
        
        // 显式配置Socket.IO连接
        this.socket = io({
            transports: ['polling', 'websocket'],
            upgrade: true,
            rememberUpgrade: true
        });
        
        this.socket.on('connect', () => {
            console.log('✅ Socket连接成功');
            console.log('Socket ID:', this.socket.id);
            console.log('传输方式:', this.socket.io.engine.transport.name);
            this.isConnected = true;
            this.updateConnectionStatus(true);
            this.showNotification('连接成功', 'success');
        });
        
        this.socket.on('connect_error', (error) => {
            console.error('❌ Socket连接错误:', error);
            console.error('错误详情:', error.message);
            this.showNotification('连接失败: ' + error.message, 'error');
        });
        
        this.socket.on('disconnect', (reason) => {
            console.log('❌ Socket断开连接');
            console.log('断开原因:', reason);
            this.isConnected = false;
            this.updateConnectionStatus(false);
            this.showNotification('连接断开: ' + reason, 'warning');
        });
        
        this.socket.on('video_frame', (data) => {
            this.updateVideoFrame(data);
        });
        
        this.socket.on('ai_response', (data) => {
            console.log('🤖 收到ai_response事件');
            console.log('完整数据:', data);
            this.handleAIResponse(data);
        });
        
        this.socket.on('scene_analysis', (data) => {
            this.handleSceneAnalysis(data);
        });
        
        this.socket.on('image_captured', (data) => {
            this.handleImageCapture(data);
        });
    }
    
    bindEvents() {
        document.getElementById('start-camera').addEventListener('click', () => {
            this.startCamera();
        });
        
        document.getElementById('stop-camera').addEventListener('click', () => {
            this.stopCamera();
        });
        
        document.getElementById('capture-image').addEventListener('click', () => {
            this.captureImage();
        });
        
        document.getElementById('ask-question').addEventListener('click', () => {
            this.askQuestion();
        });
        
        document.getElementById('question-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.askQuestion();
            }
        });
        
        document.getElementById('analyze-scene').addEventListener('click', () => {
            this.analyzeScene();
        });
    }
    
    async startCamera() {
        this.showLoading(true);
        
        try {
            const response = await fetch('/api/camera/start', {
                method: 'POST'
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification('摄像头启动成功', 'success');
                document.getElementById('camera-status').textContent = '运行中';
                document.getElementById('camera-status').className = 'h6 mb-0 text-success';
            } else {
                this.showNotification(result.message, 'error');
            }
        } catch (error) {
            this.showNotification('启动摄像头失败: ' + error.message, 'error');
        } finally {
            this.showLoading(false);
        }
    }
    
    async stopCamera() {
        try {
            const response = await fetch('/api/camera/stop', {
                method: 'POST'
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification('摄像头已停止', 'info');
                document.getElementById('camera-status').textContent = '已停止';
                document.getElementById('camera-status').className = 'h6 mb-0 text-secondary';
                
                const videoStream = document.getElementById('video-stream');
                videoStream.src = "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjQwIiBoZWlnaHQ9IjQ4MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZGRkIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtc2l6ZT0iMTgiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj7op4blkpHmtYHlvIE8L3RleHQ+PC9zdmc+";
            } else {
                this.showNotification(result.message, 'error');
            }
        } catch (error) {
            this.showNotification('停止摄像头失败: ' + error.message, 'error');
        }
    }
    
    updateVideoFrame(data) {
        console.log('📹 收到视频帧，大小:', data.frame ? data.frame.length : 0);
        const videoStream = document.getElementById('video-stream');
        if (videoStream && data.frame) {
            videoStream.src = data.frame;
            console.log('✅ 视频帧已更新');
        } else {
            console.error('❌ 视频元素或帧数据不存在');
        }
        this.updateDetectionInfo(data.detection_info);
        this.frameCount++;
    }
    
    updateDetectionInfo(detectionInfo) {
        document.getElementById('object-count').textContent = detectionInfo.object_count || 0;
        
        const resultsContainer = document.getElementById('detection-results');
        
        if (detectionInfo.objects && detectionInfo.objects.length > 0) {
            let html = '';
            detectionInfo.objects.forEach(obj => {
                html += `
                    <span class="detection-item">
                        ${obj.class} 
                        <span class="confidence">${(obj.confidence * 100).toFixed(1)}%</span>
                    </span>
                `;
            });
            resultsContainer.innerHTML = html;
        } else {
            resultsContainer.innerHTML = '<p class="text-muted mb-0">暂无检测结果</p>';
        }
    }
    
    askQuestion() {
        const input = document.getElementById('question-input');
        const question = input.value.trim();
        
        console.log('askQuestion 被调用, 问题:', question);
        
        if (!question) {
            this.showNotification('请输入问题', 'warning');
            return;
        }
        
        // 添加用户消息
        this.addChatMessage(question, 'user');
        
        // 发送到服务器
        console.log('发送问题到服务器:', question);
        this.socket.emit('ask_question', { question: question });
        
        // 清空输入框
        input.value = '';
        
        // 显示加载状态
        this.addChatMessage('正在思考中...', 'ai', true);
    }
    
    handleAIResponse(data) {
        console.log('=== handleAIResponse 开始 ===');
        console.log('收到的数据:', data);
        console.log('数据类型:', typeof data);
        console.log('JSON字符串:', JSON.stringify(data));
        
        // 移除加载消息
        this.removeLoadingMessage();
        
        // 检查是否是字符串（可能被序列化了）
        if (typeof data === 'string') {
            try {
                data = JSON.parse(data);
                console.log('解析后的数据:', data);
            } catch (e) {
                console.error('JSON解析失败:', e);
            }
        }
        
        if (data.error) {
            console.log('处理错误:', data.error);
            const errorMsg = String(data.error);
            this.addChatMessage('抱歉，出现错误: ' + errorMsg, 'ai');
            this.showNotification(errorMsg, 'error');
        } else if (data.answer) {
            console.log('处理回答:', data.answer);
            console.log('回答类型:', typeof data.answer);
            
            // 强制转换为字符串
            let answer = '';
            if (typeof data.answer === 'string') {
                answer = data.answer;
            } else if (typeof data.answer === 'object') {
                // 如果是对象，尝试提取文本
                answer = JSON.stringify(data.answer);
                console.warn('answer是对象，已转换为JSON字符串');
            } else {
                answer = String(data.answer);
            }
            
            console.log('最终回答:', answer);
            this.addChatMessage(answer, 'ai');
        } else {
            console.error('未知的数据格式:', data);
            console.error('数据keys:', Object.keys(data));
            this.addChatMessage('收到了未知格式的回答: ' + JSON.stringify(data), 'ai');
        }
        
        console.log('=== handleAIResponse 结束 ===');
    }
    
    addChatMessage(message, sender, isLoading = false) {
        console.log('addChatMessage:', message, sender, isLoading);
        
        const container = document.getElementById('chat-messages');
        if (!container) {
            console.error('找不到 chat-messages 容器!');
            return;
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        // 确保message是字符串
        let messageText = message;
        if (typeof message !== 'string') {
            messageText = String(message);
        }
        
        if (isLoading) {
            messageDiv.classList.add('loading-message');
            messageDiv.innerHTML = `
                <div class="d-flex align-items-center">
                    <div class="spinner-border spinner-border-sm me-2" role="status"></div>
                    ${messageText}
                </div>
            `;
        } else {
            messageDiv.innerHTML = `
                <div>${messageText}</div>
                <div class="timestamp">${new Date().toLocaleTimeString()}</div>
            `;
        }
        
        container.appendChild(messageDiv);
        container.scrollTop = container.scrollHeight;
        
        console.log('消息已添加到DOM, 当前消息数:', container.children.length);
    }
    
    removeLoadingMessage() {
        const loadingMessage = document.querySelector('.loading-message');
        if (loadingMessage) {
            console.log('移除加载消息');
            loadingMessage.remove();
        }
    }
    
    analyzeScene() {
        this.showLoading(true);
        this.socket.emit('analyze_scene');
    }
    
    handleSceneAnalysis(data) {
        console.log('=== handleSceneAnalysis 开始 ===');
        console.log('收到的数据:', data);
        console.log('数据类型:', typeof data);
        
        this.showLoading(false);
        
        const container = document.getElementById('scene-analysis');
        
        if (data.error) {
            container.innerHTML = `<p class="text-danger">${data.error}</p>`;
            return;
        }
        
        // 确保所有字段都是字符串
        let description = '无';
        if (data.description) {
            if (typeof data.description === 'string') {
                description = data.description;
            } else {
                description = JSON.stringify(data.description);
                console.warn('description是对象:', data.description);
            }
        }
        
        let safetyLevel = '未知';
        let safetyDescription = '无';
        let safetyClass = 'safety-low';
        
        if (data.safety) {
            console.log('safety对象:', data.safety);
            console.log('safety类型:', typeof data.safety);
            
            if (data.safety.level) {
                safetyLevel = String(data.safety.level);
                if (safetyLevel === '中') safetyClass = 'safety-medium';
                if (safetyLevel === '高') safetyClass = 'safety-high';
            }
            
            if (data.safety.description) {
                if (typeof data.safety.description === 'string') {
                    safetyDescription = data.safety.description;
                } else {
                    safetyDescription = JSON.stringify(data.safety.description);
                    console.warn('safety.description是对象:', data.safety.description);
                }
            }
        }
        
        let detectionSummary = '无';
        if (data.detection_summary) {
            detectionSummary = String(data.detection_summary);
        }
        
        let timestamp = '';
        if (data.timestamp) {
            timestamp = String(data.timestamp);
        }
        
        console.log('处理后的数据:');
        console.log('- description:', description);
        console.log('- safetyLevel:', safetyLevel);
        console.log('- safetyDescription:', safetyDescription);
        console.log('- detectionSummary:', detectionSummary);
        
        container.innerHTML = `
            <div class="mb-3">
                <h6>场景描述:</h6>
                <p class="mb-2">${description}</p>
            </div>
            
            <div class="mb-3">
                <h6>安全评估:</h6>
                <div class="safety-level ${safetyClass}">
                    安全等级: ${safetyLevel}
                </div>
                <p class="mb-2">${safetyDescription}</p>
            </div>
            
            <div class="mb-2">
                <h6>检测摘要:</h6>
                <p class="mb-0">${detectionSummary}</p>
            </div>
            
            <small class="text-muted">分析时间: ${timestamp}</small>
        `;
        
        console.log('=== handleSceneAnalysis 结束 ===');
    }
    
    captureImage() {
        this.socket.emit('capture_image');
    }
    
    handleImageCapture(data) {
        if (data.error) {
            this.showNotification(data.error, 'error');
            return;
        }
        
        const modal = new bootstrap.Modal(document.getElementById('captureModal'));
        document.getElementById('captured-image').src = data.image;
        document.getElementById('capture-time').textContent = data.timestamp;
        
        this.capturedImageData = data.image;
        this.capturedImageName = data.filename;
        
        modal.show();
        this.showNotification('截图成功', 'success');
    }
    
    updateConnectionStatus(isConnected) {
        const statusIndicator = document.getElementById('status-indicator');
        const connectionStatus = document.getElementById('connection-status');
        
        if (isConnected) {
            statusIndicator.innerHTML = '<i class="fas fa-circle text-success me-1"></i>已连接';
            connectionStatus.innerHTML = '<span class="text-success">在线</span>';
        } else {
            statusIndicator.innerHTML = '<i class="fas fa-circle text-danger me-1"></i>未连接';
            connectionStatus.innerHTML = '<span class="text-danger">离线</span>';
        }
    }
    
    showLoading(show) {
        const overlay = document.getElementById('loading-overlay');
        if (show) {
            overlay.classList.remove('d-none');
        } else {
            overlay.classList.add('d-none');
        }
    }
    
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${this.getBootstrapAlertClass(type)} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }
    
    getBootstrapAlertClass(type) {
        const classMap = {
            'success': 'success',
            'error': 'danger',
            'warning': 'warning',
            'info': 'info'
        };
        return classMap[type] || 'info';
    }
    
    startFPSCounter() {
        this.fpsInterval = setInterval(() => {
            const now = Date.now();
            const elapsed = now - this.lastFrameTime;
            const fps = Math.round((this.frameCount * 1000) / elapsed);
            
            document.getElementById('fps-counter').textContent = `${fps} FPS`;
            
            this.frameCount = 0;
            this.lastFrameTime = now;
        }, 1000);
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM加载完成，初始化应用...');
    window.app = new SmartVisionApp();
    console.log('应用初始化完成');
});

// 全局函数
function askPresetQuestion(question) {
    console.log('askPresetQuestion:', question);
    if (window.app) {
        document.getElementById('question-input').value = question;
        window.app.askQuestion();
    }
}