import streamlit as st
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.linear_model import LinearRegression
import numpy as np
import plotly.graph_objects as go
from datetime import timedelta

st.set_page_config(page_title="客户需求预测", layout="wide")

st.title("📈 客户需求预测模块")
st.markdown("---")

# 加载数据
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('data/orders.csv')
        df['order_date'] = pd.to_datetime(df['order_date'])
        return df
    except FileNotFoundError:
        st.error("❌ 数据文件未找到，请确保 data/orders.csv 文件存在")
        return pd.DataFrame()

df_orders = load_data()

if df_orders.empty:
    st.stop()

# 侧边栏筛选
st.sidebar.header("🔍 筛选条件")

# 地区筛选
regions = ['全部'] + sorted(df_orders['region'].unique().tolist())
selected_region = st.sidebar.selectbox("选择地区", regions)

if selected_region != '全部':
    df_orders = df_orders[df_orders['region'] == selected_region]

# 时间筛选
st.sidebar.subheader("⏰ 时间维度筛选")
time_filter_type = st.sidebar.selectbox(
    "选择时间筛选方式",
    ["使用全部历史数据", "自定义日期范围", "最近时间段"]
)

if time_filter_type == "自定义日期范围":
    min_date = df_orders['order_date'].dt.date.min()
    max_date = df_orders['order_date'].dt.date.max()
    
    date_range = st.sidebar.date_input(
        "选择分析时间范围",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        df_orders = df_orders[
            (df_orders['order_date'].dt.date >= start_date) & 
            (df_orders['order_date'].dt.date <= end_date)
        ]

elif time_filter_type == "最近时间段":
    recent_period = st.sidebar.selectbox(
        "选择时间段",
        ["最近30天", "最近60天", "最近90天", "最近6个月", "最近1年"]
    )
    
    period_mapping = {
        "最近30天": 30,
        "最近60天": 60,
        "最近90天": 90,
        "最近6个月": 180,
        "最近1年": 365
    }
    
    days_back = period_mapping[recent_period]
    max_date = df_orders['order_date'].dt.date.max()
    cutoff_date = max_date - timedelta(days=days_back)
    df_orders = df_orders[df_orders['order_date'].dt.date >= cutoff_date]

# 显示筛选后的数据统计
st.sidebar.markdown("---")
st.sidebar.subheader("📊 数据统计")
st.sidebar.metric("订单数量", len(df_orders))
st.sidebar.metric("总销量", df_orders['quantity'].sum())
st.sidebar.metric("数据天数", df_orders['order_date'].dt.date.nunique())

# 产品选择
products = sorted(df_orders['product'].unique().tolist())
selected_product = st.selectbox("🎯 选择要预测的产品", products)

# 筛选产品数据
df_product = df_orders[df_orders['product'] == selected_product].copy()

if df_product.empty:
    st.warning("⚠️ 所选产品在当前筛选条件下没有数据")
    st.stop()

# 按日期聚合数据
df_daily = df_product.groupby('order_date')['quantity'].sum().reset_index()
df_daily = df_daily.sort_values('order_date')

st.subheader(f"历史销售数据: {selected_product}")

# 显示基本统计
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("总销量", df_product['quantity'].sum())
with col2:
    st.metric("平均日销量", f"{df_product['quantity'].sum() / len(df_daily):.1f}")
with col3:
    st.metric("最大日销量", df_daily['quantity'].max())
with col4:
    st.metric("数据天数", len(df_daily))

# 绘制历史销量趋势图
fig_hist = go.Figure()
fig_hist.add_trace(go.Scatter(
    x=df_daily['order_date'], 
    y=df_daily['quantity'], 
    mode='lines+markers', 
    name='历史销量'
))
fig_hist.update_layout(
    title_text=f'{selected_product} - 历史每日销量趋势',
    xaxis_title='日期',
    yaxis_title='销量'
)
st.plotly_chart(fig_hist, use_container_width=True)

# 数据质量评估
if len(df_daily) < 30:
    st.warning("⚠️ 数据点较少（少于30天），预测结果可能不够准确")
elif len(df_daily) < 90:
    st.info("📊 数据量适中，预测结果具有一定参考价值")
else:
    st.success("✅ 数据量充足，预测结果较为可靠")

# 简单预测模型
st.header("2. 线性回归预测模型")

col1, col2 = st.columns(2)
with col1:
    periods_input = st.number_input("预测天数", min_value=1, max_value=365, value=30)

with col2:
    data_days = len(df_daily)
    if data_days < 90:
        suggested_periods = min(30, data_days // 3)
    elif data_days < 180:
        suggested_periods = min(60, data_days // 2)
    else:
        suggested_periods = min(90, data_days // 2)
    
    st.info(f"💡 建议预测天数: {suggested_periods} 天")

if st.button("🚀 开始预测"):
    with st.spinner("模型正在预测中..."):
        # 准备数据
        df_daily['days'] = (df_daily['order_date'] - df_daily['order_date'].min()).dt.days
        
        # 训练线性回归模型
        X = df_daily[['days']].values
        y = df_daily['quantity'].values
        
        model = LinearRegression()
        model.fit(X, y)
        
        # 预测
        last_day = df_daily['days'].max()
        future_days = np.arange(last_day + 1, last_day + 1 + periods_input).reshape(-1, 1)
        future_pred = model.predict(future_days)
        
        # 创建预测结果
        last_date = df_daily['order_date'].max()
        future_dates = [last_date + timedelta(days=i) for i in range(1, periods_input + 1)]
        
        forecast_df = pd.DataFrame({
            'date': future_dates,
            'predicted_quantity': np.maximum(future_pred, 0)  # 确保预测值非负
        })
        
        # 显示预测结果
        st.subheader("📊 预测结果")
        
        # 绘制预测图
        fig = go.Figure()
        
        # 历史数据
        fig.add_trace(go.Scatter(
            x=df_daily['order_date'],
            y=df_daily['quantity'],
            mode='lines+markers',
            name='历史销量',
            line=dict(color='blue')
        ))
        
        # 预测数据
        fig.add_trace(go.Scatter(
            x=forecast_df['date'],
            y=forecast_df['predicted_quantity'],
            mode='lines+markers',
            name='预测销量',
            line=dict(color='red', dash='dash')
        ))
        
        fig.update_layout(
            title_text=f'{selected_product} - 销量预测',
            xaxis_title='日期',
            yaxis_title='销量'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 预测统计
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("预测总销量", f"{forecast_df['predicted_quantity'].sum():.0f}")
        with col2:
            st.metric("预测平均日销量", f"{forecast_df['predicted_quantity'].mean():.1f}")
        with col3:
            st.metric("预测最大日销量", f"{forecast_df['predicted_quantity'].max():.1f}")
        
        # 显示预测数据表
        st.subheader("📋 详细预测数据")
        forecast_display = forecast_df.copy()
        forecast_display['predicted_quantity'] = forecast_display['predicted_quantity'].round(1)
        st.dataframe(forecast_display, use_container_width=True)
        
        # 模型性能评估（使用历史数据）
        st.subheader("📈 模型性能评估")
        
        # 对历史数据进行预测
        hist_pred = model.predict(X)
        mae = mean_absolute_error(y, hist_pred)
        rmse = np.sqrt(mean_squared_error(y, hist_pred))
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("平均绝对误差 (MAE)", f"{mae:.2f}")
        with col2:
            st.metric("均方根误差 (RMSE)", f"{rmse:.2f}")
        
        # 业务建议
        st.subheader("💡 业务建议")
        avg_pred = forecast_df['predicted_quantity'].mean()
        avg_hist = df_daily['quantity'].mean()
        
        if avg_pred > avg_hist * 1.1:
            st.success("📈 预测显示需求上升趋势，建议增加库存备货")
        elif avg_pred < avg_hist * 0.9:
            st.warning("📉 预测显示需求下降趋势，建议控制库存水平")
        else:
            st.info("📊 预测显示需求相对稳定，维持当前库存策略")

st.markdown("---")
st.markdown("💡 **提示**: 这是一个简化的线性回归预测模型，适用于快速趋势分析。对于更复杂的季节性模式，建议使用更高级的时间序列模型。")
