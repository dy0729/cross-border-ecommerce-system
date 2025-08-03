import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="智能需求预测",
    page_icon="📈",
    layout="wide"
)

st.title("📈 智能需求预测系统")
st.markdown("---")

# 地区数据结构
REGIONS_DATA = {
    '东亚': {
        '中国': ['北京', '上海', '广东', '浙江', '江苏', '山东', '四川', '湖北', '河南', '福建'],
        '日本': ['东京都', '大阪府', '神奈川县', '爱知县', '埼玉县', '千叶县', '兵库县', '北海道'],
        '韩国': ['首尔', '釜山', '仁川', '大邱', '大田', '光州', '蔚山', '世宗'],
        '台湾': ['台北', '新北', '桃园', '台中', '台南', '高雄']
    },
    '欧洲': {
        '德国': ['巴伐利亚州', '北莱茵-威斯特法伦州', '巴登-符腾堡州', '下萨克森州', '黑森州'],
        '法国': ['法兰西岛大区', '奥弗涅-罗纳-阿尔卑斯大区', '新阿基坦大区', '奥克西塔尼大区'],
        '英国': ['英格兰', '苏格兰', '威尔士', '北爱尔兰'],
        '意大利': ['伦巴第大区', '拉齐奥大区', '坎帕尼亚大区', '西西里大区', '威尼托大区'],
        '西班牙': ['马德里自治区', '加泰罗尼亚', '安达卢西亚', '巴伦西亚', '加利西亚']
    },
    '东南亚': {
        '新加坡': ['新加坡'],
        '马来西亚': ['吉隆坡', '雪兰莪', '柔佛', '槟城', '沙巴', '砂拉越'],
        '泰国': ['曼谷', '春武里府', '清迈府', '普吉府', '宋卡府'],
        '印度尼西亚': ['雅加达', '西爪哇省', '东爪哇省', '中爪哇省', '北苏门答腊省'],
        '菲律宾': ['马尼拉大都会', '宿务', '达沃', '卡拉巴松', '中吕宋'],
        '越南': ['胡志明市', '河内', '海防', '岘港', '芹苴']
    },
    '南美洲': {
        '巴西': ['圣保罗州', '里约热内卢州', '米纳斯吉拉斯州', '巴伊亚州', '南里奥格兰德州'],
        '阿根廷': ['布宜诺斯艾利斯省', '科尔多瓦省', '圣菲省', '门多萨省'],
        '智利': ['圣地亚哥首都大区', '瓦尔帕莱索大区', '比奥比奥大区', '阿劳卡尼亚大区'],
        '哥伦比亚': ['安蒂奥基亚省', '库迪纳马卡省', '瓦莱德尔考卡省', '大西洋省'],
        '秘鲁': ['利马大区', '阿雷基帕大区', '拉利伯塔德大区', '皮乌拉大区']
    },
    '北美洲': {
        '美国': ['加利福尼亚州', '德克萨斯州', '佛罗里达州', '纽约州', '宾夕法尼亚州', '伊利诺伊州', '俄亥俄州'],
        '加拿大': ['安大略省', '魁北克省', '不列颠哥伦比亚省', '阿尔伯塔省', '曼尼托巴省'],
        '墨西哥': ['墨西哥城', '哈利斯科州', '新莱昂州', '普埃布拉州', '瓜纳华托州']
    },
    '中东': {
        '阿联酋': ['迪拜', '阿布扎比', '沙迦', '阿治曼'],
        '沙特阿拉伯': ['利雅得省', '麦加省', '东部省', '麦地那省'],
        '以色列': ['特拉维夫区', '耶路撒冷区', '海法区', '中央区'],
        '土耳其': ['伊斯坦布尔省', '安卡拉省', '伊兹密尔省', '布尔萨省'],
        '卡塔尔': ['多哈'],
        '科威特': ['科威特省', '艾哈迈迪省', '法尔瓦尼亚省']
    }
}

