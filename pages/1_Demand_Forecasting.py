import streamlit as st
import pandas as pd
from prophet import Prophet
from prophet.plot import plot_plotly, plot_components_plotly
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np
import plotly.graph_objects as go
from datetime import timedelta

st.set_page_config(page_title="客户需求预测", layout="wide")

st.title("📈 客户需求预测模块")

@st.cache_data
def load_data(path):
    """加载并预处理数据"""
    df = pd.read_csv(path)
    df['order_date'] = pd.to_datetime(df['order_date'])
    return df

try:
    # --- 1. 数据加载 ---
    df_orders = load_data('跨境电商/data/enhanced_customer_orders.csv')

    # 添加地区筛选功能
    st.sidebar.header("🌍 地区筛选")

    # 检查是否有详细地区数据
    has_detailed_location = 'customer_country' in df_orders.columns and 'customer_state' in df_orders.columns

    if has_detailed_location:
        # 大区筛选
        all_regions = ['全部'] + sorted(df_orders['customer_region'].unique().tolist())
        selected_region = st.sidebar.selectbox("选择大区", all_regions, key="demand_region")

        # 国家筛选
        if selected_region != '全部':
            available_countries = df_orders[df_orders['customer_region'] == selected_region]['customer_country'].unique()
        else:
            available_countries = df_orders['customer_country'].unique()

        all_countries = ['全部'] + sorted(available_countries.tolist())
        selected_country = st.sidebar.selectbox("选择国家", all_countries, key="demand_country")

        # 省份/州筛选
        if selected_country != '全部':
            if selected_region != '全部':
                available_states = df_orders[
                    (df_orders['customer_region'] == selected_region) &
                    (df_orders['customer_country'] == selected_country)
                ]['customer_state'].unique()
            else:
                available_states = df_orders[df_orders['customer_country'] == selected_country]['customer_state'].unique()
        else:
            if selected_region != '全部':
                available_states = df_orders[df_orders['customer_region'] == selected_region]['customer_state'].unique()
            else:
                available_states = df_orders['customer_state'].unique()

        all_states = ['全部'] + sorted(available_states.tolist())
        selected_state = st.sidebar.selectbox("选择省份/州", all_states, key="demand_state")

        # 应用筛选
        filtered_df = df_orders.copy()
        if selected_region != '全部':
            filtered_df = filtered_df[filtered_df['customer_region'] == selected_region]
        if selected_country != '全部':
            filtered_df = filtered_df[filtered_df['customer_country'] == selected_country]
        if selected_state != '全部':
            filtered_df = filtered_df[filtered_df['customer_state'] == selected_state]

        # 显示筛选信息
        filter_info = []
        if selected_region != '全部':
            filter_info.append(f"大区: {selected_region}")
        if selected_country != '全部':
            filter_info.append(f"国家: {selected_country}")
        if selected_state != '全部':
            filter_info.append(f"省份/州: {selected_state}")

        if filter_info:
            st.sidebar.info("当前筛选:\n" + "\n".join([f"• {info}" for info in filter_info]))
            st.sidebar.metric("筛选后订单数", f"{len(filtered_df):,}")

        df_orders = filtered_df
    else:
        # 使用原有的简单地区筛选
        all_regions = ['全部'] + sorted(df_orders['customer_region'].unique().tolist())
        selected_region = st.sidebar.selectbox("选择地区", all_regions, key="demand_simple_region")

        if selected_region != '全部':
            df_orders = df_orders[df_orders['customer_region'] == selected_region]
            st.sidebar.info(f"当前筛选: {selected_region}")
            st.sidebar.metric("筛选后订单数", f"{len(df_orders):,}")

    st.sidebar.markdown("---")

    # 时间维度筛选
    st.sidebar.subheader("📅 时间维度筛选")

    # 获取数据的日期范围
    min_date = df_orders['order_date'].min().date()
    max_date = df_orders['order_date'].max().date()

    # 时间筛选方式选择
    time_filter_type = st.sidebar.selectbox(
        "选择时间筛选方式",
        ["使用全部历史数据", "自定义日期范围", "最近时间段"],
        key="time_filter_type"
    )

    if time_filter_type == "自定义日期范围":
        # 自定义日期范围
        st.sidebar.markdown("**自定义日期范围**")

        date_range = st.sidebar.date_input(
            "选择分析时间范围",
            value=[min_date, max_date],
            min_value=min_date,
            max_value=max_date,
            key="custom_date_range"
        )

        if len(date_range) == 2:
            start_date, end_date = date_range
            df_orders = df_orders[
                (df_orders['order_date'].dt.date >= start_date) &
                (df_orders['order_date'].dt.date <= end_date)
            ]
            st.sidebar.info(f"时间范围: {start_date} 至 {end_date}")
            st.sidebar.metric("筛选后订单数", f"{len(df_orders):,}")

    elif time_filter_type == "最近时间段":
        # 最近时间段选择
        st.sidebar.markdown("**最近时间段**")

        recent_period = st.sidebar.selectbox(
            "选择最近时间段",
            ["最近30天", "最近60天", "最近90天", "最近6个月", "最近1年"],
            key="recent_period"
        )

        # 计算时间范围
        period_mapping = {
            "最近30天": 30,
            "最近60天": 60,
            "最近90天": 90,
            "最近6个月": 180,
            "最近1年": 365
        }

        days_back = period_mapping[recent_period]
        cutoff_date = max_date - timedelta(days=days_back)

        df_orders = df_orders[df_orders['order_date'].dt.date >= cutoff_date]
        st.sidebar.info(f"时间范围: {cutoff_date} 至 {max_date}")
        st.sidebar.metric("筛选后订单数", f"{len(df_orders):,}")

    else:
        # 使用全部历史数据
        st.sidebar.info(f"使用全部历史数据: {min_date} 至 {max_date}")
        st.sidebar.metric("总订单数", f"{len(df_orders):,}")

    st.sidebar.markdown("---")

    st.header("1. 数据探索")
    product_list = df_orders['product_name'].unique()
    selected_product = st.selectbox("请选择您想预测的产品:", product_list)

    # --- 2. 准备数据并展示 ---
    df_product = df_orders[df_orders['product_name'] == selected_product].copy()

    if len(df_product) == 0:
        st.warning(f"⚠️ 在当前筛选条件下，没有找到产品 '{selected_product}' 的订单数据")
        st.info("💡 请调整时间范围或地区筛选条件")
        st.stop()

    df_prophet = df_product[['order_date', 'quantity']].rename(columns={'order_date': 'ds', 'quantity': 'y'})

    st.subheader(f"历史销售数据: {selected_product}")

    # 显示筛选后的数据统计
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_orders = len(df_product)
        st.metric("订单数量", f"{total_orders:,}")

    with col2:
        total_quantity = df_product['quantity'].sum()
        st.metric("总销量", f"{total_quantity:,}")

    with col3:
        date_range_days = (df_product['order_date'].max() - df_product['order_date'].min()).days + 1
        st.metric("数据天数", f"{date_range_days}")

    with col4:
        avg_daily_sales = total_quantity / date_range_days if date_range_days > 0 else 0
        st.metric("日均销量", f"{avg_daily_sales:.1f}")

    # 时间筛选影响说明
    if time_filter_type != "使用全部历史数据":
        st.info(f"📊 当前使用 {time_filter_type} 的数据进行分析，共 {date_range_days} 天的历史数据")

    # 绘制历史销量趋势图
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Scatter(x=df_prophet['ds'], y=df_prophet['y'], mode='lines+markers', name='历史销量'))
    fig_hist.update_layout(
        title_text=f'{selected_product} - 历史每日销量趋势',
        xaxis_title='日期',
        yaxis_title='销售数量',
        hovermode='x unified'
    )
    st.plotly_chart(fig_hist, use_container_width=True)

    # 添加数据质量检查
    if len(df_prophet) < 30:
        st.warning("⚠️ 数据点较少（少于30天），预测结果可能不够准确")
        st.info("💡 建议扩大时间范围以获得更准确的预测结果")
    elif len(df_prophet) < 90:
        st.info("📊 数据量适中，预测结果具有一定参考价值")
    else:
        st.success("✅ 数据量充足，预测结果较为可靠")


    # --- 3. 模型预测 ---
    st.header("2. 使用Prophet模型进行预测")

    # 预测参数设置
    col1, col2 = st.columns(2)

    with col1:
        periods_input = st.number_input('请输入您想预测的未来天数:', min_value=30, max_value=365, value=90)

    with col2:
        # 基于历史数据长度给出建议
        data_days = len(df_prophet)
        if data_days < 90:
            suggested_periods = min(30, data_days // 3)
            st.info(f"💡 建议预测天数: {suggested_periods} 天\n（基于 {data_days} 天历史数据）")
        elif data_days < 180:
            suggested_periods = min(60, data_days // 2)
            st.info(f"💡 建议预测天数: {suggested_periods} 天\n（基于 {data_days} 天历史数据）")
        else:
            suggested_periods = min(90, data_days // 2)
            st.success(f"✅ 建议预测天数: {suggested_periods} 天\n（基于 {data_days} 天历史数据）")

    # 预测质量说明
    st.markdown("### 📊 预测质量说明")

    quality_info = []

    if time_filter_type == "使用全部历史数据":
        quality_info.append("✅ 使用全部历史数据，预测结果最为可靠")
    elif time_filter_type == "最近时间段":
        quality_info.append("📈 使用最近时间段数据，能更好反映当前趋势")
    else:
        quality_info.append("🎯 使用自定义时间范围，适合特定时期分析")

    if data_days >= 180:
        quality_info.append("✅ 历史数据充足，季节性模式识别准确")
    elif data_days >= 90:
        quality_info.append("📊 历史数据适中，短期预测较为准确")
    else:
        quality_info.append("⚠️ 历史数据较少，预测结果仅供参考")

    for info in quality_info:
        st.write(info)

    if st.button("🚀 开始预测"):
        with st.spinner("模型正在努力预测中..."):
            # 训练模型
            m = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=False,
                seasonality_mode='multiplicative',
                changepoint_prior_scale=0.05
            )
            m.fit(df_prophet)

            # 创建未来日期
            future = m.make_future_dataframe(periods=periods_input)
            
            # 进行预测
            forecast = m.predict(future)

            # --- 4. 结果展示 ---
            st.subheader("预测结果可视化")
            fig_forecast = plot_plotly(m, forecast)
            fig_forecast.update_layout(
                title_text=f'{selected_product} - 未来 {periods_input} 天销量预测',
                xaxis_title='日期',
                yaxis_title='预测销售数量'
            )
            st.plotly_chart(fig_forecast, use_container_width=True)

            st.subheader("预测成分分析")
            fig_components = plot_components_plotly(m, forecast)
            st.plotly_chart(fig_components, use_container_width=True)

            # --- 5. 性能评估 ---
            st.subheader("模型性能评估")
            # 合并实际值和预测值
            performance_df = pd.merge(df_prophet, forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']], on='ds')
            
            # 计算指标
            mae = mean_absolute_error(performance_df['y'], performance_df['yhat'])
            rmse = np.sqrt(mean_squared_error(performance_df['y'], performance_df['yhat']))
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="平均绝对误差 (MAE)", value=f"{mae:.2f}")
                st.info("MAE表示模型预测值与真实值之间平均相差的数量。这个值越小越好。")
            with col2:
                st.metric(label="均方根误差 (RMSE)", value=f"{rmse:.2f}")
                st.info("RMSE对较大的误差给予更高的权重。这个值同样越小越好。")

except FileNotFoundError:
    st.error("错误：未找到`跨境电商/data/customer_orders.csv`文件。请确保数据文件已放置在正确的位置。")
except Exception as e:
    st.error(f"处理数据时发生错误: {e}")
