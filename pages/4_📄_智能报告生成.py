import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import base64
import io

st.set_page_config(
    page_title="智能报告生成",
    page_icon="📄",
    layout="wide"
)

st.title("📄 智能报告生成系统")
st.markdown("---")

# 地区数据结构
REGIONS_DATA = {
    '东亚': {
        '中国': ['北京', '上海', '广东', '浙江', '江苏'],
        '日本': ['东京都', '大阪府', '神奈川县'],
        '韩国': ['首尔', '釜山', '仁川']
    },
    '欧洲': {
        '德国': ['巴伐利亚州', '北莱茵-威斯特法伦州'],
        '法国': ['法兰西岛大区', '奥弗涅-罗纳-阿尔卑斯大区'],
        '英国': ['英格兰', '苏格兰', '威尔士']
    },
    '北美洲': {
        '美国': ['加利福尼亚州', '德克萨斯州', '佛罗里达州'],
        '加拿大': ['安大略省', '魁北克省']
    }
}

# 生成模拟数据
@st.cache_data
def generate_report_data():
    """生成报告用的模拟数据"""
    np.random.seed(42)
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    products = ['电子产品', '服装配饰', '女装系列', '女装配饰', '家居用品', '运动户外', '美妆护肤']
    
    data = []
    for continent, countries in REGIONS_DATA.items():
        for country, provinces in countries.items():
            for province in provinces[:2]:  # 每个国家取前2个省份
                for product in products:
                    region_multiplier = np.random.uniform(0.5, 2.0)
                    base_trend = np.linspace(100, 200, len(dates)) * region_multiplier
                    seasonal = 50 * np.sin(2 * np.pi * np.arange(len(dates)) / 365.25)
                    noise = np.random.normal(0, 15, len(dates))
                    sales = base_trend + seasonal + noise
                    sales = np.maximum(sales, 10)
                    
                    for i, date in enumerate(dates):
                        data.append({
                            'date': date,
                            'product': product,
                            'continent': continent,
                            'country': country,
                            'province': province,
                            'sales': int(sales[i]),
                            'revenue': sales[i] * np.random.uniform(20, 100)
                        })
    
    return pd.DataFrame(data)

# 生成图表
def create_charts(df, report_type):
    """创建报告图表"""
    charts = {}
    
    if report_type == "需求预测报告":
        # 时间序列图
        daily_sales = df.groupby('date')['sales'].sum().reset_index()
        fig_trend = px.line(daily_sales, x='date', y='sales', title='销售趋势分析')
        charts['trend'] = fig_trend
        
        # 产品对比图
        product_sales = df.groupby('product')['sales'].sum().reset_index()
        fig_product = px.bar(product_sales, x='product', y='sales', title='产品销售对比')
        charts['product'] = fig_product
        
        # 地区分析图
        continent_sales = df.groupby('continent')['sales'].sum().reset_index()
        fig_region = px.pie(continent_sales, values='sales', names='continent', title='地区销售分布')
        charts['region'] = fig_region
    
    elif report_type == "供应商分析报告":
        # 模拟供应商数据
        suppliers = ['供应商A', '供应商B', '供应商C', '供应商D', '供应商E']
        scores = np.random.uniform(7, 9.5, len(suppliers))
        fig_supplier = px.bar(x=suppliers, y=scores, title='供应商评分对比')
        charts['supplier'] = fig_supplier
    
    elif report_type == "库存分析报告":
        # 库存周转率
        products = df['product'].unique()
        turnover_rates = np.random.uniform(2, 8, len(products))
        fig_turnover = px.bar(x=products, y=turnover_rates, title='库存周转率分析')
        charts['turnover'] = fig_turnover
    
    return charts

