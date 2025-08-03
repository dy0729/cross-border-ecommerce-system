import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

st.set_page_config(
    page_title="智能订单管理",
    page_icon="📋",
    layout="wide"
)

st.title("📋 智能订单管理系统")
st.markdown("---")

# 地区数据结构
REGIONS_DATA = {
    '东亚': ['中国', '日本', '韩国', '台湾'],
    '欧洲': ['德国', '法国', '英国', '意大利', '西班牙'],
    '东南亚': ['新加坡', '马来西亚', '泰国', '印度尼西亚', '菲律宾', '越南'],
    '南美洲': ['巴西', '阿根廷', '智利', '哥伦比亚', '秘鲁'],
    '北美洲': ['美国', '加拿大', '墨西哥'],
    '中东': ['阿联酋', '沙特阿拉伯', '以色列', '土耳其', '卡塔尔', '科威特']
}

# 销售渠道
SALES_CHANNELS = ['官方网站', 'Amazon', 'eBay', '速卖通', 'Shopify', '独立站', '社交媒体', '线下门店']

# 产品类别
PRODUCT_CATEGORIES = ['电子产品', '服装配饰', '女装系列', '女装配饰', '家居用品', '运动户外', '美妆护肤']

# 生成模拟订单数据
@st.cache_data
def generate_order_data():
    """生成模拟的订单数据"""
    np.random.seed(42)
    
    # 生成日期范围（过去90天）
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    dates = pd.date_range(start=start_date, end=end_date, freq='H')  # 按小时生成
    
    orders = []
    order_id = 100001
    
    for date in dates:
        # 每小时生成0-10个订单
        num_orders = np.random.poisson(3)
        
        for _ in range(num_orders):
            # 随机选择地区
            continent = np.random.choice(list(REGIONS_DATA.keys()))
            country = np.random.choice(REGIONS_DATA[continent])
            
            # 随机选择渠道和产品
            channel = np.random.choice(SALES_CHANNELS)
            product = np.random.choice(PRODUCT_CATEGORIES)
            
            # 生成订单金额（考虑产品类别差异）
            if product in ['电子产品']:
                base_amount = np.random.uniform(200, 1500)
            elif product in ['女装系列', '女装配饰', '服装配饰']:
                base_amount = np.random.uniform(30, 300)
            else:
                base_amount = np.random.uniform(50, 500)
            
            # 考虑地区差异
            if continent in ['北美洲', '欧洲']:
                region_multiplier = np.random.uniform(1.2, 1.8)
            elif continent in ['东亚']:
                region_multiplier = np.random.uniform(0.8, 1.4)
            else:
                region_multiplier = np.random.uniform(0.6, 1.2)
            
            amount = base_amount * region_multiplier
            
            # 生成订单状态
            status_weights = [0.7, 0.15, 0.1, 0.05]  # 已完成、处理中、已取消、退款
            status = np.random.choice(['已完成', '处理中', '已取消', '退款'], p=status_weights)
            
            # 生成支付方式
            payment_method = np.random.choice(['信用卡', 'PayPal', '银行转账', '数字钱包'], 
                                            p=[0.4, 0.3, 0.2, 0.1])
            
            orders.append({
                'order_id': f'ORD{order_id}',
                'order_time': date,
                'continent': continent,
                'country': country,
                'channel': channel,
                'product_category': product,
                'amount': round(amount, 2),
                'status': status,
                'payment_method': payment_method,
                'quantity': np.random.randint(1, 5)
            })
            
            order_id += 1
    
    return pd.DataFrame(orders)

