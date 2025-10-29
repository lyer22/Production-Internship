#!/usr/bin/env python3
"""
启动智能视觉分析助手
"""
import os
import sys

def check_api_key():
    """检查API密钥"""
    from config import Config
    
    if Config.DASHSCOPE_API_KEY == 'your-dashscope-api-key-here':
        print("⚠️  警告: 未配置阿里云百炼API密钥")
        print("   请在 config.py 中设置 DASHSCOPE_API_KEY")
        print("   或设置环境变量: export DASHSCOPE_API_KEY='your-key'")
        
        choice = input("\n是否继续启动? (y/n): ")
        if choice.lower() != 'y':
            print("已取消启动")
            sys.exit(0)
        
        print("\n⚠️  将以测试模式运行（AI功能受限）")
    else:
        print("✅ API密钥已配置")
    
    return True

def main():
    print("🚀 智能视觉分析助手启动程序")
    print("=" * 60)
    
    # 检查API密钥
    check_api_key()
    
    print("\n📋 启动选项:")
    print("1. 完整功能模式 (app.py) - 包含YOLO检测和AI问答")
    print("2. 简化测试模式 (app_fixed.py) - 仅视频流和测试AI")
    print("3. 演示模式 (demo.py) - 无需摄像头和API")
    
    choice = input("\n请选择启动模式 (1/2/3，默认1): ").strip() or "1"
    
    if choice == "1":
        print("\n🎯 启动完整功能模式...")
        print("=" * 60)
        from app import app, socketio, initialize_components, start_video_thread
        from config import Config
        
        # 初始化组件
        initialize_components()
        
        # 启动视频流线程
        start_video_thread()
        
        # 创建必要目录
        os.makedirs('static/captures', exist_ok=True)
        
        print(f"🌐 访问地址: http://localhost:{Config.PORT}")
        print("📋 功能:")
        print("   ✅ 实时视频流")
        print("   ✅ YOLO目标检测")
        print("   ✅ AI智能问答")
        print("   ✅ 场景分析")
        print("   ✅ 安全监控")
        print("=" * 60)
        
        socketio.run(
            app,
            host=Config.HOST,
            port=Config.PORT,
            debug=False,
            allow_unsafe_werkzeug=True
        )
        
    elif choice == "2":
        print("\n🎯 启动简化测试模式...")
        os.system("python app_fixed.py")
        
    elif choice == "3":
        print("\n🎯 启动演示模式...")
        os.system("python demo.py")
        
    else:
        print("❌ 无效选择")
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 应用已停止")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)