@echo off
cd /d "%~dp0"
echo ☁️ 启动智链云：智能决策系统
echo 📁 工作目录: %CD%
echo.
echo 🌐 启动 Streamlit...
echo 📍 访问地址: http://localhost:8501
echo 💡 按 Ctrl+C 停止应用
echo.

python -m streamlit run app.py --server.port 8501 --server.address localhost

pause