# 生成模拟数据
@st.cache_data
def generate_sample_data():
    """生成模拟的历史销售数据"""
    np.random.seed(42)

    # 生成日期范围（过去2年）
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')

    # 产品类别
    products = ['电子产品', '服装配饰', '女装系列', '家居用品', '运动户外', '美妆护肤']
    
    data = []

    # 为每个地区生成数据
    for continent, countries in REGIONS_DATA.items():
        for country, provinces in countries.items():
            for province in provinces:
                for product in products:
                    # 基础趋势（不同地区有不同的基础销量）
                    region_multiplier = np.random.uniform(0.5, 2.0)
                    base_trend = np.linspace(100, 200, len(dates)) * region_multiplier

                    # 季节性模式（北半球和南半球相反）
                    if continent in ['南美洲']:
                        seasonal = 50 * np.sin(2 * np.pi * np.arange(len(dates)) / 365.25 + np.pi)
                    else:
                        seasonal = 50 * np.sin(2 * np.pi * np.arange(len(dates)) / 365.25)

                    # 周期性模式（周末效应）
                    weekly = 20 * np.sin(2 * np.pi * np.arange(len(dates)) / 7)

                    # 随机噪声
                    noise = np.random.normal(0, 15, len(dates))

                    # 特殊事件（促销等）
                    special_events = np.zeros(len(dates))
                    for i in range(0, len(dates), 90):  # 每季度一次促销
                        if i + 7 < len(dates):
                            special_events[i:i+7] = 50 * np.random.uniform(0.5, 1.5)

                    # 合成销量数据
                    sales = base_trend + seasonal + weekly + noise + special_events
                    sales = np.maximum(sales, 10)  # 确保销量不为负

                    for i, date in enumerate(dates):
                        data.append({
                            'date': date,
                            'product': product,
                            'continent': continent,
                            'country': country,
                            'province': province,
                            'sales': int(sales[i]),
                            'revenue': sales[i] * np.random.uniform(20, 100)  # 随机单价
                        })
    
    return pd.DataFrame(data)

# 简单的预测函数（替代Prophet）
def simple_forecast(data, periods=30):
    """简单的时间序列预测"""
    # 计算趋势
    x = np.arange(len(data))
    y = data['sales'].values
    
    # 线性回归拟合趋势
    z = np.polyfit(x, y, 1)
    trend = np.poly1d(z)
    
    # 计算季节性（简化版）
    seasonal_period = min(365, len(data))
    if len(data) >= seasonal_period:
        seasonal = []
        for i in range(seasonal_period):
            seasonal_values = y[i::seasonal_period]
            seasonal.append(np.mean(seasonal_values) - np.mean(y))
        seasonal = np.array(seasonal)
    else:
        seasonal = np.zeros(len(data))
    
    # 生成预测
    future_x = np.arange(len(data), len(data) + periods)
    future_trend = trend(future_x)
    
    # 添加季节性
    future_seasonal = []
    for i in range(periods):
        season_idx = (len(data) + i) % len(seasonal) if len(seasonal) > 0 else 0
        future_seasonal.append(seasonal[season_idx] if len(seasonal) > 0 else 0)
    
    forecast = future_trend + np.array(future_seasonal)
    
    # 生成预测日期
    last_date = data['date'].max()
    future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=periods, freq='D')
    
    return pd.DataFrame({
        'date': future_dates,
        'forecast': np.maximum(forecast, 10)  # 确保预测值不为负
    })

# 加载数据
df = generate_sample_data()

# 侧边栏控制
st.sidebar.header("📊 预测参数设置")

# 地区筛选
st.sidebar.subheader("🌍 地区筛选")

# 大洲选择
selected_continent = st.sidebar.selectbox(
    "选择大洲",
    options=['全部'] + list(REGIONS_DATA.keys()),
    index=0
)

# 国家选择
if selected_continent != '全部':
    available_countries = ['全部'] + list(REGIONS_DATA[selected_continent].keys())
    selected_country = st.sidebar.selectbox(
        "选择国家",
        options=available_countries,
        index=0
    )

    # 省份/州选择
    if selected_country != '全部':
        available_provinces = ['全部'] + REGIONS_DATA[selected_continent][selected_country]
        selected_province = st.sidebar.selectbox(
            "选择省份/州",
            options=available_provinces,
            index=0
        )
    else:
        selected_province = '全部'
else:
    selected_country = '全部'
    selected_province = '全部'

# 产品选择
selected_product = st.sidebar.selectbox(
    "选择产品类别",
    options=df['product'].unique(),
    index=0
)

# 预测天数
forecast_days = st.sidebar.slider(
    "预测天数",
    min_value=7,
    max_value=365,
    value=30,
    step=7
)

# 数据时间范围
date_range = st.sidebar.date_input(
    "选择数据时间范围",
    value=[df['date'].min().date(), df['date'].max().date()],
    min_value=df['date'].min().date(),
    max_value=df['date'].max().date()
)

# 筛选数据
filtered_df = df[df['product'] == selected_product].copy()