# 生成简化PDF报告
def generate_simple_pdf_report(df, report_type, selected_params):
    """生成简化的PDF报告"""
    try:
        # 这里使用简单的HTML转PDF方法
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{report_type}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #2E86AB; text-align: center; }}
                h2 {{ color: #A23B72; border-bottom: 2px solid #A23B72; }}
                .metric {{ background: #f0f0f0; padding: 10px; margin: 10px 0; border-radius: 5px; }}
                .summary {{ background: #e8f4f8; padding: 15px; border-radius: 8px; }}
            </style>
        </head>
        <body>
            <h1>智链云：{report_type}</h1>
            <p><strong>生成时间：</strong> {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}</p>
            <p><strong>分析时间范围：</strong> {selected_params.get('date_range', '过去一年')}</p>
            
            <h2>执行摘要</h2>
            <div class="summary">
                <div class="metric">总销量：{df['sales'].sum():,.0f} 件</div>
                <div class="metric">总收入：${df['revenue'].sum():,.2f}</div>
                <div class="metric">日均销量：{df.groupby('date')['sales'].sum().mean():.0f} 件</div>
                <div class="metric">产品类别：{len(df['product'].unique())} 个</div>
                <div class="metric">覆盖地区：{len(df['continent'].unique())} 个大洲</div>
            </div>
            
            <h2>主要发现</h2>
            <ul>
                <li>销售趋势整体向好，具有明显的季节性特征</li>
                <li>不同产品类别表现差异明显，需要差异化策略</li>
                <li>地区市场发展不均衡，存在巨大优化空间</li>
                <li>建议加强对高增长产品的资源投入</li>
            </ul>
            
            <h2>行动建议</h2>
            <ol>
                <li>制定地区化的营销和库存策略</li>
                <li>建立动态需求预测模型，提高预测准确性</li>
                <li>优化供应商结构，降低采购成本</li>
                <li>实施精细化库存管理，提高周转效率</li>
            </ol>
            
            <hr>
            <p style="text-align: center; color: #666;">
                © 2024 智链云项目组 | 智能决策系统报告
            </p>
        </body>
        </html>
        """
        
        return html_content.encode('utf-8')
        
    except Exception as e:
        st.error(f"PDF生成失败: {str(e)}")
        return None

# 侧边栏控制
st.sidebar.header("📊 报告配置")

# 报告类型选择
report_type = st.sidebar.selectbox(
    "选择报告类型",
    options=["需求预测报告", "供应商分析报告", "库存分析报告", "综合分析报告"],
    index=0
)

# 时间范围选择
time_range = st.sidebar.selectbox(
    "分析时间范围",
    options=["过去7天", "过去30天", "过去90天", "过去1年"],
    index=3
)

# 地区选择
selected_continent = st.sidebar.selectbox(
    "选择分析地区",
    options=['全部'] + list(REGIONS_DATA.keys()),
    index=0
)

# 产品类别选择
product_categories = ['全部', '电子产品', '服装配饰', '女装系列', '女装配饰', '家居用品', '运动户外', '美妆护肤']
selected_products = st.sidebar.multiselect(
    "选择产品类别",
    options=product_categories,
    default=['全部']
)

# 加载数据
df = generate_report_data()

# 数据筛选
filtered_df = df.copy()

if selected_continent != '全部':
    filtered_df = filtered_df[filtered_df['continent'] == selected_continent]

if '全部' not in selected_products:
    filtered_df = filtered_df[filtered_df['product'].isin(selected_products)]

# 主要内容区域
st.subheader(f"📋 {report_type}")

# 报告参数显示
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("数据记录数", f"{len(filtered_df):,}")

with col2:
    st.metric("分析时间范围", time_range)

with col3:
    st.metric("覆盖地区", selected_continent)

# 生成报告按钮
if st.button("🔄 生成报告", type="primary"):
    with st.spinner("正在生成报告..."):
        # 准备报告参数
        selected_params = {
            'report_type': report_type,
            'time_range': time_range,
            'continent': selected_continent,
            'products': selected_products,
            'date_range': f"{filtered_df['date'].min().date()} 至 {filtered_df['date'].max().date()}"
        }
        
        # 生成图表
        charts = create_charts(filtered_df, report_type)
        
        # 存储到session state
        st.session_state['report_data'] = filtered_df
        st.session_state['report_params'] = selected_params
        st.session_state['report_charts'] = charts
        
        st.success("✅ 报告生成完成！")

# 显示报告内容
if 'report_data' in st.session_state:
    st.markdown("---")
    
    # 报告标题
    params = st.session_state['report_params']
    st.subheader(f"📊 {params['report_type']} - {params['date_range']}")
    
    # 执行摘要
    st.subheader("📋 执行摘要")
    
    report_df = st.session_state['report_data']
    total_sales = report_df['sales'].sum()
    total_revenue = report_df['revenue'].sum()
    avg_daily_sales = report_df.groupby('date')['sales'].sum().mean()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("总销量", f"{total_sales:,.0f} 件")
    
    with col2:
        st.metric("总收入", f"${total_revenue:,.2f}")
    
    with col3:
        st.metric("日均销量", f"{avg_daily_sales:.0f} 件")
    
    with col4:
        st.metric("产品类别", f"{len(report_df['product'].unique())} 个")
    
    # 图表展示
    st.subheader("📈 数据可视化")
    
    charts = st.session_state['report_charts']
    
    if 'trend' in charts:
        st.plotly_chart(charts['trend'], use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'product' in charts:
            st.plotly_chart(charts['product'], use_container_width=True)
        elif 'supplier' in charts:
            st.plotly_chart(charts['supplier'], use_container_width=True)
        elif 'turnover' in charts:
            st.plotly_chart(charts['turnover'], use_container_width=True)
    
    with col2:
        if 'region' in charts:
            st.plotly_chart(charts['region'], use_container_width=True)
        else:
            # 显示月度趋势
            monthly_data = report_df.groupby(report_df['date'].dt.to_period('M'))['sales'].sum().reset_index()
            monthly_data['date'] = monthly_data['date'].astype(str)
            fig_monthly = px.bar(monthly_data, x='date', y='sales', title='月度销售趋势')
            st.plotly_chart(fig_monthly, use_container_width=True)
    
    # 详细数据表
    st.subheader("📊 详细数据")
    
    if report_type == "需求预测报告":
        # 产品销售汇总
        product_summary = report_df.groupby('product').agg({
            'sales': ['sum', 'mean'],
            'revenue': ['sum', 'mean']
        }).round(2)
        product_summary.columns = ['总销量', '平均销量', '总收入', '平均收入']
        st.dataframe(product_summary, use_container_width=True)
        
    elif report_type == "供应商分析报告":
        # 模拟供应商数据
        suppliers_data = {
            '供应商名称': ['深圳科技有限公司', '广州制造集团', '东莞精密工业', '佛山智能科技', '中山电子有限公司'],
            'TOPSIS评分': np.random.uniform(7.5, 9.5, 5).round(3),
            '价格评分': np.random.uniform(7, 9, 5).round(1),
            '质量评分': np.random.uniform(8, 9.5, 5).round(1),
            '交期评分': np.random.uniform(7.5, 9, 5).round(1),
            '推荐等级': ['A', 'A', 'B', 'A', 'B']
        }
        suppliers_df = pd.DataFrame(suppliers_data)
        st.dataframe(suppliers_df, use_container_width=True)
        
    elif report_type == "库存分析报告":
        # 模拟库存数据
        products = report_df['product'].unique()
        inventory_data = {
            '产品类别': products,
            '当前库存': np.random.randint(500, 2000, len(products)),
            '安全库存': np.random.randint(200, 500, len(products)),
            '再订货点': np.random.randint(800, 1500, len(products)),
            '建议补货量': np.random.randint(1000, 3000, len(products)),
            '库存周转率': np.random.uniform(2, 8, len(products)).round(2)
        }
        inventory_df = pd.DataFrame(inventory_data)
        st.dataframe(inventory_df, use_container_width=True)
    
    # 结论和建议
    st.subheader("💡 结论与建议")
    
    if report_type == "需求预测报告":
        st.markdown("""
        **主要发现：**
        - 销售趋势整体向好，具有明显的季节性特征
        - 不同产品类别表现差异明显，需要差异化策略
        - 地区市场发展不均衡，存在巨大优化空间
        
        **行动建议：**
        - 加强对高增长产品的资源投入
        - 制定地区化的营销和库存策略
        - 建立动态需求预测模型，提高预测准确性
        """)
        
    elif report_type == "供应商分析报告":
        st.markdown("""
        **主要发现：**
        - 供应商整体质量较高，但仍有优化空间
        - 价格和质量之间存在一定的权衡关系
        - 部分供应商在交期方面表现突出
        
        **行动建议：**
        - 与评分最高的供应商建立长期合作关系
        - 对低评分供应商进行改进指导或替换
        - 建立供应商绩效监控体系
        """)
        
    elif report_type == "库存分析报告":
        st.markdown("""
        **主要发现：**
        - 部分产品库存过多，占用资金较大
        - 某些热销产品存在缺货风险
        - 库存周转率整体偏低，有提升空间
        
        **行动建议：**
        - 优化库存结构，减少滞销品库存
        - 提高热销品的安全库存水平
        - 实施JIT库存管理，提高周转效率
        """)
    
    # 导出功能
    st.markdown("---")
    st.subheader("📥 报告导出")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 生成HTML报告"):
            html_content = generate_simple_pdf_report(report_df, params['report_type'], params)
            if html_content:
                st.download_button(
                    label="📥 下载HTML报告",
                    data=html_content,
                    file_name=f"{params['report_type']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                    mime="text/html"
                )
                st.success("✅ HTML报告生成成功！")
    
    with col2:
        if st.button("📊 导出Excel数据"):
            # 创建Excel文件
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                # 原始数据
                report_df.to_excel(writer, sheet_name='原始数据', index=False)
                
                # 汇总数据
                if report_type == "需求预测报告":
                    product_summary.to_excel(writer, sheet_name='产品汇总')
                elif report_type == "供应商分析报告":
                    suppliers_df.to_excel(writer, sheet_name='供应商评分', index=False)
                elif report_type == "库存分析报告":
                    inventory_df.to_excel(writer, sheet_name='库存状态', index=False)
            
            excel_buffer.seek(0)
            
            st.download_button(
                label="📥 下载Excel数据",
                data=excel_buffer.getvalue(),
                file_name=f"{params['report_type']}_数据_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    with col3:
        if st.button("📋 复制报告链接"):
            st.info("📎 报告链接已复制到剪贴板")
            st.code(f"http://localhost:8501/?report_id={datetime.now().strftime('%Y%m%d_%H%M%S')}")

# 帮助信息
with st.expander("❓ 使用帮助"):
    st.markdown("""
    ### 📖 功能说明
    
    1. **报告类型**: 选择需要生成的报告类型
    2. **时间范围**: 设置分析的时间范围
    3. **地区筛选**: 选择分析的地理区域
    4. **产品筛选**: 选择要分析的产品类别
    
    ### 📊 报告类型说明
    
    - **需求预测报告**: 基于历史数据的需求趋势分析和预测
    - **供应商分析报告**: 供应商评估和选择建议
    - **库存分析报告**: 库存状态分析和优化建议
    - **综合分析报告**: 包含多个维度的综合分析
    
    ### 📥 导出功能
    
    - **HTML报告**: 生成网页格式的分析报告
    - **Excel数据**: 导出详细的数据表格
    - **在线查看**: 在浏览器中直接查看报告内容
    """)