# 订单预测模型
def predict_orders(df, days_ahead=7):
    """基于历史数据预测未来订单"""
    # 按日聚合订单数据
    daily_orders = df.groupby(df['order_time'].dt.date).agg({
        'order_id': 'count',
        'amount': 'sum'
    }).reset_index()
    daily_orders.columns = ['date', 'order_count', 'total_amount']
    
    # 简单的移动平均预测
    recent_orders = daily_orders.tail(14)['order_count'].mean()
    recent_amount = daily_orders.tail(14)['total_amount'].mean()
    
    # 生成预测数据
    future_dates = pd.date_range(
        start=daily_orders['date'].max() + timedelta(days=1),
        periods=days_ahead,
        freq='D'
    )
    
    predictions = []
    for date in future_dates:
        # 添加一些随机波动
        predicted_orders = int(recent_orders * np.random.uniform(0.8, 1.2))
        predicted_amount = recent_amount * np.random.uniform(0.8, 1.2)
        
        predictions.append({
            'date': date,
            'predicted_orders': predicted_orders,
            'predicted_amount': predicted_amount
        })
    
    return pd.DataFrame(predictions)

# 侧边栏控制
st.sidebar.header("📊 订单管理控制台")

# 时间范围选择
time_range = st.sidebar.selectbox(
    "选择时间范围",
    options=["过去7天", "过去30天", "过去90天", "自定义"],
    index=1
)

# 地区筛选
selected_continent = st.sidebar.selectbox(
    "选择地区",
    options=['全部'] + list(REGIONS_DATA.keys()),
    index=0
)

# 渠道筛选
selected_channels = st.sidebar.multiselect(
    "选择销售渠道",
    options=SALES_CHANNELS,
    default=SALES_CHANNELS[:3]
)

# 产品类别筛选
selected_products = st.sidebar.multiselect(
    "选择产品类别",
    options=PRODUCT_CATEGORIES,
    default=PRODUCT_CATEGORIES[:3]
)

# 订单状态筛选
selected_status = st.sidebar.multiselect(
    "选择订单状态",
    options=['已完成', '处理中', '已取消', '退款'],
    default=['已完成', '处理中']
)

# 加载数据
df = generate_order_data()

# 数据筛选
filtered_df = df.copy()

# 时间筛选
if time_range == "过去7天":
    cutoff_date = datetime.now() - timedelta(days=7)
    filtered_df = filtered_df[filtered_df['order_time'] >= cutoff_date]
elif time_range == "过去30天":
    cutoff_date = datetime.now() - timedelta(days=30)
    filtered_df = filtered_df[filtered_df['order_time'] >= cutoff_date]
elif time_range == "过去90天":
    cutoff_date = datetime.now() - timedelta(days=90)
    filtered_df = filtered_df[filtered_df['order_time'] >= cutoff_date]

# 地区筛选
if selected_continent != '全部':
    filtered_df = filtered_df[filtered_df['continent'] == selected_continent]

# 渠道筛选
if selected_channels:
    filtered_df = filtered_df[filtered_df['channel'].isin(selected_channels)]

# 产品筛选
if selected_products:
    filtered_df = filtered_df[filtered_df['product_category'].isin(selected_products)]

# 状态筛选
if selected_status:
    filtered_df = filtered_df[filtered_df['status'].isin(selected_status)]

# 主要内容区域
st.subheader("📊 订单概览")

# 关键指标
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    total_orders = len(filtered_df)
    st.metric("总订单数", f"{total_orders:,}")

with col2:
    total_amount = filtered_df['amount'].sum()
    st.metric("总金额", f"${total_amount:,.2f}")

with col3:
    avg_order_value = filtered_df['amount'].mean() if len(filtered_df) > 0 else 0
    st.metric("平均订单价值", f"${avg_order_value:.2f}")

with col4:
    completion_rate = len(filtered_df[filtered_df['status'] == '已完成']) / len(filtered_df) * 100 if len(filtered_df) > 0 else 0
    st.metric("完成率", f"{completion_rate:.1f}%")

with col5:
    unique_customers = len(filtered_df['country'].unique()) if len(filtered_df) > 0 else 0
    st.metric("覆盖国家", f"{unique_customers}")

# 订单趋势分析
st.subheader("📈 订单趋势分析")

