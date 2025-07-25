"""
简化版 Streamlit 启动脚本
"""
import subprocess
import sys
import os
import time

def check_port(port):
    """检查端口是否被占用"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("🚀 启动跨境电商智能决策系统")
    print(f"📁 工作目录: {os.getcwd()}")
    
    # 检查端口
    port = 8501
    if check_port(port):
        print(f"⚠️  端口 {port} 已被占用，尝试使用端口 8502")
        port = 8502
    
    # 检查数据文件
    required_files = [
        'data/enhanced_customer_orders.csv',
        'data/enhanced_supplier_data.csv'
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file}")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n❌ 缺少必要的数据文件: {missing_files}")
        print("请确保数据文件存在后重试")
        return
    
    print(f"\n🌐 启动 Streamlit 在端口 {port}...")
    print(f"📍 访问地址: http://localhost:{port}")
    print("💡 按 Ctrl+C 停止应用\n")
    
    try:
        # 使用更简单的启动方式
        cmd = [
            sys.executable, '-m', 'streamlit', 'run', 'app.py',
            '--server.port', str(port),
            '--server.address', 'localhost'
        ]
        
        print(f"执行命令: {' '.join(cmd)}")
        
        # 启动进程
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # 实时输出
        for line in process.stdout:
            print(line.strip())
            
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
        if 'process' in locals():
            process.terminate()
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == "__main__":
    main()
