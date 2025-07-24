import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
import base64
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="数据报告生成器", layout="wide")

st.title("📊 智能数据报告生成器")
st.write("生成完整的跨境电商决策分析报告")

# 加载所有数据
@st.cache_data
def load_all_data():
    try:
        orders_df = pd.read_csv('跨境电商/data/enhanced_customer_orders.csv')
        orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])
        
        suppliers_df = pd.read_csv('跨境电商/data/enhanced_supplier_data.csv')
        
        try:
            crawled_suppliers_df = pd.read_csv('跨境电商/data/crawled_suppliers.csv')
        except FileNotFoundError:
            crawled_suppliers_df = pd.DataFrame()
        
        return orders_df, suppliers_df, crawled_suppliers_df
    except FileNotFoundError as e:
        st.error(f"数据文件加载失败: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

orders_df, suppliers_df, crawled_suppliers_df = load_all_data()

if not orders_df.empty:
    
    st.sidebar.header("📋 报告配置")
    
    # 报告类型选择
    report_type = st.sidebar.selectbox(
        "选择报告类型",
        ["综合分析报告", "产品需求预测报告", "供应商评估报告", "库存优化报告"]
    )
    
    # 选择产品（如果需要）
    if report_type in ["产品需求预测报告", "库存优化报告"]:
        selected_product = st.sidebar.selectbox(
            "选择产品",
            orders_df['product_name'].unique()
        )
    
    # 时间范围选择
    date_range = st.sidebar.date_input(
        "选择分析时间范围",
        value=[orders_df['order_date'].min().date(), orders_df['order_date'].max().date()],
        min_value=orders_df['order_date'].min().date(),
        max_value=orders_df['order_date'].max().date()
    )

    # 地区筛选
    st.sidebar.subheader("🌍 地区筛选")

    # 检查是否有详细地区数据
    has_detailed_location = 'customer_country' in orders_df.columns and 'customer_state' in orders_df.columns

    if has_detailed_location:
        # 大区筛选
        all_regions = ['全部'] + sorted(orders_df['customer_region'].unique().tolist())
        selected_region = st.sidebar.selectbox("选择大区", all_regions, key="report_region")

        # 国家筛选
        if selected_region != '全部':
            available_countries = orders_df[orders_df['customer_region'] == selected_region]['customer_country'].unique()
        else:
            available_countries = orders_df['customer_country'].unique()

        all_countries = ['全部'] + sorted(available_countries.tolist())
        selected_country = st.sidebar.selectbox("选择国家", all_countries, key="report_country")

        # 省份/州筛选
        if selected_country != '全部':
            if selected_region != '全部':
                available_states = orders_df[
                    (orders_df['customer_region'] == selected_region) &
                    (orders_df['customer_country'] == selected_country)
                ]['customer_state'].unique()
            else:
                available_states = orders_df[orders_df['customer_country'] == selected_country]['customer_state'].unique()
        else:
            if selected_region != '全部':
                available_states = orders_df[orders_df['customer_region'] == selected_region]['customer_state'].unique()
            else:
                available_states = orders_df['customer_state'].unique()

        all_states = ['全部'] + sorted(available_states.tolist())
        selected_state = st.sidebar.selectbox("选择省份/州", all_states, key="report_state")
    else:
        # 使用原有的简单地区筛选
        all_regions = ['全部'] + sorted(orders_df['customer_region'].unique().tolist())
        selected_region = st.sidebar.selectbox("选择地区", all_regions, key="report_simple_region")
        selected_country = '全部'
        selected_state = '全部'
    
    # 应用筛选条件
    filtered_orders = orders_df.copy()

    # 时间筛选
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_orders = filtered_orders[
            (filtered_orders['order_date'].dt.date >= start_date) &
            (filtered_orders['order_date'].dt.date <= end_date)
        ]

    # 地区筛选
    if has_detailed_location:
        if selected_region != '全部':
            filtered_orders = filtered_orders[filtered_orders['customer_region'] == selected_region]
        if selected_country != '全部':
            filtered_orders = filtered_orders[filtered_orders['customer_country'] == selected_country]
        if selected_state != '全部':
            filtered_orders = filtered_orders[filtered_orders['customer_state'] == selected_state]
    else:
        if selected_region != '全部':
            filtered_orders = filtered_orders[filtered_orders['customer_region'] == selected_region]

    # 显示筛选信息
    filter_info = []
    if len(date_range) == 2:
        filter_info.append(f"时间: {start_date} 至 {end_date}")
    if selected_region != '全部':
        filter_info.append(f"大区: {selected_region}")
    if selected_country != '全部':
        filter_info.append(f"国家: {selected_country}")
    if selected_state != '全部':
        filter_info.append(f"省份/州: {selected_state}")

    if filter_info:
        st.sidebar.info("筛选条件:\n" + "\n".join([f"• {info}" for info in filter_info]))
        st.sidebar.metric("筛选后订单数", f"{len(filtered_orders):,}")
    
    # 生成报告按钮
    if st.sidebar.button("🚀 生成报告", type="primary"):
        
        if report_type == "综合分析报告":
            st.header("📈 跨境电商综合分析报告")
            
            # 报告基本信息
            st.subheader("📋 报告基本信息")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.info(f"**报告生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            with col2:
                st.info(f"**分析时间范围:** {start_date} 至 {end_date}")
            with col3:
                st.info(f"**数据记录数:** {len(filtered_orders):,} 条")
            
            # 1. 业务概览
            st.subheader("💼 业务概览")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_revenue = filtered_orders['total_amount'].sum()
                st.metric("总收入", f"${total_revenue:,.2f}")
            
            with col2:
                total_orders = len(filtered_orders)
                st.metric("总订单数", f"{total_orders:,}")
            
            with col3:
                avg_order_value = filtered_orders['total_amount'].mean()
                st.metric("平均订单价值", f"${avg_order_value:.2f}")
            
            with col4:
                unique_products = filtered_orders['product_name'].nunique()
                st.metric("产品种类", unique_products)
            
            # 2. 销售趋势分析
            st.subheader("📈 销售趋势分析")
            
            # 按月聚合数据
            monthly_data = filtered_orders.groupby(filtered_orders['order_date'].dt.to_period('M')).agg({
                'total_amount': 'sum',
                'order_id': 'count',
                'quantity': 'sum'
            }).reset_index()
            monthly_data['order_date'] = monthly_data['order_date'].astype(str)
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=monthly_data['order_date'],
                y=monthly_data['total_amount'],
                mode='lines+markers',
                name='月度收入',
                line=dict(color='blue')
            ))
            
            fig.update_layout(
                title="月度销售收入趋势",
                xaxis_title="月份",
                yaxis_title="收入 ($)",
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 3. 产品类别分析
            st.subheader("🏷️ 产品类别分析")
            
            category_analysis = filtered_orders.groupby('product_category').agg({
                'total_amount': 'sum',
                'quantity': 'sum',
                'order_id': 'count'
            }).reset_index()
            category_analysis.columns = ['产品类别', '销售额', '销售数量', '订单数']
            category_analysis = category_analysis.sort_values('销售额', ascending=False)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_pie = px.pie(
                    category_analysis,
                    values='销售额',
                    names='产品类别',
                    title="各类别销售额占比"
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                fig_bar = px.bar(
                    category_analysis,
                    x='产品类别',
                    y='销售数量',
                    title="各类别销售数量"
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            
            # 4. 地区分析
            st.subheader("🌍 客户地区分析")

            if has_detailed_location:
                # 详细地区分析
                col1, col2 = st.columns(2)

                with col1:
                    # 大区分析
                    region_analysis = filtered_orders.groupby('customer_region').agg({
                        'total_amount': 'sum',
                        'order_id': 'count',
                        'customer_country': 'nunique',
                        'customer_state': 'nunique'
                    }).reset_index()
                    region_analysis.columns = ['大区', '销售额', '订单数', '国家数', '省份/州数']
                    region_analysis = region_analysis.sort_values('销售额', ascending=False)

                    fig_region = px.pie(
                        region_analysis,
                        values='销售额',
                        names='大区',
                        title="各大区销售额占比"
                    )
                    st.plotly_chart(fig_region, use_container_width=True)

                with col2:
                    # 国家分析
                    country_analysis = filtered_orders.groupby(['customer_region', 'customer_country']).agg({
                        'total_amount': 'sum',
                        'order_id': 'count'
                    }).reset_index()
                    country_analysis.columns = ['大区', '国家', '销售额', '订单数']
                    country_analysis = country_analysis.sort_values('销售额', ascending=False).head(10)

                    fig_country = px.bar(
                        country_analysis,
                        x='国家',
                        y='销售额',
                        color='大区',
                        title="前10名国家销售额"
                    )
                    fig_country.update_xaxes(tickangle=45)
                    st.plotly_chart(fig_country, use_container_width=True)

                # 详细地区数据表
                st.markdown("**详细地区数据**")

                detailed_region_analysis = filtered_orders.groupby(['customer_region', 'customer_country', 'customer_state']).agg({
                    'total_amount': 'sum',
                    'order_id': 'count',
                    'quantity': 'sum'
                }).reset_index()
                detailed_region_analysis.columns = ['大区', '国家', '省份/州', '销售额', '订单数', '销售数量']
                detailed_region_analysis = detailed_region_analysis.sort_values('销售额', ascending=False)

                st.dataframe(detailed_region_analysis.head(20), use_container_width=True)

            else:
                # 简单地区分析
                region_analysis = filtered_orders.groupby('customer_region').agg({
                    'total_amount': 'sum',
                    'order_id': 'count',
                    'quantity': 'sum'
                }).reset_index()
                region_analysis.columns = ['客户地区', '销售额', '订单数', '销售数量']
                region_analysis = region_analysis.sort_values('销售额', ascending=False)

                st.dataframe(region_analysis, use_container_width=True)
            
            # 5. 供应商概览
            st.subheader("🏭 供应商概览")
            
            if not suppliers_df.empty:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("本地供应商数量", len(suppliers_df))
                
                with col2:
                    if not crawled_suppliers_df.empty:
                        st.metric("爬取供应商数量", len(crawled_suppliers_df))
                    else:
                        st.metric("爬取供应商数量", 0)
                
                with col3:
                    total_suppliers = len(suppliers_df) + (len(crawled_suppliers_df) if not crawled_suppliers_df.empty else 0)
                    st.metric("总供应商数量", total_suppliers)
                
                # 供应商地区分布
                if not suppliers_df.empty:
                    supplier_regions = suppliers_df['所在地区'].value_counts()
                    
                    fig_supplier = px.bar(
                        x=supplier_regions.index,
                        y=supplier_regions.values,
                        title="供应商地区分布",
                        labels={'x': '地区', 'y': '供应商数量'}
                    )
                    st.plotly_chart(fig_supplier, use_container_width=True)
            
            # 6. 关键洞察和建议
            st.subheader("💡 关键洞察和建议")
            
            insights = []
            
            # 最佳销售类别
            best_category = category_analysis.iloc[0]['产品类别']
            best_category_revenue = category_analysis.iloc[0]['销售额']
            insights.append(f"🏆 **最佳销售类别**: {best_category}，销售额达 ${best_category_revenue:,.2f}")
            
            # 最佳销售地区
            if has_detailed_location:
                region_col = '大区'
            else:
                region_col = '客户地区'

            best_region = region_analysis.iloc[0][region_col]
            best_region_revenue = region_analysis.iloc[0]['销售额']
            insights.append(f"🌟 **最佳销售地区**: {best_region}，销售额达 ${best_region_revenue:,.2f}")
            
            # 平均订单价值分析
            if avg_order_value > 50:
                insights.append(f"💰 **高价值订单**: 平均订单价值 ${avg_order_value:.2f}，建议重点维护高价值客户")
            else:
                insights.append(f"📈 **提升机会**: 平均订单价值 ${avg_order_value:.2f}，建议通过套餐销售提升客单价")
            
            # 产品多样性分析
            if unique_products > 20:
                insights.append(f"🎯 **产品丰富**: 共有 {unique_products} 种产品，建议优化产品组合，聚焦核心产品")
            else:
                insights.append(f"🚀 **扩展机会**: 当前有 {unique_products} 种产品，建议扩展产品线以满足更多需求")
            
            for insight in insights:
                st.success(insight)
        
        elif report_type == "产品需求预测报告":
            st.header(f"🔮 {selected_product} - 需求预测报告")
            
            # 筛选产品数据
            product_data = filtered_orders[filtered_orders['product_name'] == selected_product]
            
            if len(product_data) > 0:
                # 基本统计
                st.subheader("📊 产品基本统计")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    total_quantity = product_data['quantity'].sum()
                    st.metric("历史总销量", f"{total_quantity:,}件")
                
                with col2:
                    total_revenue = product_data['total_amount'].sum()
                    st.metric("历史总收入", f"${total_revenue:,.2f}")
                
                with col3:
                    avg_price = product_data['unit_price'].mean()
                    st.metric("平均单价", f"${avg_price:.2f}")
                
                with col4:
                    order_count = len(product_data)
                    st.metric("订单数量", f"{order_count:,}")
                
                # 需求趋势
                st.subheader("📈 历史需求趋势")
                
                daily_demand = product_data.groupby('order_date')['quantity'].sum().reset_index()
                
                fig = px.line(
                    daily_demand,
                    x='order_date',
                    y='quantity',
                    title=f"{selected_product} 日销量趋势"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # 简单预测
                st.subheader("🔮 需求预测")
                
                # 计算基本统计指标
                avg_daily_demand = daily_demand['quantity'].mean()
                demand_std = daily_demand['quantity'].std()
                
                # 未来30天预测
                forecast_days = 30
                future_dates = pd.date_range(
                    start=daily_demand['order_date'].max() + timedelta(days=1),
                    periods=forecast_days,
                    freq='D'
                )
                
                # 简单预测（基于历史平均）
                predicted_demand = [max(0, np.random.normal(avg_daily_demand, demand_std)) for _ in range(forecast_days)]
                
                forecast_df = pd.DataFrame({
                    'date': future_dates,
                    'predicted_quantity': predicted_demand
                })
                
                col1, col2 = st.columns(2)
                
                with col1:
                    total_forecast = sum(predicted_demand)
                    st.metric("未来30天预测需求", f"{total_forecast:.0f}件")
                
                with col2:
                    avg_forecast = np.mean(predicted_demand)
                    st.metric("预测日均需求", f"{avg_forecast:.1f}件")
                
                # 预测图表
                fig_forecast = go.Figure()
                
                # 历史数据
                fig_forecast.add_trace(go.Scatter(
                    x=daily_demand['order_date'],
                    y=daily_demand['quantity'],
                    mode='lines',
                    name='历史需求',
                    line=dict(color='blue')
                ))
                
                # 预测数据
                fig_forecast.add_trace(go.Scatter(
                    x=forecast_df['date'],
                    y=forecast_df['predicted_quantity'],
                    mode='lines',
                    name='预测需求',
                    line=dict(color='red', dash='dash')
                ))
                
                fig_forecast.update_layout(
                    title=f"{selected_product} - 需求预测",
                    xaxis_title="日期",
                    yaxis_title="需求量"
                )
                
                st.plotly_chart(fig_forecast, use_container_width=True)
                
                # 预测建议
                st.subheader("💡 预测建议")
                
                if avg_forecast > avg_daily_demand * 1.2:
                    st.success("📈 预测显示需求将显著增长，建议增加库存备货")
                elif avg_forecast < avg_daily_demand * 0.8:
                    st.warning("📉 预测显示需求可能下降，建议谨慎备货")
                else:
                    st.info("📊 预测显示需求相对稳定，建议保持当前备货水平")
            
            else:
                st.error(f"未找到产品 '{selected_product}' 的数据")

        elif report_type == "供应商评估报告":
            st.header("🏭 供应商评估报告")

            # 报告基本信息
            st.subheader("📋 报告基本信息")
            col1, col2, col3 = st.columns(3)

            with col1:
                st.info(f"**报告生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            with col2:
                st.info(f"**本地供应商数量:** {len(suppliers_df)}")
            with col3:
                crawled_count = len(crawled_suppliers_df) if not crawled_suppliers_df.empty else 0
                st.info(f"**爬取供应商数量:** {crawled_count}")

            # 供应商概览
            st.subheader("📊 供应商数据概览")

            if not suppliers_df.empty:
                # 地区分布
                col1, col2 = st.columns(2)

                with col1:
                    region_dist = suppliers_df['所在地区'].value_counts()
                    fig_region = px.pie(
                        values=region_dist.values,
                        names=region_dist.index,
                        title="供应商地区分布"
                    )
                    st.plotly_chart(fig_region, use_container_width=True)

                with col2:
                    category_dist = suppliers_df['主营产品'].value_counts()
                    fig_category = px.bar(
                        x=category_dist.index,
                        y=category_dist.values,
                        title="供应商产品类别分布",
                        labels={'x': '产品类别', 'y': '供应商数量'}
                    )
                    st.plotly_chart(fig_category, use_container_width=True)

                # 供应商评分分析
                st.subheader("⭐ 供应商评分分析")

                # 清理评分数据
                suppliers_df_clean = suppliers_df.copy()
                suppliers_df_clean['评分_数值'] = pd.to_numeric(suppliers_df_clean['店铺评分'], errors='coerce')

                col1, col2, col3 = st.columns(3)

                with col1:
                    avg_rating = suppliers_df_clean['评分_数值'].mean()
                    st.metric("平均评分", f"{avg_rating:.2f}")

                with col2:
                    high_rating_count = len(suppliers_df_clean[suppliers_df_clean['评分_数值'] >= 4.5])
                    st.metric("高评分供应商 (≥4.5)", high_rating_count)

                with col3:
                    rating_std = suppliers_df_clean['评分_数值'].std()
                    st.metric("评分标准差", f"{rating_std:.2f}")

                # 评分分布图
                fig_rating = px.histogram(
                    suppliers_df_clean,
                    x='评分_数值',
                    nbins=20,
                    title="供应商评分分布",
                    labels={'评分_数值': '评分', 'count': '供应商数量'}
                )
                st.plotly_chart(fig_rating, use_container_width=True)

                # 供应商能力分析
                st.subheader("🏭 供应商能力分析")

                # 清理产能数据
                suppliers_df_clean['产能_数值'] = suppliers_df_clean['月产能'].str.replace('件', '').str.replace(',', '').astype(float)
                suppliers_df_clean['起订量_数值'] = suppliers_df_clean['最小起订量'].str.replace('件', '').str.replace(',', '').astype(float)

                capacity_analysis = suppliers_df_clean.groupby('主营产品').agg({
                    '产能_数值': ['mean', 'max', 'min'],
                    '起订量_数值': ['mean', 'max', 'min']
                }).round(0)

                st.dataframe(capacity_analysis, use_container_width=True)

                # 关键洞察
                st.subheader("💡 关键洞察")

                insights = []

                # 最佳评分类别
                best_category_rating = suppliers_df_clean.groupby('主营产品')['评分_数值'].mean().sort_values(ascending=False)
                best_category = best_category_rating.index[0]
                best_rating = best_category_rating.iloc[0]
                insights.append(f"🏆 **最佳评分类别**: {best_category}，平均评分 {best_rating:.2f}")

                # 产能最强类别
                best_capacity_category = suppliers_df_clean.groupby('主营产品')['产能_数值'].mean().sort_values(ascending=False)
                capacity_category = best_capacity_category.index[0]
                capacity_value = best_capacity_category.iloc[0]
                insights.append(f"🏭 **产能最强类别**: {capacity_category}，平均月产能 {capacity_value:,.0f} 件")

                # 地区优势
                region_rating = suppliers_df_clean.groupby('所在地区')['评分_数值'].mean().sort_values(ascending=False)
                best_region = region_rating.index[0]
                region_avg_rating = region_rating.iloc[0]
                insights.append(f"🌟 **优势地区**: {best_region}，平均评分 {region_avg_rating:.2f}")

                for insight in insights:
                    st.success(insight)

            else:
                st.warning("没有供应商数据可供分析")

        elif report_type == "库存优化报告":
            st.header("📦 库存优化报告")

            # 产品选择和参数设置
            st.subheader("📝 优化参数")

            col1, col2, col3 = st.columns(3)

            with col1:
                service_level = st.slider("目标服务水平 (%)", 85, 99, 95)
            with col2:
                lead_time = st.slider("平均交货周期 (天)", 7, 60, 15)
            with col3:
                holding_cost_rate = st.slider("年持有成本率 (%)", 10, 50, 25) / 100

            # 产品库存分析
            st.subheader("📊 产品库存分析")

            # 计算每个产品的库存指标
            product_inventory = []

            for product in filtered_orders['product_name'].unique()[:10]:  # 分析前10个产品
                product_data = filtered_orders[filtered_orders['product_name'] == product]

                if len(product_data) > 5:
                    # 计算基本统计
                    daily_demand = product_data.groupby('order_date')['quantity'].sum()
                    avg_demand = daily_demand.mean()
                    demand_std = daily_demand.std()
                    avg_price = product_data['unit_price'].mean()

                    # 计算库存指标
                    z_score = stats.norm.ppf(service_level / 100)
                    safety_stock = z_score * demand_std * np.sqrt(lead_time)
                    reorder_point = (avg_demand * lead_time) + safety_stock

                    # EOQ计算
                    annual_demand = avg_demand * 365
                    ordering_cost = 50
                    holding_cost = avg_price * holding_cost_rate

                    if holding_cost > 0:
                        eoq = np.sqrt((2 * annual_demand * ordering_cost) / holding_cost)
                    else:
                        eoq = annual_demand / 12

                    product_inventory.append({
                        '产品名称': product,
                        '平均日需求': round(avg_demand, 1),
                        '需求标准差': round(demand_std, 1),
                        '安全库存': round(safety_stock, 0),
                        '再订货点': round(reorder_point, 0),
                        '经济订货量': round(eoq, 0),
                        '平均单价': round(avg_price, 2),
                        '年需求量': round(annual_demand, 0)
                    })

            if product_inventory:
                inventory_df = pd.DataFrame(product_inventory)
                st.dataframe(inventory_df, use_container_width=True)

                # 库存投资分析
                st.subheader("💰 库存投资分析")

                inventory_df['安全库存投资'] = inventory_df['安全库存'] * inventory_df['平均单价']
                inventory_df['EOQ投资'] = inventory_df['经济订货量'] * inventory_df['平均单价']

                col1, col2, col3 = st.columns(3)

                with col1:
                    total_safety_investment = inventory_df['安全库存投资'].sum()
                    st.metric("总安全库存投资", f"${total_safety_investment:,.2f}")

                with col2:
                    total_eoq_investment = inventory_df['EOQ投资'].sum()
                    st.metric("总EOQ投资", f"${total_eoq_investment:,.2f}")

                with col3:
                    total_annual_demand_value = (inventory_df['年需求量'] * inventory_df['平均单价']).sum()
                    st.metric("年需求总价值", f"${total_annual_demand_value:,.2f}")

                # 库存周转分析
                st.subheader("🔄 库存周转分析")

                inventory_df['库存周转率'] = inventory_df['年需求量'] / (inventory_df['经济订货量'] / 2)
                inventory_df['库存天数'] = 365 / inventory_df['库存周转率']

                fig_turnover = px.bar(
                    inventory_df.head(10),
                    x='产品名称',
                    y='库存周转率',
                    title="产品库存周转率对比",
                    labels={'库存周转率': '周转率 (次/年)'}
                )
                fig_turnover.update_xaxes(tickangle=45)
                st.plotly_chart(fig_turnover, use_container_width=True)

                # 优化建议
                st.subheader("💡 优化建议")

                # 高周转产品
                high_turnover = inventory_df[inventory_df['库存周转率'] > inventory_df['库存周转率'].median()]
                low_turnover = inventory_df[inventory_df['库存周转率'] <= inventory_df['库存周转率'].median()]

                if len(high_turnover) > 0:
                    st.success(f"🚀 **高周转产品** ({len(high_turnover)}个): 建议优先保证库存，减少缺货风险")
                    st.write("高周转产品:", ", ".join(high_turnover['产品名称'].head(5).tolist()))

                if len(low_turnover) > 0:
                    st.warning(f"⚠️ **低周转产品** ({len(low_turnover)}个): 建议控制库存水平，避免资金占用")
                    st.write("低周转产品:", ", ".join(low_turnover['产品名称'].head(5).tolist()))

                # 库存投资建议
                high_investment = inventory_df[inventory_df['安全库存投资'] > inventory_df['安全库存投资'].median()]
                if len(high_investment) > 0:
                    st.info(f"💰 **高投资产品**: 考虑与供应商协商缩短交货周期以降低安全库存需求")

            else:
                st.warning("没有足够的数据进行库存分析")

    # 导出功能
    st.sidebar.markdown("---")
    st.sidebar.subheader("📥 导出报告")
    
    if st.sidebar.button("导出为Excel"):
        # 创建Excel文件
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # 订单数据
            filtered_orders.to_excel(writer, sheet_name='订单数据', index=False)
            
            # 产品分析
            if not filtered_orders.empty:
                product_summary = filtered_orders.groupby('product_name').agg({
                    'quantity': 'sum',
                    'total_amount': 'sum',
                    'order_id': 'count'
                }).reset_index()
                product_summary.columns = ['产品名称', '总销量', '总销售额', '订单数']
                product_summary.to_excel(writer, sheet_name='产品分析', index=False)
            
            # 供应商数据
            if not suppliers_df.empty:
                suppliers_df.to_excel(writer, sheet_name='供应商数据', index=False)
        
        output.seek(0)
        
        # 提供下载链接
        b64 = base64.b64encode(output.read()).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="跨境电商分析报告_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx">点击下载Excel报告</a>'
        st.sidebar.markdown(href, unsafe_allow_html=True)

else:
    st.error("无法加载数据，请检查数据文件是否存在")
