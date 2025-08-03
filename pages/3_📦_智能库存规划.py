import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import math

st.set_page_config(
    page_title="智能库存规划",
    page_icon="📦",
    layout="wide"
)

st.title("📦 智能库存规划系统")
st.markdown("---")

# 生成模拟库存数据
@st.cache_data
def generate_inventory_data():
    """生成模拟的库存数据"""
    np.random.seed(42)
    
    products = [
        "iPhone 14", "Samsung Galaxy S23", "华为 Mate 50", "小米 13", "OPPO Find X5",
        "Nike Air Max", "Adidas Ultra Boost", "New Balance 990", "Converse Chuck Taylor", "Vans Old Skool",
        "MacBook Pro", "Dell XPS 13", "ThinkPad X1", "Surface Laptop", "HP Spectre",
        "Sony WH-1000XM4", "AirPods Pro", "Bose QC35", "Sennheiser HD650", "Audio-Technica ATH-M50x",
        "连衣裙", "半身裙", "上衣", "外套", "裤装", "内衣", "配饰", "鞋履", "包包", "首饰"
    ]

    categories = ["电子产品", "运动鞋", "笔记本电脑", "耳机", "女装系列", "女装配饰"]
    
    inventory_data = []
    for i, product in enumerate(products):
        if i < 5:
            category = categories[0]  # 电子产品
        elif i < 10:
            category = categories[1]  # 运动鞋
        elif i < 15:
            category = categories[2]  # 笔记本电脑
        elif i < 20:
            category = categories[3]  # 耳机
        elif i < 25:
            category = categories[4]  # 女装系列
        else:
            category = categories[5]  # 女装配饰
        
        # 基础参数
        avg_demand = np.random.uniform(50, 200)  # 平均日需求
        demand_std = avg_demand * 0.3  # 需求标准差
        lead_time = np.random.randint(7, 30)  # 采购提前期
        unit_cost = np.random.uniform(100, 2000)  # 单位成本
        holding_cost_rate = np.random.uniform(0.15, 0.25)  # 库存持有成本率
        ordering_cost = np.random.uniform(50, 200)  # 订货成本
        
        # 当前库存状态
        current_stock = np.random.randint(int(avg_demand * lead_time * 0.5), int(avg_demand * lead_time * 2))
        
        inventory_data.append({
            "产品名称": product,
            "产品类别": category,
            "平均日需求": avg_demand,
            "需求标准差": demand_std,
            "采购提前期": lead_time,
            "单位成本": unit_cost,
            "库存持有成本率": holding_cost_rate,
            "订货成本": ordering_cost,
            "当前库存": current_stock,
            "在途库存": np.random.randint(0, int(avg_demand * lead_time * 0.5)),
            "安全库存": 0,  # 待计算
            "再订货点": 0,  # 待计算
            "经济订货量": 0,  # 待计算
            "库存周转率": 0,  # 待计算
            "缺货风险": 0,  # 待计算
        })
    
    return pd.DataFrame(inventory_data)

# 库存优化计算函数
def calculate_inventory_metrics(data, service_level=0.95):
    """计算库存优化指标"""
    from scipy import stats
    
    # 服务水平对应的Z值
    z_score = stats.norm.ppf(service_level)
    
    for idx, row in data.iterrows():
        avg_demand = row['平均日需求']
        demand_std = row['需求标准差']
        lead_time = row['采购提前期']
        unit_cost = row['单位成本']
        holding_cost_rate = row['库存持有成本率']
        ordering_cost = row['订货成本']
        current_stock = row['当前库存']
        
        # 计算安全库存
        lead_time_demand_std = demand_std * math.sqrt(lead_time)
        safety_stock = z_score * lead_time_demand_std
        
        # 计算再订货点
        reorder_point = avg_demand * lead_time + safety_stock
        
        # 计算经济订货量 (EOQ)
        annual_demand = avg_demand * 365
        holding_cost = unit_cost * holding_cost_rate
        eoq = math.sqrt(2 * annual_demand * ordering_cost / holding_cost)
        
        # 计算库存周转率
        inventory_turnover = annual_demand / (current_stock + safety_stock)
        
        # 计算缺货风险
        if current_stock < reorder_point:
            shortage_risk = 1 - stats.norm.cdf(current_stock, reorder_point, lead_time_demand_std)
        else:
            shortage_risk = 0
        
        # 更新数据
        data.at[idx, '安全库存'] = safety_stock
        data.at[idx, '再订货点'] = reorder_point
        data.at[idx, '经济订货量'] = eoq
        data.at[idx, '库存周转率'] = inventory_turnover
        data.at[idx, '缺货风险'] = shortage_risk
    
    return data

