#!/bin/bash

echo "========================================"
echo "   智链云：智能决策系统启动器"
echo "========================================"
echo

echo "正在检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "错误：未找到Python，请先安装Python 3.8+"
    exit 1
fi

python3 --version

echo
echo "正在检查依赖包..."
python3 -c "import streamlit, pandas, numpy, plotly" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "正在安装依赖包..."
    pip3 install streamlit pandas numpy plotly scikit-learn scipy
fi

echo
echo "正在启动智链云系统..."
echo "系统将在浏览器中自动打开"
echo "访问地址: http://localhost:8501"
echo
echo "按 Ctrl+C 停止服务器"
echo "========================================"

python3 -m streamlit run app.py --server.port 8501
