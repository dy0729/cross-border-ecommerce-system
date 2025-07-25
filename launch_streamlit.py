import os
import sys
import subprocess

# 设置工作目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("🚀 启动跨境电商智能决策系统")
print(f"📁 工作目录: {os.getcwd()}")

# 检查数据文件
data_files = [
    'data/enhanced_customer_orders.csv',
    'data/enhanced_supplier_data.csv'
]

for file in data_files:
    if os.path.exists(file):
        print(f"✅ {file}")
    else:
        print(f"❌ {file} 不存在")

print("\n🌐 启动 Streamlit...")
print("📍 访问地址: http://localhost:8501")
print("💡 按 Ctrl+C 停止应用\n")

# 启动 Streamlit
try:
    # 方法1: 使用 subprocess
    result = subprocess.run([
        sys.executable, '-m', 'streamlit', 'run', 'app.py', 
        '--server.port', '8501',
        '--server.headless', 'true'
    ], check=True)
except subprocess.CalledProcessError as e:
    print(f"❌ Streamlit 启动失败: {e}")
    
    # 方法2: 直接导入并运行
    try:
        print("🔄 尝试直接启动...")
        import streamlit.web.cli as stcli
        sys.argv = ['streamlit', 'run', 'app.py', '--server.port', '8501']
        stcli.main()
    except Exception as e2:
        print(f"❌ 直接启动也失败: {e2}")
except KeyboardInterrupt:
    print("\n👋 应用已停止")
except Exception as e:
    print(f"❌ 未知错误: {e}")
