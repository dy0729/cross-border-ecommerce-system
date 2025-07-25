#!/usr/bin/env python3
"""
跨境电商智能决策系统启动脚本
"""

import os
import sys
import subprocess

def main():
    # 确保在正确的目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print("🚀 启动跨境电商智能决策系统...")
    print(f"📁 工作目录: {os.getcwd()}")
    
    # 检查数据文件
    data_files = [
        'data/enhanced_customer_orders.csv',
        'data/enhanced_supplier_data.csv',
        'data/crawled_suppliers.csv'
    ]
    
    for file in data_files:
        if os.path.exists(file):
            print(f"✅ 数据文件存在: {file}")
        else:
            print(f"❌ 数据文件缺失: {file}")
    
    # 启动 Streamlit
    try:
        cmd = [sys.executable, '-m', 'streamlit', 'run', 'app.py', '--server.port', '8501']
        print(f"🔧 执行命令: {' '.join(cmd)}")
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == "__main__":
    main()