# 地区筛选
if selected_continent != '全部':
    filtered_df = filtered_df[filtered_df['continent'] == selected_continent]

if selected_country != '全部':
    filtered_df = filtered_df[filtered_df['country'] == selected_country]

if selected_province != '全部':
    filtered_df = filtered_df[filtered_df['province'] == selected_province]

# 时间范围筛选
if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = filtered_df[
        (filtered_df['date'].dt.date >= start_date) &
        (filtered_df['date'].dt.date <= end_date)
    ]

# 按日期聚合数据（如果有多个地区的数据）
if len(filtered_df) > 0:
    filtered_df = filtered_df.groupby(['date', 'product']).agg({
        'sales': 'sum',
        'revenue': 'sum'
    }).reset_index()

# 按日期聚合数据（如果有多个地区的数据）
if len(filtered_df) > 0:
    filtered_df = filtered_df.groupby(['date', 'product']).agg({
        'sales': 'sum',
        'revenue': 'sum'
    }).reset_index()

# 主要内容区域
col1, col2 = st.columns([2, 1])

with col1:
    # 构建地区显示文本
    region_text = ""
    if selected_continent != '全部':
        region_text = f" - {selected_continent}"
        if selected_country != '全部':
            region_text += f"/{selected_country}"
            if selected_province != '全部':
                region_text += f"/{selected_province}"

    st.subheader(f"📊 {selected_product}{region_text} - 历史销售数据")

    # 历史数据图表
    fig_history = px.line(
        filtered_df,
        x='date',
        y='sales',
        title=f"{selected_product}{region_text} 历史销售趋势",
        labels={'sales': '销量', 'date': '日期'}
    )
    fig_history.update_layout(height=400)
    st.plotly_chart(fig_history, use_container_width=True)

with col2:
    st.subheader("📈 数据统计")
    
    # 基础统计信息
    total_sales = filtered_df['sales'].sum()
    avg_daily_sales = filtered_df['sales'].mean()
    max_sales = filtered_df['sales'].max()
    min_sales = filtered_df['sales'].min()
    
    st.metric("总销量", f"{total_sales:,}")
    st.metric("日均销量", f"{avg_daily_sales:.1f}")
    st.metric("最高日销量", f"{max_sales:,}")
    st.metric("最低日销量", f"{min_sales:,}")

# 预测按钮
if st.button("🔮 开始预测", type="primary"):
    with st.spinner("正在进行智能预测..."):
        # 执行预测
        forecast_df = simple_forecast(filtered_df, forecast_days)
        
        # 存储预测结果到session state
        st.session_state['forecast_result'] = forecast_df
        st.session_state['historical_data'] = filtered_df
        
        st.success(f"✅ 预测完成！已生成未来 {forecast_days} 天的需求预测")

# 显示预测结果
if 'forecast_result' in st.session_state:
    st.markdown("---")
    st.subheader("🔮 预测结果")
    
    forecast_df = st.session_state['forecast_result']
    historical_df = st.session_state['historical_data']
    
    # 预测图表
    fig_forecast = go.Figure()
    
    # 历史数据
    fig_forecast.add_trace(go.Scatter(
        x=historical_df['date'],
        y=historical_df['sales'],
        mode='lines',
        name='历史数据',
        line=dict(color='blue')
    ))
    
    # 预测数据
    fig_forecast.add_trace(go.Scatter(
        x=forecast_df['date'],
        y=forecast_df['forecast'],
        mode='lines',
        name='预测数据',
        line=dict(color='red', dash='dash')
    ))
    
    fig_forecast.update_layout(
        title=f"{selected_product} - 需求预测结果",
        xaxis_title="日期",
        yaxis_title="销量",
        height=500
    )
    
    st.plotly_chart(fig_forecast, use_container_width=True)
    
    # 预测数据表格
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 预测数据详情")
        forecast_display = forecast_df.copy()
        forecast_display['date'] = forecast_display['date'].dt.strftime('%Y-%m-%d')
        forecast_display['forecast'] = forecast_display['forecast'].round(0).astype(int)
        forecast_display.columns = ['日期', '预测销量']
        st.dataframe(forecast_display, use_container_width=True)
    
    with col2:
        st.subheader("📊 预测统计")
        
        total_forecast = forecast_df['forecast'].sum()
        avg_forecast = forecast_df['forecast'].mean()
        max_forecast = forecast_df['forecast'].max()
        min_forecast = forecast_df['forecast'].min()
        
        st.metric("预测总销量", f"{total_forecast:.0f}")
        st.metric("预测日均销量", f"{avg_forecast:.1f}")
        st.metric("预测最高日销量", f"{max_forecast:.0f}")
        st.metric("预测最低日销量", f"{min_forecast:.0f}")
        
        # 与历史数据对比
        historical_avg = historical_df['sales'].mean()
        growth_rate = ((avg_forecast - historical_avg) / historical_avg) * 100
        
        st.metric(
            "预测增长率", 
            f"{growth_rate:+.1f}%",
            delta=f"{growth_rate:.1f}%"
        )