# 加载数据
df = generate_inventory_data()

# 侧边栏控制
st.sidebar.header("📊 库存参数设置")

# 服务水平设置
service_level = st.sidebar.slider(
    "目标服务水平",
    min_value=0.80,
    max_value=0.99,
    value=0.95,
    step=0.01,
    format="%.2f"
)

# 产品类别筛选
selected_category = st.sidebar.selectbox(
    "选择产品类别",
    options=["全部"] + list(df['产品类别'].unique()),
    index=0
)

# 库存状态筛选
inventory_status = st.sidebar.selectbox(
    "库存状态筛选",
    options=["全部", "需要补货", "库存充足", "库存过多"],
    index=0
)

# 筛选数据
filtered_df = df.copy()

if selected_category != "全部":
    filtered_df = filtered_df[filtered_df['产品类别'] == selected_category]

# 计算库存指标
filtered_df = calculate_inventory_metrics(filtered_df, service_level)

# 根据库存状态筛选
if inventory_status == "需要补货":
    filtered_df = filtered_df[filtered_df['当前库存'] < filtered_df['再订货点']]
elif inventory_status == "库存充足":
    filtered_df = filtered_df[
        (filtered_df['当前库存'] >= filtered_df['再订货点']) & 
        (filtered_df['当前库存'] <= filtered_df['再订货点'] * 1.5)
    ]
elif inventory_status == "库存过多":
    filtered_df = filtered_df[filtered_df['当前库存'] > filtered_df['再订货点'] * 1.5]

# 主要内容区域
if len(filtered_df) == 0:
    st.warning("⚠️ 没有符合筛选条件的产品，请调整筛选条件。")