if len(filtered_df) > 0:
    # 按日期聚合
    daily_stats = filtered_df.groupby(filtered_df['order_time'].dt.date).agg({
        'order_id': 'count',
        'amount': 'sum'
    }).reset_index()
    daily_stats.columns = ['date', 'order_count', 'total_amount']
    
    # 创建双轴图表
    fig_trend = go.Figure()

    # 添加订单数量（左轴）
    fig_trend.add_trace(
        go.Scatter(
            x=daily_stats['date'],
            y=daily_stats['order_count'],
            mode='lines+markers',
            name='订单数量',
            line=dict(color='blue'),
            yaxis='y'
        )
    )

    # 添加订单金额（右轴）
    fig_trend.add_trace(
        go.Scatter(
            x=daily_stats['date'],
            y=daily_stats['total_amount'],
            mode='lines+markers',
            name='订单金额',
            line=dict(color='red'),
            yaxis='y2'
        )
    )

    # 设置布局和双轴
    fig_trend.update_layout(
        title="订单数量和金额趋势",
        height=400,
        xaxis=dict(title="日期"),
        yaxis=dict(
            title="订单数量",
            side="left",
            color="blue"
        ),
        yaxis2=dict(
            title="订单金额 ($)",
            side="right",
            overlaying="y",
            color="red"
        ),
        legend=dict(x=0.01, y=0.99)
    )

    st.plotly_chart(fig_trend, use_container_width=True)

# 多维度分析
st.subheader("🔍 多维度分析")

col1, col2 = st.columns(2)

with col1:
    # 地区分析
    if len(filtered_df) > 0:
        region_stats = filtered_df.groupby('continent').agg({
            'order_id': 'count',
            'amount': 'sum'
        }).reset_index()
        region_stats.columns = ['continent', 'order_count', 'total_amount']
        
        fig_region = px.bar(region_stats, x='continent', y='order_count',
                           title='各地区订单分布', labels={'order_count': '订单数量'})
        st.plotly_chart(fig_region, use_container_width=True)

with col2:
    # 渠道分析
    if len(filtered_df) > 0:
        channel_stats = filtered_df.groupby('channel').agg({
            'order_id': 'count',
            'amount': 'sum'
        }).reset_index()
        channel_stats.columns = ['channel', 'order_count', 'total_amount']
        
        fig_channel = px.pie(channel_stats, values='order_count', names='channel',
                            title='销售渠道分布')
        st.plotly_chart(fig_channel, use_container_width=True)

# 产品分析
col1, col2 = st.columns(2)

with col1:
    # 产品类别分析
    if len(filtered_df) > 0:
        product_stats = filtered_df.groupby('product_category').agg({
            'order_id': 'count',
            'amount': 'sum'
        }).reset_index()
        product_stats.columns = ['product_category', 'order_count', 'total_amount']
        
        fig_product = px.bar(product_stats, x='product_category', y='total_amount',
                           title='产品类别销售额', labels={'total_amount': '销售额'})
        fig_product.update_xaxes(tickangle=45)
        st.plotly_chart(fig_product, use_container_width=True)

with col2:
    # 订单状态分析
    if len(filtered_df) > 0:
        status_stats = filtered_df.groupby('status').agg({
            'order_id': 'count'
        }).reset_index()
        status_stats.columns = ['status', 'order_count']
        
        fig_status = px.pie(status_stats, values='order_count', names='status',
                           title='订单状态分布')
        st.plotly_chart(fig_status, use_container_width=True)

# 订单预测
st.subheader("🔮 智能订单预测")

if len(filtered_df) > 0:
    # 生成预测
    predictions = predict_orders(filtered_df, days_ahead=7)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("预测7天订单总数", f"{predictions['predicted_orders'].sum():,.0f}")
        st.metric("预测7天总金额", f"${predictions['predicted_amount'].sum():,.2f}")
    
    with col2:
        st.metric("日均预测订单", f"{predictions['predicted_orders'].mean():.0f}")
        st.metric("日均预测金额", f"${predictions['predicted_amount'].mean():.2f}")
    
    # 预测图表
    fig_prediction = go.Figure()
    
    fig_prediction.add_trace(go.Scatter(
        x=predictions['date'],
        y=predictions['predicted_orders'],
        mode='lines+markers',
        name='预测订单数',
        line=dict(color='green', dash='dash')
    ))
    
    fig_prediction.update_layout(
        title="未来7天订单预测",
        xaxis_title="日期",
        yaxis_title="预测订单数",
        height=400
    )
    
    st.plotly_chart(fig_prediction, use_container_width=True)

