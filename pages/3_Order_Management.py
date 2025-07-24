import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="订单管理系统", layout="wide")

st.title("📦 智能订单管理系统")
st.write("实时订单系统 | 订单量预测 | 备货建议")

# 加载数据
@st.cache_data
def load_order_data():
    try:
        df = pd.read_csv('跨境电商/data/enhanced_customer_orders.csv')
        df['order_date'] = pd.to_datetime(df['order_date'])
        return df
    except FileNotFoundError:
        st.error("未找到增强订单数据文件，请先运行数据生成器")
        return pd.DataFrame()

df = load_order_data()

if not df.empty:
    # 侧边栏控制
    st.sidebar.header("🎛️ 控制面板")

    # 地区筛选功能
    st.sidebar.subheader("🌍 地区筛选")

    # 检查是否有详细地区数据
    has_detailed_location = 'customer_country' in df.columns and 'customer_state' in df.columns

    if has_detailed_location:
        # 大区筛选
        all_regions = ['全部'] + sorted(df['customer_region'].unique().tolist())
        selected_region = st.sidebar.selectbox("选择大区", all_regions)

        # 根据大区筛选数据
        if selected_region != '全部':
            region_filtered_df = df[df['customer_region'] == selected_region]
        else:
            region_filtered_df = df

        # 国家筛选
        all_countries = ['全部'] + sorted(region_filtered_df['customer_country'].unique().tolist())
        selected_country = st.sidebar.selectbox("选择国家", all_countries)

        # 根据国家筛选数据
        if selected_country != '全部':
            country_filtered_df = region_filtered_df[region_filtered_df['customer_country'] == selected_country]
        else:
            country_filtered_df = region_filtered_df

        # 省份/州筛选
        all_states = ['全部'] + sorted(country_filtered_df['customer_state'].unique().tolist())
        selected_state = st.sidebar.selectbox("选择省份/州", all_states)

        # 最终筛选结果
        if selected_state != '全部':
            filtered_df = country_filtered_df[country_filtered_df['customer_state'] == selected_state]
        else:
            filtered_df = country_filtered_df

        # 显示筛选信息
        if selected_region != '全部' or selected_country != '全部' or selected_state != '全部':
            filter_info = []
            if selected_region != '全部':
                filter_info.append(f"大区: {selected_region}")
            if selected_country != '全部':
                filter_info.append(f"国家: {selected_country}")
            if selected_state != '全部':
                filter_info.append(f"省份/州: {selected_state}")

            st.sidebar.info(f"当前筛选: {' | '.join(filter_info)}")
            st.sidebar.metric("筛选后订单数", f"{len(filtered_df):,}")
    else:
        # 使用原有的简单地区筛选
        all_regions = ['全部'] + sorted(df['customer_region'].unique().tolist())
        selected_region = st.sidebar.selectbox("选择地区", all_regions)

        if selected_region != '全部':
            filtered_df = df[df['customer_region'] == selected_region]
            st.sidebar.info(f"当前筛选: {selected_region}")
            st.sidebar.metric("筛选后订单数", f"{len(filtered_df):,}")
        else:
            filtered_df = df

    # 使用筛选后的数据
    df = filtered_df

    st.sidebar.markdown("---")

    # 选择功能模块
    module = st.sidebar.selectbox(
        "选择功能模块",
        ["订单数据概览", "订单详情查看", "订单量预测", "产品需求分析", "备货建议", "地区分析详情"]
    )
    
    if module == "订单数据概览":
        st.header("📊 订单数据概览")
        
        # 基本统计
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_orders = len(df)
            st.metric("总订单数", f"{total_orders:,}")
        
        with col2:
            total_revenue = df['total_amount'].sum()
            st.metric("总收入", f"${total_revenue:,.2f}")
        
        with col3:
            avg_order_value = df['total_amount'].mean()
            st.metric("平均订单价值", f"${avg_order_value:.2f}")
        
        with col4:
            unique_products = df['product_name'].nunique()
            st.metric("产品种类", unique_products)
        
        # 时间序列图
        st.subheader("📈 订单趋势分析")
        
        # 按日期聚合订单数据
        daily_orders = df.groupby('order_date').agg({
            'order_id': 'count',
            'quantity': 'sum',
            'total_amount': 'sum'
        }).reset_index()
        daily_orders.columns = ['日期', '订单数', '销售数量', '销售额']
        
        # 创建多指标图表
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=daily_orders['日期'],
            y=daily_orders['订单数'],
            mode='lines',
            name='每日订单数',
            line=dict(color='blue')
        ))
        
        fig.add_trace(go.Scatter(
            x=daily_orders['日期'],
            y=daily_orders['销售数量'],
            mode='lines',
            name='每日销售数量',
            yaxis='y2',
            line=dict(color='green')
        ))
        
        fig.update_layout(
            title="订单数量与销售数量趋势",
            xaxis_title="日期",
            yaxis=dict(title="订单数", side="left"),
            yaxis2=dict(title="销售数量", side="right", overlaying="y"),
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 产品类别分析
        st.subheader("🏷️ 产品类别分析")
        
        col1, col2 = st.columns(2)
        
        with col1:
            category_sales = df.groupby('product_category')['total_amount'].sum().sort_values(ascending=False)
            fig_pie = px.pie(
                values=category_sales.values,
                names=category_sales.index,
                title="各类别销售额占比"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            category_orders = df.groupby('product_category')['order_id'].count().sort_values(ascending=False)
            fig_bar = px.bar(
                x=category_orders.index,
                y=category_orders.values,
                title="各类别订单数量",
                labels={'x': '产品类别', 'y': '订单数量'}
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # 地区分析
        st.subheader("🌍 客户地区分析")
        
        region_analysis = df.groupby('customer_region').agg({
            'order_id': 'count',
            'total_amount': 'sum',
            'quantity': 'sum'
        }).reset_index()
        region_analysis.columns = ['客户地区', '订单数', '销售额', '销售数量']
        
        st.dataframe(region_analysis, use_container_width=True)

    elif module == "订单详情查看":
        st.header("📋 订单详情查看")
        st.write("根据日期和商品品类筛选查看具体订单信息")

        # 筛选控件
        st.subheader("🔍 订单筛选条件")

        col1, col2, col3 = st.columns(3)

        with col1:
            # 日期范围筛选
            st.markdown("**📅 日期范围**")
            date_range = st.date_input(
                "选择日期范围",
                value=[df['order_date'].min().date(), df['order_date'].max().date()],
                min_value=df['order_date'].min().date(),
                max_value=df['order_date'].max().date(),
                key="order_detail_date"
            )

        with col2:
            # 商品品类筛选
            st.markdown("**🏷️ 商品品类**")
            all_categories = ['全部'] + sorted(df['product_category'].unique().tolist())
            selected_category = st.selectbox(
                "选择商品品类",
                all_categories,
                key="order_detail_category"
            )

        with col3:
            # 订单状态筛选
            st.markdown("**📦 订单状态**")
            all_status = ['全部'] + sorted(df['order_status'].unique().tolist())
            selected_status = st.selectbox(
                "选择订单状态",
                all_status,
                key="order_detail_status"
            )

        # 应用筛选条件
        filtered_orders = df.copy()

        # 日期筛选
        if len(date_range) == 2:
            start_date, end_date = date_range
            filtered_orders = filtered_orders[
                (filtered_orders['order_date'].dt.date >= start_date) &
                (filtered_orders['order_date'].dt.date <= end_date)
            ]

        # 品类筛选
        if selected_category != '全部':
            filtered_orders = filtered_orders[filtered_orders['product_category'] == selected_category]

        # 状态筛选
        if selected_status != '全部':
            filtered_orders = filtered_orders[filtered_orders['order_status'] == selected_status]

        # 显示筛选结果统计
        st.subheader("📊 筛选结果统计")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("筛选订单数", f"{len(filtered_orders):,}")

        with col2:
            total_amount = filtered_orders['total_amount'].sum()
            st.metric("总金额", f"${total_amount:,.2f}")

        with col3:
            total_quantity = filtered_orders['quantity'].sum()
            st.metric("总数量", f"{total_quantity:,}")

        with col4:
            avg_order_value = filtered_orders['total_amount'].mean() if len(filtered_orders) > 0 else 0
            st.metric("平均订单价值", f"${avg_order_value:.2f}")

        # 详细订单列表
        if len(filtered_orders) > 0:
            st.subheader("📋 订单详细列表")

            # 排序选项
            col1, col2 = st.columns(2)

            with col1:
                sort_by = st.selectbox(
                    "排序方式",
                    ["订单日期", "订单金额", "商品数量", "订单ID"],
                    key="order_sort"
                )

            with col2:
                sort_order = st.selectbox(
                    "排序顺序",
                    ["降序", "升序"],
                    key="order_sort_order"
                )

            # 应用排序
            sort_mapping = {
                "订单日期": "order_date",
                "订单金额": "total_amount",
                "商品数量": "quantity",
                "订单ID": "order_id"
            }

            sort_column = sort_mapping[sort_by]
            ascending = sort_order == "升序"

            sorted_orders = filtered_orders.sort_values(sort_column, ascending=ascending)

            # 分页显示
            st.markdown("**📄 分页显示**")

            # 每页显示数量
            page_size = st.selectbox("每页显示订单数", [10, 20, 50, 100], index=1)

            # 计算总页数
            total_pages = (len(sorted_orders) - 1) // page_size + 1

            if total_pages > 1:
                page_number = st.number_input(
                    f"页码 (共 {total_pages} 页)",
                    min_value=1,
                    max_value=total_pages,
                    value=1,
                    key="order_page"
                )
            else:
                page_number = 1

            # 获取当前页数据
            start_idx = (page_number - 1) * page_size
            end_idx = start_idx + page_size
            current_page_orders = sorted_orders.iloc[start_idx:end_idx]

            # 显示订单表格
            display_columns = [
                'order_id', 'order_date', 'product_name', 'product_category',
                'quantity', 'unit_price', 'total_amount', 'customer_region',
                'sales_channel', 'order_status'
            ]

            # 确保所有列都存在
            available_columns = [col for col in display_columns if col in current_page_orders.columns]

            if available_columns:
                # 格式化显示
                display_df = current_page_orders[available_columns].copy()

                # 重命名列为中文
                column_names = {
                    'order_id': '订单ID',
                    'order_date': '订单日期',
                    'product_name': '商品名称',
                    'product_category': '商品品类',
                    'quantity': '数量',
                    'unit_price': '单价($)',
                    'total_amount': '总金额($)',
                    'customer_region': '客户地区',
                    'sales_channel': '销售渠道',
                    'order_status': '订单状态'
                }

                display_df = display_df.rename(columns=column_names)

                # 格式化日期和金额
                if '订单日期' in display_df.columns:
                    display_df['订单日期'] = display_df['订单日期'].dt.strftime('%Y-%m-%d')

                if '单价($)' in display_df.columns:
                    display_df['单价($)'] = display_df['单价($)'].round(2)

                if '总金额($)' in display_df.columns:
                    display_df['总金额($)'] = display_df['总金额($)'].round(2)

                st.dataframe(display_df, use_container_width=True)

                # 显示分页信息
                if total_pages > 1:
                    st.info(f"显示第 {page_number} 页，共 {total_pages} 页 | 当前页显示 {len(current_page_orders)} 条订单，总共 {len(sorted_orders)} 条订单")

            # 订单详情分析
            st.subheader("📈 筛选订单分析")

            col1, col2 = st.columns(2)

            with col1:
                # 按日期统计
                daily_stats = filtered_orders.groupby(filtered_orders['order_date'].dt.date).agg({
                    'order_id': 'count',
                    'total_amount': 'sum'
                }).reset_index()
                daily_stats.columns = ['日期', '订单数', '销售额']

                fig_daily = px.line(
                    daily_stats,
                    x='日期',
                    y='订单数',
                    title="每日订单数量趋势",
                    markers=True
                )
                st.plotly_chart(fig_daily, use_container_width=True)

            with col2:
                # 按商品统计
                product_stats = filtered_orders.groupby('product_name').agg({
                    'quantity': 'sum',
                    'total_amount': 'sum'
                }).reset_index()
                product_stats = product_stats.sort_values('total_amount', ascending=False).head(10)
                product_stats.columns = ['商品名称', '销售数量', '销售额']

                fig_product = px.bar(
                    product_stats,
                    x='商品名称',
                    y='销售额',
                    title="热销商品TOP10",
                    labels={'销售额': '销售额 ($)'}
                )
                fig_product.update_xaxes(tickangle=45)
                st.plotly_chart(fig_product, use_container_width=True)

            # 导出功能
            st.subheader("📥 数据导出")

            if st.button("导出筛选订单数据", key="export_filtered_orders"):
                # 准备导出数据
                export_df = filtered_orders[available_columns].copy()
                export_df = export_df.rename(columns=column_names)

                # 格式化日期
                if '订单日期' in export_df.columns:
                    export_df['订单日期'] = export_df['订单日期'].dt.strftime('%Y-%m-%d')

                # 转换为CSV
                csv = export_df.to_csv(index=False, encoding='utf-8-sig')

                # 提供下载
                st.download_button(
                    label="下载CSV文件",
                    data=csv,
                    file_name=f"筛选订单数据_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    key="download_filtered_orders"
                )

                st.success(f"✅ 准备导出 {len(filtered_orders)} 条订单数据")

        else:
            st.warning("😔 没有找到符合筛选条件的订单")
            st.info("💡 请调整筛选条件，如扩大日期范围或选择不同的商品品类")

    elif module == "订单量预测":
        st.header("🔮 订单量预测")
        
        # 选择产品
        selected_product = st.selectbox(
            "选择要预测的产品",
            df['product_name'].unique()
        )
        
        # 选择预测天数
        forecast_days = st.slider("预测天数", 7, 90, 30)
        
        if st.button("开始预测", type="primary"):
            # 筛选产品数据
            product_df = df[df['product_name'] == selected_product].copy()
            
            if len(product_df) > 10:  # 确保有足够的数据
                # 按日期聚合
                daily_data = product_df.groupby('order_date').agg({
                    'quantity': 'sum',
                    'order_id': 'count'
                }).reset_index()
                daily_data.columns = ['date', 'quantity', 'orders']
                
                # 创建特征
                daily_data['day_of_week'] = daily_data['date'].dt.dayofweek
                daily_data['month'] = daily_data['date'].dt.month
                daily_data['day_of_year'] = daily_data['date'].dt.dayofyear
                daily_data['days_since_start'] = (daily_data['date'] - daily_data['date'].min()).dt.days
                
                # 准备训练数据
                feature_cols = ['day_of_week', 'month', 'day_of_year', 'days_since_start']
                X = daily_data[feature_cols]
                y_quantity = daily_data['quantity']
                y_orders = daily_data['orders']
                
                # 训练模型
                model_quantity = RandomForestRegressor(n_estimators=100, random_state=42)
                model_orders = RandomForestRegressor(n_estimators=100, random_state=42)
                
                model_quantity.fit(X, y_quantity)
                model_orders.fit(X, y_orders)
                
                # 生成未来日期
                last_date = daily_data['date'].max()
                future_dates = pd.date_range(
                    start=last_date + timedelta(days=1),
                    periods=forecast_days,
                    freq='D'
                )
                
                # 创建未来特征
                future_features = pd.DataFrame({
                    'day_of_week': future_dates.dayofweek,
                    'month': future_dates.month,
                    'day_of_year': future_dates.dayofyear,
                    'days_since_start': (future_dates - daily_data['date'].min()).days
                })
                
                # 预测
                pred_quantity = model_quantity.predict(future_features)
                pred_orders = model_orders.predict(future_features)
                
                # 确保预测值为正数
                pred_quantity = np.maximum(pred_quantity, 0)
                pred_orders = np.maximum(pred_orders, 0)
                
                # 创建预测结果DataFrame
                forecast_df = pd.DataFrame({
                    'date': future_dates,
                    'predicted_quantity': pred_quantity,
                    'predicted_orders': pred_orders
                })
                
                # 显示预测结果
                col1, col2 = st.columns(2)
                
                with col1:
                    total_pred_quantity = pred_quantity.sum()
                    st.metric(
                        f"未来{forecast_days}天预测销量",
                        f"{total_pred_quantity:.0f}件"
                    )
                
                with col2:
                    total_pred_orders = pred_orders.sum()
                    st.metric(
                        f"未来{forecast_days}天预测订单数",
                        f"{total_pred_orders:.0f}单"
                    )
                
                # 绘制预测图表
                fig = go.Figure()
                
                # 历史数据
                fig.add_trace(go.Scatter(
                    x=daily_data['date'],
                    y=daily_data['quantity'],
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
                    title=f"{selected_product} - 销量预测",
                    xaxis_title="日期",
                    yaxis_title="销量",
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # 显示详细预测数据
                st.subheader("📋 详细预测数据")
                forecast_display = forecast_df.copy()
                forecast_display['date'] = forecast_display['date'].dt.strftime('%Y-%m-%d')
                forecast_display['predicted_quantity'] = forecast_display['predicted_quantity'].round(0).astype(int)
                forecast_display['predicted_orders'] = forecast_display['predicted_orders'].round(0).astype(int)
                forecast_display.columns = ['日期', '预测销量', '预测订单数']
                
                st.dataframe(forecast_display, use_container_width=True)
                
            else:
                st.warning(f"产品 '{selected_product}' 的历史数据不足，无法进行预测")
    
    elif module == "产品需求分析":
        st.header("📈 产品需求分析")
        
        # 选择分析维度
        analysis_type = st.selectbox(
            "选择分析维度",
            ["产品排行榜", "季节性分析", "地区偏好分析", "渠道分析"]
        )
        
        if analysis_type == "产品排行榜":
            st.subheader("🏆 产品销售排行榜")
            
            # 计算产品排名
            product_ranking = df.groupby('product_name').agg({
                'quantity': 'sum',
                'total_amount': 'sum',
                'order_id': 'count'
            }).reset_index()
            product_ranking.columns = ['产品名称', '总销量', '总销售额', '订单数']
            product_ranking = product_ranking.sort_values('总销售额', ascending=False)
            
            # 显示前20名
            top_products = product_ranking.head(20)
            
            fig = px.bar(
                top_products,
                x='产品名称',
                y='总销售额',
                title="产品销售额排行榜 (前20名)",
                labels={'总销售额': '销售额 ($)'}
            )
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(product_ranking, use_container_width=True)
        
        elif analysis_type == "季节性分析":
            st.subheader("🌸 季节性需求分析")
            
            # 添加月份信息
            df_seasonal = df.copy()
            df_seasonal['month'] = df_seasonal['order_date'].dt.month
            df_seasonal['month_name'] = df_seasonal['order_date'].dt.strftime('%m月')
            
            # 按月份和产品类别分析
            monthly_category = df_seasonal.groupby(['month_name', 'product_category'])['quantity'].sum().reset_index()
            
            fig = px.bar(
                monthly_category,
                x='month_name',
                y='quantity',
                color='product_category',
                title="各类别产品月度销量分布",
                labels={'quantity': '销量', 'month_name': '月份'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # 热力图
            pivot_data = monthly_category.pivot(index='product_category', columns='month_name', values='quantity')
            
            fig_heatmap = px.imshow(
                pivot_data,
                title="产品类别季节性热力图",
                labels=dict(x="月份", y="产品类别", color="销量")
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)

        elif analysis_type == "地区偏好分析":
            st.subheader("🌍 地区偏好分析")

            # 按地区和产品类别分析
            region_category = df.groupby(['customer_region', 'product_category']).agg({
                'quantity': 'sum',
                'total_amount': 'sum',
                'order_id': 'count'
            }).reset_index()
            region_category.columns = ['客户地区', '产品类别', '销量', '销售额', '订单数']

            # 地区销售额分布
            region_sales = df.groupby('customer_region')['total_amount'].sum().sort_values(ascending=False)

            col1, col2 = st.columns(2)

            with col1:
                fig_region = px.pie(
                    values=region_sales.values,
                    names=region_sales.index,
                    title="各地区销售额占比"
                )
                st.plotly_chart(fig_region, use_container_width=True)

            with col2:
                # 地区产品偏好热力图
                region_pivot = region_category.pivot(
                    index='客户地区',
                    columns='产品类别',
                    values='销量'
                ).fillna(0)

                fig_region_heatmap = px.imshow(
                    region_pivot,
                    title="地区产品偏好热力图",
                    labels=dict(x="产品类别", y="客户地区", color="销量")
                )
                st.plotly_chart(fig_region_heatmap, use_container_width=True)

            # 详细数据表
            st.subheader("📊 地区偏好详细数据")
            st.dataframe(region_category, use_container_width=True)

        elif analysis_type == "渠道分析":
            st.subheader("📱 销售渠道分析")

            # 按渠道分析
            channel_analysis = df.groupby('sales_channel').agg({
                'quantity': 'sum',
                'total_amount': 'sum',
                'order_id': 'count',
                'unit_price': 'mean'
            }).reset_index()
            channel_analysis.columns = ['销售渠道', '总销量', '总销售额', '订单数', '平均单价']
            channel_analysis = channel_analysis.sort_values('总销售额', ascending=False)

            col1, col2 = st.columns(2)

            with col1:
                # 渠道销售额对比
                fig_channel_sales = px.bar(
                    channel_analysis,
                    x='销售渠道',
                    y='总销售额',
                    title="各渠道销售额对比",
                    labels={'总销售额': '销售额 ($)'}
                )
                st.plotly_chart(fig_channel_sales, use_container_width=True)

            with col2:
                # 渠道订单数对比
                fig_channel_orders = px.bar(
                    channel_analysis,
                    x='销售渠道',
                    y='订单数',
                    title="各渠道订单数对比",
                    color='订单数',
                    color_continuous_scale='viridis'
                )
                st.plotly_chart(fig_channel_orders, use_container_width=True)

            # 渠道效率分析
            st.subheader("📈 渠道效率分析")

            # 计算渠道效率指标
            channel_analysis['平均订单价值'] = channel_analysis['总销售额'] / channel_analysis['订单数']
            channel_analysis['单位销量价值'] = channel_analysis['总销售额'] / channel_analysis['总销量']

            # 显示渠道效率
            efficiency_metrics = channel_analysis[['销售渠道', '平均订单价值', '单位销量价值', '平均单价']].copy()
            efficiency_metrics['平均订单价值'] = efficiency_metrics['平均订单价值'].round(2)
            efficiency_metrics['单位销量价值'] = efficiency_metrics['单位销量价值'].round(2)
            efficiency_metrics['平均单价'] = efficiency_metrics['平均单价'].round(2)

            st.dataframe(efficiency_metrics, use_container_width=True)

            # 渠道产品偏好
            st.subheader("🎯 渠道产品偏好")

            channel_product = df.groupby(['sales_channel', 'product_category'])['quantity'].sum().reset_index()

            fig_channel_product = px.bar(
                channel_product,
                x='sales_channel',
                y='quantity',
                color='product_category',
                title="各渠道产品类别销量分布",
                labels={'quantity': '销量', 'sales_channel': '销售渠道'}
            )
            st.plotly_chart(fig_channel_product, use_container_width=True)

    elif module == "地区分析详情":
        st.header("🌍 地区分析详情")

        if has_detailed_location:
            # 地区层级分析
            st.subheader("📊 地区层级数据概览")

            col1, col2, col3 = st.columns(3)

            with col1:
                region_count = df['customer_region'].nunique()
                st.metric("大区数量", region_count)

            with col2:
                country_count = df['customer_country'].nunique()
                st.metric("国家数量", country_count)

            with col3:
                state_count = df['customer_state'].nunique()
                st.metric("省份/州数量", state_count)

            # 大区销售分析
            st.subheader("🌎 大区销售分析")

            region_analysis = df.groupby('customer_region').agg({
                'total_amount': 'sum',
                'order_id': 'count',
                'quantity': 'sum',
                'customer_country': 'nunique',
                'customer_state': 'nunique'
            }).reset_index()
            region_analysis.columns = ['大区', '销售额', '订单数', '销售数量', '国家数', '省份/州数']
            region_analysis = region_analysis.sort_values('销售额', ascending=False)

            col1, col2 = st.columns(2)

            with col1:
                fig_region_sales = px.pie(
                    region_analysis,
                    values='销售额',
                    names='大区',
                    title="各大区销售额占比"
                )
                st.plotly_chart(fig_region_sales, use_container_width=True)

            with col2:
                fig_region_orders = px.bar(
                    region_analysis,
                    x='大区',
                    y='订单数',
                    title="各大区订单数量",
                    color='订单数',
                    color_continuous_scale='viridis'
                )
                st.plotly_chart(fig_region_orders, use_container_width=True)

            st.dataframe(region_analysis, use_container_width=True)

            # 国家销售分析
            st.subheader("🏳️ 国家销售分析")

            country_analysis = df.groupby(['customer_region', 'customer_country']).agg({
                'total_amount': 'sum',
                'order_id': 'count',
                'quantity': 'sum',
                'customer_state': 'nunique'
            }).reset_index()
            country_analysis.columns = ['大区', '国家', '销售额', '订单数', '销售数量', '省份/州数']
            country_analysis = country_analysis.sort_values('销售额', ascending=False)

            # 显示前15个国家
            top_countries = country_analysis.head(15)

            fig_country = px.bar(
                top_countries,
                x='国家',
                y='销售额',
                color='大区',
                title="各国家销售额排行榜 (前15名)",
                labels={'销售额': '销售额 ($)'}
            )
            fig_country.update_xaxes(tickangle=45)
            st.plotly_chart(fig_country, use_container_width=True)

            st.dataframe(country_analysis, use_container_width=True)

            # 省份/州销售分析
            st.subheader("🏛️ 省份/州销售分析")

            state_analysis = df.groupby(['customer_region', 'customer_country', 'customer_state']).agg({
                'total_amount': 'sum',
                'order_id': 'count',
                'quantity': 'sum'
            }).reset_index()
            state_analysis.columns = ['大区', '国家', '省份/州', '销售额', '订单数', '销售数量']
            state_analysis = state_analysis.sort_values('销售额', ascending=False)

            # 显示前20个省份/州
            top_states = state_analysis.head(20)

            fig_state = px.bar(
                top_states,
                x='省份/州',
                y='销售额',
                color='国家',
                title="各省份/州销售额排行榜 (前20名)",
                labels={'销售额': '销售额 ($)'}
            )
            fig_state.update_xaxes(tickangle=45)
            st.plotly_chart(fig_state, use_container_width=True)

            # 地区产品偏好分析
            st.subheader("🎯 地区产品偏好分析")

            region_product = df.groupby(['customer_region', 'product_category'])['total_amount'].sum().reset_index()

            fig_region_product = px.bar(
                region_product,
                x='customer_region',
                y='total_amount',
                color='product_category',
                title="各大区产品类别销售额分布",
                labels={'total_amount': '销售额 ($)', 'customer_region': '大区'}
            )
            st.plotly_chart(fig_region_product, use_container_width=True)

            # 地区热力图
            st.subheader("🔥 地区销售热力图")

            # 创建国家-产品类别热力图
            country_product_pivot = df.groupby(['customer_country', 'product_category'])['total_amount'].sum().reset_index()
            country_product_matrix = country_product_pivot.pivot(
                index='customer_country',
                columns='product_category',
                values='total_amount'
            ).fillna(0)

            fig_heatmap = px.imshow(
                country_product_matrix,
                title="国家-产品类别销售热力图",
                labels=dict(x="产品类别", y="国家", color="销售额"),
                aspect="auto"
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)

            # 详细数据表
            st.subheader("📋 详细地区数据")

            # 选择查看级别
            view_level = st.selectbox(
                "选择查看级别",
                ["大区汇总", "国家汇总", "省份/州详情"]
            )

            if view_level == "大区汇总":
                st.dataframe(region_analysis, use_container_width=True)
            elif view_level == "国家汇总":
                st.dataframe(country_analysis, use_container_width=True)
            else:
                st.dataframe(state_analysis, use_container_width=True)

        else:
            st.warning("当前数据不包含详细地区信息，请重新生成数据以获得完整的地区分析功能。")

            # 显示现有的简单地区分析
            st.subheader("📊 基础地区分析")

            region_analysis = df.groupby('customer_region').agg({
                'total_amount': 'sum',
                'order_id': 'count',
                'quantity': 'sum'
            }).reset_index()
            region_analysis.columns = ['地区', '销售额', '订单数', '销售数量']

            st.dataframe(region_analysis, use_container_width=True)

    else:
        st.info("更多功能正在开发中...")

else:
    st.error("无法加载订单数据，请检查数据文件是否存在")