else:
    # 概览指标
    st.subheader("📊 库存概览")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_products = len(filtered_df)
        st.metric("产品总数", total_products)
    
    with col2:
        need_reorder = len(filtered_df[filtered_df['当前库存'] < filtered_df['再订货点']])
        st.metric("需要补货", need_reorder, delta=f"{need_reorder/total_products*100:.1f}%")
    
    with col3:
        avg_turnover = filtered_df['库存周转率'].mean()
        st.metric("平均周转率", f"{avg_turnover:.2f}")
    
    with col4:
        high_risk = len(filtered_df[filtered_df['缺货风险'] > 0.1])
        st.metric("高风险产品", high_risk, delta=f"{high_risk/total_products*100:.1f}%")
    
    # 库存分析图表
    st.markdown("---")
    st.subheader("📈 库存分析")
    
    tab1, tab2, tab3 = st.tabs(["库存状态", "补货建议", "成本分析"])
    
    with tab1:
        # 库存状态图表
        col1, col2 = st.columns(2)
        
        with col1:
            # 库存水平对比
            fig_inventory = go.Figure()
            
            fig_inventory.add_trace(go.Bar(
                name='当前库存',
                x=filtered_df['产品名称'][:10],
                y=filtered_df['当前库存'][:10],
                marker_color='lightblue'
            ))
            
            fig_inventory.add_trace(go.Bar(
                name='再订货点',
                x=filtered_df['产品名称'][:10],
                y=filtered_df['再订货点'][:10],
                marker_color='orange'
            ))
            
            fig_inventory.add_trace(go.Bar(
                name='安全库存',
                x=filtered_df['产品名称'][:10],
                y=filtered_df['安全库存'][:10],
                marker_color='red'
            ))
            
            fig_inventory.update_layout(
                title="库存水平对比（前10个产品）",
                xaxis_title="产品",
                yaxis_title="库存数量",
                barmode='group',
                height=400
            )
            
            st.plotly_chart(fig_inventory, use_container_width=True)
        
        with col2:
            # 缺货风险分布
            fig_risk = px.scatter(
                filtered_df,
                x='当前库存',
                y='缺货风险',
                size='平均日需求',
                color='产品类别',
                hover_data=['产品名称'],
                title="缺货风险分析"
            )
            fig_risk.update_layout(height=400)
            st.plotly_chart(fig_risk, use_container_width=True)
    
    with tab2:
        # 补货建议
        st.subheader("🔄 补货建议")
        
        # 需要补货的产品
        reorder_products = filtered_df[filtered_df['当前库存'] < filtered_df['再订货点']].copy()
        reorder_products['建议订货量'] = reorder_products['经济订货量']
        reorder_products['预计到货时间'] = reorder_products['采购提前期']
        
        if len(reorder_products) > 0:
            st.warning(f"⚠️ 有 {len(reorder_products)} 个产品需要补货")
            
            # 补货建议表格
            reorder_display = reorder_products[[
                '产品名称', '产品类别', '当前库存', '再订货点', 
                '建议订货量', '预计到货时间', '缺货风险'
            ]].copy()
            
            # 格式化数值
            for col in ['当前库存', '再订货点', '建议订货量']:
                reorder_display[col] = reorder_display[col].round(0).astype(int)
            reorder_display['缺货风险'] = (reorder_display['缺货风险'] * 100).round(1).astype(str) + '%'
            
            st.dataframe(reorder_display, use_container_width=True)
            
            # 紧急程度排序
            urgent_products = reorder_products.nlargest(5, '缺货风险')
            
            st.subheader("🚨 紧急补货产品")
            for idx, product in urgent_products.iterrows():
                with st.container():
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.write(f"**{product['产品名称']}**")
                        st.write(f"类别: {product['产品类别']}")
                    with col2:
                        st.metric("缺货风险", f"{product['缺货风险']*100:.1f}%")
                    with col3:
                        st.metric("建议订货量", f"{product['建议订货量']:.0f}")
        else:
            st.success("✅ 所有产品库存充足，暂无需要补货的产品")
    
    with tab3:
        # 成本分析
        st.subheader("💰 库存成本分析")
        
        # 计算各种成本
        filtered_df['库存持有成本'] = filtered_df['当前库存'] * filtered_df['单位成本'] * filtered_df['库存持有成本率'] / 365
        filtered_df['年度订货成本'] = (filtered_df['平均日需求'] * 365 / filtered_df['经济订货量']) * filtered_df['订货成本']
        filtered_df['总库存成本'] = filtered_df['库存持有成本'] * 365 + filtered_df['年度订货成本']
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 成本构成饼图
            total_holding_cost = filtered_df['库存持有成本'].sum() * 365
            total_ordering_cost = filtered_df['年度订货成本'].sum()
            
            fig_cost = px.pie(
                values=[total_holding_cost, total_ordering_cost],
                names=['库存持有成本', '订货成本'],
                title="年度库存成本构成"
            )
            st.plotly_chart(fig_cost, use_container_width=True)
        
        with col2:
            # 产品成本排名
            top_cost_products = filtered_df.nlargest(10, '总库存成本')[['产品名称', '总库存成本']]
            
            fig_cost_rank = px.bar(
                top_cost_products,
                x='总库存成本',
                y='产品名称',
                orientation='h',
                title="产品库存成本排名（前10）"
            )
            fig_cost_rank.update_layout(height=400)
            st.plotly_chart(fig_cost_rank, use_container_width=True)

    # 详细数据表格
    st.markdown("---")
    st.subheader("📋 详细库存数据")
    
    # 选择显示的列
    display_columns = st.multiselect(
        "选择要显示的列",
        options=filtered_df.columns.tolist(),
        default=['产品名称', '产品类别', '当前库存', '再订货点', '安全库存', '经济订货量', '库存周转率', '缺货风险']
    )
    
    if display_columns:
        display_df = filtered_df[display_columns].copy()
        
        # 格式化数值列
        numeric_columns = display_df.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if col in ['缺货风险']:
                display_df[col] = (display_df[col] * 100).round(1).astype(str) + '%'
            else:
                display_df[col] = display_df[col].round(2)
        
        st.dataframe(display_df, use_container_width=True)