# 实时订单监控
st.subheader("⚡ 实时订单监控")

# 模拟实时数据
if st.button("🔄 刷新实时数据"):
    # 生成最近1小时的模拟订单
    recent_orders = []
    current_time = datetime.now()
    
    for i in range(np.random.randint(5, 15)):
        order_time = current_time - timedelta(minutes=np.random.randint(0, 60))
        continent = np.random.choice(list(REGIONS_DATA.keys()))
        country = np.random.choice(REGIONS_DATA[continent])
        channel = np.random.choice(SALES_CHANNELS)
        product = np.random.choice(PRODUCT_CATEGORIES)
        amount = np.random.uniform(50, 500)
        
        recent_orders.append({
            'order_id': f'ORD{np.random.randint(200000, 299999)}',
            'order_time': order_time.strftime('%H:%M:%S'),
            'country': country,
            'channel': channel,
            'product_category': product,
            'amount': f'${amount:.2f}',
            'status': '处理中'
        })
    
    recent_df = pd.DataFrame(recent_orders)
    st.dataframe(recent_df, use_container_width=True)

# 详细订单数据
st.subheader("📋 详细订单数据")

if len(filtered_df) > 0:
    # 显示筛选后的订单数据
    display_df = filtered_df.copy()
    display_df['order_time'] = display_df['order_time'].dt.strftime('%Y-%m-%d %H:%M')
    display_df['amount'] = display_df['amount'].apply(lambda x: f'${x:.2f}')
    
    # 重新排列列的顺序
    column_order = ['order_id', 'order_time', 'country', 'channel', 'product_category', 'amount', 'status', 'payment_method']
    display_df = display_df[column_order]
    
    st.dataframe(display_df, use_container_width=True)
    
    # 导出功能
    csv = display_df.to_csv(index=False)
    st.download_button(
        label="📥 导出订单数据 (CSV)",
        data=csv,
        file_name=f"orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

# 系统对接说明
with st.expander("🔗 系统对接说明"):
    st.markdown("""
    ### 📡 实时对接订单业务系统
    
    #### 支持的对接方式
    - **API接口**: RESTful API实时数据同步
    - **数据库连接**: 直连订单数据库
    - **文件导入**: CSV/Excel批量导入
    - **Webhook**: 实时推送订单事件
    
    #### 对接的业务系统
    - **电商平台**: Amazon, eBay, 速卖通等
    - **ERP系统**: SAP, Oracle, 用友等
    - **CRM系统**: Salesforce, HubSpot等
    - **支付系统**: PayPal, Stripe, 支付宝等
    
    #### 数据同步频率
    - **实时同步**: 订单创建/更新时立即同步
    - **定时同步**: 每5分钟/15分钟/1小时同步
    - **批量同步**: 每日/每周批量处理
    
    #### 技术支持
    - 提供完整的API文档和SDK
    - 专业的技术支持团队
    - 7x24小时系统监控
    """)

# 帮助信息
with st.expander("❓ 使用帮助"):
    st.markdown("""
    ### 📖 功能说明
    
    1. **订单概览**: 查看关键订单指标和统计
    2. **趋势分析**: 分析订单数量和金额的时间趋势
    3. **多维度分析**: 按地区、渠道、产品等维度分析
    4. **智能预测**: 基于机器学习的订单量预测
    5. **实时监控**: 实时查看最新订单动态
    
    ### 🎯 使用建议
    
    - 定期查看订单趋势，识别业务模式
    - 利用多维度分析优化渠道和产品策略
    - 关注预测数据，提前做好库存和人员准备
    - 监控实时订单，及时响应异常情况
    """)