# 数据分析
st.markdown("---")
st.subheader("📊 数据分析")

# 地区分析（如果选择了全部地区）
if selected_continent == '全部':
    st.subheader("🌍 地区销售分析")

    # 按大洲统计
    continent_data = df[df['product'] == selected_product].groupby('continent')['sales'].sum().reset_index()
    continent_data = continent_data.sort_values('sales', ascending=False)

    col1, col2 = st.columns(2)

    with col1:
        fig_continent = px.bar(
            continent_data,
            x='continent',
            y='sales',
            title="各大洲销售量对比",
            labels={'sales': '总销量', 'continent': '大洲'},
            color='sales',
            color_continuous_scale='viridis'
        )
        fig_continent.update_layout(height=400)
        st.plotly_chart(fig_continent, use_container_width=True)

    with col2:
        fig_continent_pie = px.pie(
            continent_data,
            values='sales',
            names='continent',
            title="各大洲销售占比"
        )
        fig_continent_pie.update_layout(height=400)
        st.plotly_chart(fig_continent_pie, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    # 月度销售趋势
    monthly_data = filtered_df.copy()
    monthly_data['month'] = monthly_data['date'].dt.to_period('M')
    monthly_sales = monthly_data.groupby('month')['sales'].sum().reset_index()
    monthly_sales['month'] = monthly_sales['month'].astype(str)
    
    fig_monthly = px.bar(
        monthly_sales,
        x='month',
        y='sales',
        title="月度销售趋势",
        labels={'sales': '销量', 'month': '月份'}
    )
    fig_monthly.update_layout(height=400)
    st.plotly_chart(fig_monthly, use_container_width=True)

with col2:
    # 周度销售模式
    weekly_data = filtered_df.copy()
    weekly_data['weekday'] = weekly_data['date'].dt.day_name()
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekly_avg = weekly_data.groupby('weekday')['sales'].mean().reindex(weekday_order).reset_index()
    
    fig_weekly = px.bar(
        weekly_avg,
        x='weekday',
        y='sales',
        title="周度销售模式",
        labels={'sales': '平均销量', 'weekday': '星期'}
    )
    fig_weekly.update_layout(height=400)
    st.plotly_chart(fig_weekly, use_container_width=True)

# 导出功能
st.markdown("---")
st.subheader("📥 数据导出")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📊 导出历史数据"):
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="下载 CSV 文件",
            data=csv,
            file_name=f"{selected_product}_历史数据.csv",
            mime="text/csv"
        )

with col2:
    if 'forecast_result' in st.session_state:
        if st.button("🔮 导出预测数据"):
            csv = st.session_state['forecast_result'].to_csv(index=False)
            st.download_button(
                label="下载预测 CSV",
                data=csv,
                file_name=f"{selected_product}_预测数据.csv",
                mime="text/csv"
            )

with col3:
    if st.button("📋 生成分析报告"):
        st.info("📄 分析报告生成功能开发中...")

# 帮助信息
with st.expander("❓ 使用帮助"):
    st.markdown("""
    ### 📖 功能说明
    
    1. **产品选择**: 从下拉菜单中选择要分析的产品类别
    2. **时间范围**: 设置历史数据的分析时间范围
    3. **预测天数**: 选择要预测的未来天数（7-365天）
    4. **开始预测**: 点击按钮执行智能预测算法
    
    ### 📊 图表说明
    
    - **历史销售趋势**: 显示选定产品的历史销售数据
    - **预测结果**: 蓝色线为历史数据，红色虚线为预测数据
    - **月度趋势**: 按月汇总的销售数据
    - **周度模式**: 一周内各天的平均销售模式
    
    ### 🔧 技术说明
    
    - 使用时间序列分析方法
    - 考虑趋势、季节性和周期性因素
    - 提供多种评估指标
    - 支持数据导出和报告生成
    """)
