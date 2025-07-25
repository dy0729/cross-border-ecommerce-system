import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import warnings
import os

warnings.filterwarnings('ignore')

# 确保工作目录正确
script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(script_dir)

st.set_page_config(page_title="智链云 - 库存规划", layout="wide")

st.title("📦 智能库存规划系统")
st.write("基于需求预测的库存优化 | 安全库存计算 | 补货建议")

# 加载数据
@st.cache_data
def load_data():
    try:
        orders_df = pd.read_csv('data/enhanced_customer_orders.csv')
        orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])

        suppliers_df = pd.read_csv('data/enhanced_supplier_data.csv')
        
        return orders_df, suppliers_df
    except FileNotFoundError:
        st.error("未找到数据文件，请先运行增强数据生成器")
        return pd.DataFrame(), pd.DataFrame()

orders_df, suppliers_df = load_data()

if not orders_df.empty and not suppliers_df.empty:
    
    st.sidebar.header("🎛️ 备货参数设置")
    
    # 选择产品
    selected_product = st.sidebar.selectbox(
        "选择产品",
        orders_df['product_name'].unique()
    )
    
    # 备货参数
    lead_time = st.sidebar.slider("供应商交货周期 (天)", 7, 60, 15)
    service_level = st.sidebar.slider("服务水平 (%)", 85, 99, 95)
    forecast_period = st.sidebar.slider("预测周期 (天)", 30, 180, 60)
    
    # 成本参数
    holding_cost_rate = st.sidebar.slider("库存持有成本率 (%/年)", 10, 50, 25) / 100
    stockout_cost = st.sidebar.number_input("缺货成本 ($/件)", 1.0, 100.0, 10.0)
    
    if st.sidebar.button("🚀 开始分析", type="primary"):
        
        # 筛选产品数据
        product_data = orders_df[orders_df['product_name'] == selected_product].copy()
        
        if len(product_data) > 0:
            
            # 计算基本统计信息
            st.header("📊 产品需求分析")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_quantity = product_data['quantity'].sum()
                st.metric("历史总销量", f"{total_quantity:,}件")
            
            with col2:
                avg_daily_demand = product_data.groupby('order_date')['quantity'].sum().mean()
                st.metric("平均日需求", f"{avg_daily_demand:.1f}件")
            
            with col3:
                demand_std = product_data.groupby('order_date')['quantity'].sum().std()
                st.metric("需求标准差", f"{demand_std:.1f}件")
            
            with col4:
                avg_price = product_data['unit_price'].mean()
                st.metric("平均单价", f"${avg_price:.2f}")
            
            # 需求预测
            st.header("🔮 需求预测与备货建议")
            
            # 简化的需求预测（基于历史平均和趋势）
            daily_demand = product_data.groupby('order_date')['quantity'].sum()
            
            # 计算预测需求
            forecast_daily_demand = avg_daily_demand
            forecast_total_demand = forecast_daily_demand * forecast_period
            
            # 计算安全库存
            # 使用正态分布假设计算安全库存
            from scipy import stats
            z_score = stats.norm.ppf(service_level / 100)
            safety_stock = z_score * demand_std * np.sqrt(lead_time)
            
            # 计算再订货点
            reorder_point = (forecast_daily_demand * lead_time) + safety_stock
            
            # 计算经济订货量 (EOQ)
            annual_demand = forecast_daily_demand * 365
            ordering_cost = 50  # 假设订货成本
            holding_cost = avg_price * holding_cost_rate
            
            if holding_cost > 0:
                eoq = np.sqrt((2 * annual_demand * ordering_cost) / holding_cost)
            else:
                eoq = forecast_total_demand / 4  # 备用计算
            
            # 显示备货建议
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📋 备货建议")
                
                st.metric("预测总需求", f"{forecast_total_demand:.0f}件", 
                         help=f"未来{forecast_period}天的预测需求")
                
                st.metric("安全库存", f"{safety_stock:.0f}件", 
                         help=f"在{service_level}%服务水平下的安全库存")
                
                st.metric("再订货点", f"{reorder_point:.0f}件", 
                         help="当库存降至此水平时应立即补货")
                
                st.metric("建议订货量", f"{eoq:.0f}件", 
                         help="经济订货量，平衡订货成本和持有成本")
            
            with col2:
                st.subheader("💰 成本分析")
                
                # 计算各种成本
                holding_cost_total = (eoq / 2) * holding_cost
                ordering_frequency = annual_demand / eoq
                ordering_cost_total = ordering_frequency * ordering_cost
                total_cost = holding_cost_total + ordering_cost_total
                
                st.metric("年持有成本", f"${holding_cost_total:.2f}")
                st.metric("年订货成本", f"${ordering_cost_total:.2f}")
                st.metric("总库存成本", f"${total_cost:.2f}")
                
                # 库存周转率
                inventory_turnover = annual_demand / (eoq / 2)
                st.metric("库存周转率", f"{inventory_turnover:.1f}次/年")
            
            # 需求趋势图
            st.subheader("📈 历史需求趋势")
            
            # 按周聚合数据以减少噪音
            weekly_demand = product_data.set_index('order_date').resample('W')['quantity'].sum()
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=weekly_demand.index,
                y=weekly_demand.values,
                mode='lines+markers',
                name='周需求量',
                line=dict(color='blue')
            ))
            
            # 添加平均需求线
            fig.add_hline(
                y=weekly_demand.mean(),
                line_dash="dash",
                line_color="red",
                annotation_text=f"平均周需求: {weekly_demand.mean():.1f}件"
            )
            
            fig.update_layout(
                title=f"{selected_product} - 历史需求趋势",
                xaxis_title="日期",
                yaxis_title="需求量",
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 库存模拟
            st.subheader("📊 库存水平模拟")
            
            # 模拟未来库存水平
            simulation_days = min(forecast_period, 90)
            current_inventory = eoq  # 假设当前库存为EOQ
            
            inventory_levels = [current_inventory]
            dates = [datetime.now()]
            
            for day in range(1, simulation_days + 1):
                # 模拟每日需求（使用正态分布）
                daily_demand_sim = max(0, np.random.normal(forecast_daily_demand, demand_std))
                
                # 更新库存
                current_inventory -= daily_demand_sim
                
                # 检查是否需要补货
                if current_inventory <= reorder_point and day % lead_time == 0:
                    current_inventory += eoq
                
                inventory_levels.append(current_inventory)
                dates.append(datetime.now() + timedelta(days=day))
            
            # 绘制库存模拟图
            fig_sim = go.Figure()
            
            fig_sim.add_trace(go.Scatter(
                x=dates,
                y=inventory_levels,
                mode='lines',
                name='库存水平',
                line=dict(color='green')
            ))
            
            fig_sim.add_hline(
                y=reorder_point,
                line_dash="dash",
                line_color="orange",
                annotation_text=f"再订货点: {reorder_point:.0f}件"
            )
            
            fig_sim.add_hline(
                y=safety_stock,
                line_dash="dash",
                line_color="red",
                annotation_text=f"安全库存: {safety_stock:.0f}件"
            )
            
            fig_sim.update_layout(
                title="库存水平模拟",
                xaxis_title="日期",
                yaxis_title="库存数量",
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_sim, use_container_width=True)
            
            # 供应商匹配
            st.header("🏭 推荐供应商")
            
            # 获取产品类别
            product_category = product_data['product_category'].iloc[0]
            
            # 筛选相关供应商
            relevant_suppliers = suppliers_df[suppliers_df['主营产品'] == product_category].copy()
            
            if not relevant_suppliers.empty:
                # 清理数据
                relevant_suppliers['店铺年份_数值'] = relevant_suppliers['店铺年份'].str.replace('年', '').astype(float)
                relevant_suppliers['月产能_数值'] = relevant_suppliers['月产能'].str.replace('件', '').astype(float)
                relevant_suppliers['最小起订量_数值'] = relevant_suppliers['最小起订量'].str.replace('件', '').astype(float)
                relevant_suppliers['交货周期_数值'] = relevant_suppliers['交货周期'].str.replace('天', '').astype(float)
                relevant_suppliers['准时交货率_数值'] = relevant_suppliers['准时交货率'].str.replace('%', '').astype(float)
                
                # 筛选满足条件的供应商
                suitable_suppliers = relevant_suppliers[
                    (relevant_suppliers['月产能_数值'] >= eoq) &
                    (relevant_suppliers['最小起订量_数值'] <= eoq) &
                    (relevant_suppliers['交货周期_数值'] <= lead_time + 5)
                ].copy()
                
                if not suitable_suppliers.empty:
                    # 计算综合评分
                    suitable_suppliers['综合评分'] = (
                        suitable_suppliers['店铺评分'] * 0.3 +
                        (suitable_suppliers['准时交货率_数值'] / 100) * 5 * 0.3 +
                        (suitable_suppliers['店铺年份_数值'] / 25) * 5 * 0.2 +
                        (1 - suitable_suppliers['交货周期_数值'] / 30) * 5 * 0.2
                    )
                    
                    # 排序
                    suitable_suppliers = suitable_suppliers.sort_values('综合评分', ascending=False)
                    
                    # 显示推荐供应商
                    display_cols = ['店铺名称', '店铺评分', '月产能', '最小起订量', '交货周期', '准时交货率', '所在地区', '综合评分']
                    
                    st.dataframe(
                        suitable_suppliers[display_cols].head(10),
                        use_container_width=True
                    )
                    
                    # 供应商对比图
                    if len(suitable_suppliers) >= 3:
                        top_3_suppliers = suitable_suppliers.head(3)
                        
                        fig_radar = go.Figure()
                        
                        categories = ['店铺评分', '准时交货率_数值', '店铺年份_数值']
                        
                        for idx, (_, supplier) in enumerate(top_3_suppliers.iterrows()):
                            values = [
                                supplier['店铺评分'],
                                supplier['准时交货率_数值'],
                                supplier['店铺年份_数值']
                            ]
                            
                            fig_radar.add_trace(go.Scatterpolar(
                                r=values,
                                theta=categories,
                                fill='toself',
                                name=supplier['店铺名称']
                            ))
                        
                        fig_radar.update_layout(
                            polar=dict(
                                radialaxis=dict(visible=True)
                            ),
                            title="前三名供应商对比雷达图"
                        )
                        
                        st.plotly_chart(fig_radar, use_container_width=True)
                
                else:
                    st.warning("没有找到满足当前需求条件的供应商")
            else:
                st.warning(f"没有找到主营 '{product_category}' 的供应商")
        
        else:
            st.error(f"未找到产品 '{selected_product}' 的历史数据")

else:
    st.error("无法加载数据，请检查数据文件是否存在")
