@echo off
cd /d "%~dp0"
echo ☁️ 重启智链云：智能决策系统
echo 📁 工作目录: %CD%
echo.

echo 🧹 清理缓存...
if exist ".streamlit" rmdir /s /q .streamlit
if exist "__pycache__" rmdir /s /q __pycache__
if exist "pages\__pycache__" rmdir /s /q pages\__pycache__

echo.
echo 🌐 启动 Streamlit (清除缓存模式)...
echo 📍 访问地址: http://localhost:8501
echo 💡 按 Ctrl+C 停止应用
echo.

python -m streamlit run app.py --server.runOnSave true --server.port 8501

pause
