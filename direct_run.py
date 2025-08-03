"""
直接运行 Streamlit 应用的脚本
"""
import os
import sys

# 设置工作目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("🚀 直接启动跨境电商智能决策系统")
print(f"📁 工作目录: {os.getcwd()}")

# 检查数据文件
if os.path.exists('data/enhanced_customer_orders.csv'):
    print("✅ 订单数据文件存在")
else:
    print("❌ 订单数据文件不存在")

if os.path.exists('data/enhanced_supplier_data.csv'):
    print("✅ 供应商数据文件存在")
else:
    print("❌ 供应商数据文件不存在")

print("\n🌐 启动应用...")

# 直接导入并运行 Streamlit
try:
    import streamlit.web.bootstrap as bootstrap
    import streamlit.web.cli as stcli
    
    # 设置参数
    sys.argv = [
        'streamlit', 'run', 'app.py',
        '--server.port', '8501',
        '--server.headless', 'false',
        '--browser.gatherUsageStats', 'false'
    ]
    
    print("📍 应用将在 http://localhost:8501 启动")
    print("💡 按 Ctrl+C 停止应用\n")
    
    # 启动应用
    stcli.main()
    
except ImportError as e:
    print(f"❌ 导入错误: {e}")
except Exception as e:
    print(f"❌ 启动错误: {e}")
    import traceback
    traceback.print_exc()