# 库存优化建议
st.markdown("---")
st.subheader("💡 库存优化建议")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🎯 短期建议")
    
    # 分析当前库存状况
    need_reorder = filtered_df[filtered_df['当前库存'] < filtered_df['再订货点']]
    overstocked = filtered_df[filtered_df['当前库存'] > filtered_df['再订货点'] * 2]
    
    if len(need_reorder) > 0:
        st.warning(f"• 立即补货 {len(need_reorder)} 个产品")
    
    if len(overstocked) > 0:
        st.info(f"• 考虑促销 {len(overstocked)} 个库存过多的产品")
    
    high_risk = filtered_df[filtered_df['缺货风险'] > 0.1]
    if len(high_risk) > 0:
        st.error(f"• 重点关注 {len(high_risk)} 个高缺货风险产品")

with col2:
    st.markdown("#### 📈 长期建议")
    
    low_turnover = filtered_df[filtered_df['库存周转率'] < 2]
    if len(low_turnover) > 0:
        st.warning(f"• 优化 {len(low_turnover)} 个低周转率产品的库存策略")
    
    st.info("• 定期审查和调整安全库存水平")
    st.info("• 考虑实施JIT（准时制）库存管理")
    st.info("• 建立供应商协同库存管理")

# 导出功能
st.markdown("---")
st.subheader("📥 数据导出")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📊 导出库存数据"):
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="下载库存 CSV",
            data=csv,
            file_name="库存数据.csv",
            mime="text/csv"
        )

with col2:
    if st.button("🔄 导出补货建议"):
        reorder_data = filtered_df[filtered_df['当前库存'] < filtered_df['再订货点']]
        if len(reorder_data) > 0:
            csv = reorder_data.to_csv(index=False)
            st.download_button(
                label="下载补货建议",
                data=csv,
                file_name="补货建议.csv",
                mime="text/csv"
            )
        else:
            st.info("当前无需补货的产品")

with col3:
    if st.button("📋 生成库存报告"):
        st.info("📄 库存报告生成功能开发中...")

# 帮助信息
with st.expander("❓ 使用帮助"):
    st.markdown("""
    ### 📖 功能说明
    
    1. **服务水平**: 设置目标服务水平，影响安全库存计算
    2. **库存状态**: 筛选不同库存状态的产品
    3. **补货建议**: 基于再订货点的智能补货建议
    4. **成本分析**: 库存持有成本和订货成本分析
    
    ### 📊 关键指标说明
    
    - **安全库存**: 为应对需求不确定性而保持的额外库存
    - **再订货点**: 触发补货的库存水平
    - **经济订货量**: 使总成本最小的订货量
    - **库存周转率**: 年度需求量与平均库存的比值
    - **缺货风险**: 在当前库存水平下发生缺货的概率
    
    ### 🔧 计算方法
    
    - **安全库存** = Z值 × 提前期需求标准差
    - **再订货点** = 提前期需求 + 安全库存
    - **EOQ** = √(2 × 年需求量 × 订货成本 / 库存持有成本)
    - **库存周转率** = 年需求量 / 平均库存
    
    ### 💡 优化建议
    
    - 定期审查库存参数设置
    - 根据季节性调整安全库存
    - 考虑供应商可靠性
    - 平衡服务水平和库存成本
    """)
