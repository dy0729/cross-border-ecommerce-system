import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="智能供应商选择",
    page_icon="🏭",
    layout="wide"
)

st.title("🏭 智能供应商选择系统")
st.markdown("---")

# 生成模拟供应商数据
@st.cache_data
def generate_supplier_data():
    """生成模拟的供应商数据"""
    np.random.seed(42)
    
    suppliers = []
    company_names = [
        "深圳科技有限公司", "广州制造集团", "东莞精密工业", "佛山智能科技",
        "中山电子有限公司", "珠海创新制造", "惠州精工科技", "江门智造集团",
        "肇庆工业园区", "汕头出口贸易", "潮州陶瓷工艺", "揭阳五金制品",
        "梅州农产品加工", "河源矿物材料", "阳江刀具制造", "湛江海产加工",
        "茂名石化产品", "清远环保材料", "韶关钢铁集团", "云浮石材加工"
    ]
    
    product_categories = ["电子产品", "服装配饰", "女装系列", "女装配饰", "家居用品", "运动户外", "美妆护肤"]
    
    for i, name in enumerate(company_names):
        supplier = {
            "供应商ID": f"SUP{i+1:03d}",
            "公司名称": name,
            "产品类别": np.random.choice(product_categories),
            "价格评分": np.random.uniform(6.0, 9.5),  # 价格竞争力（越高越好）
            "质量评分": np.random.uniform(7.0, 9.8),  # 产品质量
            "交期评分": np.random.uniform(6.5, 9.5),  # 交货及时性
            "服务评分": np.random.uniform(6.0, 9.0),  # 客户服务
            "信誉评分": np.random.uniform(7.0, 9.5),  # 企业信誉
            "产能评分": np.random.uniform(6.0, 9.0),  # 生产能力
            "单价": np.random.uniform(10, 100),       # 产品单价
            "最小订量": np.random.randint(100, 5000),  # 最小起订量
            "交货周期": np.random.randint(7, 45),      # 交货周期（天）
            "所在地区": np.random.choice(["华南", "华东", "华北", "西南", "华中"]),
            "成立年份": np.random.randint(2000, 2020),
            "员工数量": np.random.randint(50, 2000),
            "年产值": np.random.uniform(1000, 50000)   # 万元
        }
        suppliers.append(supplier)
    
    return pd.DataFrame(suppliers)

# TOPSIS多准则决策分析
def topsis_analysis(data, weights):
    """TOPSIS多准则决策分析"""
    # 选择评估指标
    criteria = ['价格评分', '质量评分', '交期评分', '服务评分', '信誉评分', '产能评分']
    
    # 提取决策矩阵
    decision_matrix = data[criteria].values
    
    # 标准化决策矩阵
    normalized_matrix = decision_matrix / np.sqrt(np.sum(decision_matrix**2, axis=0))
    
    # 加权标准化矩阵
    weighted_matrix = normalized_matrix * weights
    
    # 确定正理想解和负理想解
    ideal_best = np.max(weighted_matrix, axis=0)
    ideal_worst = np.min(weighted_matrix, axis=0)
    
    # 计算距离
    distance_best = np.sqrt(np.sum((weighted_matrix - ideal_best)**2, axis=1))
    distance_worst = np.sqrt(np.sum((weighted_matrix - ideal_worst)**2, axis=1))
    
    # 计算相对接近度
    closeness = distance_worst / (distance_best + distance_worst)
    
    return closeness

# 加载数据
df = generate_supplier_data()

# 侧边栏控制
st.sidebar.header("🎯 筛选条件")

# 产品类别筛选
selected_category = st.sidebar.selectbox(
    "选择产品类别",
    options=["全部"] + list(df['产品类别'].unique()),
    index=0
)

# 地区筛选
selected_region = st.sidebar.selectbox(
    "选择地区",
    options=["全部"] + list(df['所在地区'].unique()),
    index=0
)

# 价格范围
price_range = st.sidebar.slider(
    "单价范围",
    min_value=float(df['单价'].min()),
    max_value=float(df['单价'].max()),
    value=(float(df['单价'].min()), float(df['单价'].max())),
    step=1.0
)

# 筛选数据
filtered_df = df.copy()

if selected_category != "全部":
    filtered_df = filtered_df[filtered_df['产品类别'] == selected_category]

if selected_region != "全部":
    filtered_df = filtered_df[filtered_df['所在地区'] == selected_region]

filtered_df = filtered_df[
    (filtered_df['单价'] >= price_range[0]) & 
    (filtered_df['单价'] <= price_range[1])
]

# 权重设置
st.sidebar.header("⚖️ 评估权重设置")
st.sidebar.markdown("调整各项指标的重要性权重：")

