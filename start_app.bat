@echo off
echo 🚀 启动跨境电商智能决策系统...
echo 📁 当前目录: %CD%

echo 🔧 检查数据文件...
if exist "data\enhanced_customer_orders.csv" (
    echo ✅ 订单数据文件存在
) else (
    echo ❌ 订单数据文件缺失
)

if exist "data\enhanced_supplier_data.csv" (
    echo ✅ 供应商数据文件存在
) else (
    echo ❌ 供应商数据文件缺失
)

echo.
echo 🌐 启动 Streamlit 应用...
echo 📍 访问地址: http://localhost:8501
echo 💡 按 Ctrl+C 停止应用
echo.

python -m streamlit run app.py --server.port 8501

pause