weight_price = st.sidebar.slider("价格权重", 0.0, 1.0, 0.2, 0.05)
weight_quality = st.sidebar.slider("质量权重", 0.0, 1.0, 0.25, 0.05)
weight_delivery = st.sidebar.slider("交期权重", 0.0, 1.0, 0.2, 0.05)
weight_service = st.sidebar.slider("服务权重", 0.0, 1.0, 0.15, 0.05)
weight_reputation = st.sidebar.slider("信誉权重", 0.0, 1.0, 0.15, 0.05)
weight_capacity = st.sidebar.slider("产能权重", 0.0, 1.0, 0.05, 0.05)

# 权重归一化
total_weight = weight_price + weight_quality + weight_delivery + weight_service + weight_reputation + weight_capacity
if total_weight > 0:
    weights = np.array([weight_price, weight_quality, weight_delivery, weight_service, weight_reputation, weight_capacity]) / total_weight
else:
    weights = np.array([1/6] * 6)

st.sidebar.markdown(f"**权重总和**: {total_weight:.2f}")

# 主要内容区域
if len(filtered_df) == 0:
    st.warning("⚠️ 没有符合筛选条件的供应商，请调整筛选条件。")
else:
    # 执行TOPSIS分析
    topsis_scores = topsis_analysis(filtered_df, weights)
    filtered_df['TOPSIS评分'] = topsis_scores
    filtered_df['排名'] = filtered_df['TOPSIS评分'].rank(ascending=False, method='min').astype(int)
    
    # 按TOPSIS评分排序
    ranked_df = filtered_df.sort_values('TOPSIS评分', ascending=False)
    
    # 显示结果
    st.subheader("🏆 供应商排名结果")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 排名表格
        display_columns = ['排名', '公司名称', '产品类别', '所在地区', 'TOPSIS评分', '单价', '交货周期']
        display_df = ranked_df[display_columns].head(10)
        display_df['TOPSIS评分'] = display_df['TOPSIS评分'].round(4)
        display_df['单价'] = display_df['单价'].round(2)
        
        st.dataframe(display_df, use_container_width=True)
    
    with col2:
        # 推荐供应商
        st.subheader("🎯 推荐供应商")
        top_supplier = ranked_df.iloc[0]
        
        st.success(f"**{top_supplier['公司名称']}**")
        st.write(f"📍 地区: {top_supplier['所在地区']}")
        st.write(f"🏷️ 类别: {top_supplier['产品类别']}")
        st.write(f"💰 单价: ¥{top_supplier['单价']:.2f}")
        st.write(f"📅 交期: {top_supplier['交货周期']}天")
        st.write(f"⭐ 评分: {top_supplier['TOPSIS评分']:.4f}")
        
        # 联系按钮
        if st.button("📞 联系供应商", type="primary"):
            st.info("📧 联系信息已发送到您的邮箱")

    # 可视化分析
    st.markdown("---")
    st.subheader("📊 供应商分析")
    
    tab1, tab2, tab3 = st.tabs(["雷达图对比", "散点图分析", "分布统计"])
    
    with tab1:
        # 雷达图对比
        st.subheader("🎯 供应商雷达图对比")
        
        # 选择要对比的供应商
        supplier_options = ranked_df['公司名称'].head(10).tolist()
        selected_suppliers = st.multiselect(
            "选择要对比的供应商（最多5个）",
            options=supplier_options,
            default=supplier_options[:3],
            max_selections=5
        )
        
        if selected_suppliers:
            # 创建雷达图
            fig_radar = go.Figure()
            
            criteria = ['价格评分', '质量评分', '交期评分', '服务评分', '信誉评分', '产能评分']
            
            for supplier_name in selected_suppliers:
                supplier_data = ranked_df[ranked_df['公司名称'] == supplier_name].iloc[0]
                values = [supplier_data[criterion] for criterion in criteria]
                
                fig_radar.add_trace(go.Scatterpolar(
                    r=values,
                    theta=criteria,
                    fill='toself',
                    name=supplier_name
                ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 10]
                    )),
                showlegend=True,
                title="供应商多维度对比",
                height=500
            )
            
            st.plotly_chart(fig_radar, use_container_width=True)
    
    with tab2:
        # 散点图分析
        st.subheader("📈 价格-质量散点图")
        
        fig_scatter = px.scatter(
            ranked_df.head(20),
            x='单价',
            y='质量评分',
            size='TOPSIS评分',
            color='产品类别',
            hover_data=['公司名称', '交货周期'],
            title="供应商价格与质量关系"
        )
        
        fig_scatter.update_layout(height=500)
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with tab3:
        # 分布统计
        col1, col2 = st.columns(2)
        
        with col1:
            # 地区分布
            region_count = filtered_df['所在地区'].value_counts()
            fig_region = px.pie(
                values=region_count.values,
                names=region_count.index,
                title="供应商地区分布"
            )
            st.plotly_chart(fig_region, use_container_width=True)
        
        with col2:
            # 价格分布
            fig_price = px.histogram(
                filtered_df,
                x='单价',
                nbins=20,
                title="供应商价格分布"
            )
            st.plotly_chart(fig_price, use_container_width=True)

    # 详细信息
    st.markdown("---")
    st.subheader("📋 供应商详细信息")
    
    # 选择查看详情的供应商
    selected_detail = st.selectbox(
        "选择查看详情的供应商",
        options=ranked_df['公司名称'].tolist(),
        index=0
    )
    
    if selected_detail:
        detail_data = ranked_df[ranked_df['公司名称'] == selected_detail].iloc[0]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 基本信息")
            st.write(f"**公司名称**: {detail_data['公司名称']}")
            st.write(f"**供应商ID**: {detail_data['供应商ID']}")
            st.write(f"**产品类别**: {detail_data['产品类别']}")
            st.write(f"**所在地区**: {detail_data['所在地区']}")
            st.write(f"**成立年份**: {detail_data['成立年份']}")
        
        with col2:
            st.markdown("#### 商务信息")
            st.write(f"**产品单价**: ¥{detail_data['单价']:.2f}")
            st.write(f"**最小订量**: {detail_data['最小订量']:,}件")
            st.write(f"**交货周期**: {detail_data['交货周期']}天")
            st.write(f"**年产值**: {detail_data['年产值']:.0f}万元")
            st.write(f"**员工数量**: {detail_data['员工数量']}人")
        
        with col3:
            st.markdown("#### 评估得分")
            st.write(f"**TOPSIS评分**: {detail_data['TOPSIS评分']:.4f}")
            st.write(f"**综合排名**: 第{detail_data['排名']}名")
            st.write(f"**价格评分**: {detail_data['价格评分']:.1f}/10")
            st.write(f"**质量评分**: {detail_data['质量评分']:.1f}/10")
            st.write(f"**交期评分**: {detail_data['交期评分']:.1f}/10")

# 导出功能
st.markdown("---")
st.subheader("📥 数据导出")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📊 导出排名结果"):
        csv = ranked_df.to_csv(index=False)
        st.download_button(
            label="下载排名 CSV",
            data=csv,
            file_name="供应商排名结果.csv",
            mime="text/csv"
        )

with col2:
    if st.button("🎯 导出推荐报告"):
        # 生成推荐报告
        report = f"""
供应商推荐报告
================

推荐供应商: {ranked_df.iloc[0]['公司名称']}
TOPSIS评分: {ranked_df.iloc[0]['TOPSIS评分']:.4f}
综合排名: 第1名

评估权重设置:
- 价格权重: {weight_price:.2f}
- 质量权重: {weight_quality:.2f}
- 交期权重: {weight_delivery:.2f}
- 服务权重: {weight_service:.2f}
- 信誉权重: {weight_reputation:.2f}
- 产能权重: {weight_capacity:.2f}

筛选条件:
- 产品类别: {selected_category}
- 地区: {selected_region}
- 价格范围: {price_range[0]:.2f} - {price_range[1]:.2f}

候选供应商数量: {len(filtered_df)}
        """
        
        st.download_button(
            label="下载推荐报告",
            data=report,
            file_name="供应商推荐报告.txt",
            mime="text/plain"
        )

with col3:
    if st.button("📋 生成对比分析"):
        st.info("📄 对比分析报告生成功能开发中...")

# 帮助信息
with st.expander("❓ 使用帮助"):
    st.markdown("""
    ### 📖 功能说明
    
    1. **筛选条件**: 根据产品类别、地区、价格等条件筛选供应商
    2. **权重设置**: 调整各评估指标的重要性权重
    3. **TOPSIS分析**: 基于多准则决策的供应商排名
    4. **可视化对比**: 雷达图、散点图等多种对比方式
    
    ### 📊 评估指标说明
    
    - **价格评分**: 价格竞争力（分数越高表示价格越有优势）
    - **质量评分**: 产品质量水平
    - **交期评分**: 交货及时性和可靠性
    - **服务评分**: 客户服务质量
    - **信誉评分**: 企业信誉和口碑
    - **产能评分**: 生产能力和规模
    
    ### 🔧 TOPSIS方法

    TOPSIS（逼近理想解排序法）是一种多准则决策分析方法：
    1. 构建标准化决策矩阵
    2. 确定加权标准化矩阵
    3. 计算正理想解和负理想解
    4. 计算各方案到理想解的距离
    5. 计算相对接近度并排序

    ### 💡 使用建议

    - 根据实际业务需求调整权重设置
    - 结合多个维度进行综合评估
    - 定期更新供应商数据和评估结果
    - 建立长期合作关系前进行实地考察
    """)
