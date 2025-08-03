import streamlit as st
import os

# 确保工作目录正确
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

st.set_page_config(
    page_title="系统介绍",
    page_icon="☁️",
    layout="wide"
)

st.title("☁️ 智链云：智能决策系统")
st.markdown("---")

st.header("🎯 系统介绍")
st.info(
    """
    欢迎使用智链云：智能决策系统！
    
    这是一个完整的企业级智能决策支持平台，集成了需求预测、供应商选择、库存优化和数据分析等核心功能。
    系统结合了真实数据分析、机器学习预测和多准则决策分析，为您的业务决策提供全方位的智能支持。
    
    **👈 请通过左侧的导航栏选择功能模块:**
    """
)

# 功能模块介绍
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 📈 智能需求预测
    - **智能预测**: 基于历史数据预测产品需求
    - **季节性分析**: 识别销售季节性模式
    - **多产品支持**: 支持多种产品类别预测
    - **趋势分析**: 长期趋势识别和分析
    
    ### 📦 智能订单管理
    - **订单系统对接**: 实时对接订单业务系统
    - **订单量预测**: 基于机器学习的订单预测
    - **数据可视化**: 丰富的图表和分析
    - **多维度分析**: 地区、渠道、产品等维度
    """)

with col2:
    st.markdown("""
    ### 🏭 智能供应商选择
    - **智能匹配**: 基于需求自动匹配供应商
    - **多源数据**: 整合本地和爬取的供应商数据
    - **综合评估**: 多准则决策分析
    - **实时更新**: 支持供应商数据实时更新
    
    ### 📊 智能库存规划
    - **安全库存计算**: 基于服务水平的库存优化
    - **补货建议**: 智能补货时间和数量建议
    - **成本分析**: 库存持有成本和订货成本分析
    - **风险评估**: 缺货风险和库存风险评估
    """)

st.markdown("---")

# 核心功能模块
st.header("🚀 核心功能模块")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown("""
    #### 📈 智能需求预测
    - 时间序列分析
    - 季节性识别
    - 多地区预测
    - 机器学习算法
    - 女装产品支持
    """)

with col2:
    st.markdown("""
    #### 🏭 智能供应商选择
    - TOPSIS决策分析
    - 多准则评估
    - 权重自定义
    - 智能推荐
    - 雷达图对比
    """)

with col3:
    st.markdown("""
    #### 📦 智能库存规划
    - 安全库存计算
    - EOQ优化
    - 补货建议
    - 成本分析
    - 周转率优化
    """)

with col4:
    st.markdown("""
    #### 📋 智能订单管理
    - 实时订单监控
    - 订单量预测
    - 多维度分析
    - 系统对接
    - 数据可视化
    """)

with col5:
    st.markdown("""
    #### 📄 智能报告生成
    - 智能报告生成
    - PDF/Excel导出
    - 专业可视化
    - 决策建议
    - 在线查看
    """)

st.markdown("---")

# 系统特色
st.header("✨ 系统特色")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    #### 🔍 数据驱动
    - 多源数据整合
    - 多维度数据分析
    - 智能数据清洗
    - 实时数据更新
    """)

with col2:
    st.markdown("""
    #### 🤖 AI智能
    - 机器学习预测
    - 智能推荐算法
    - 自动化决策支持
    - 持续学习优化
    """)

with col3:
    st.markdown("""
    #### 📋 报告生成
    - 智能报告生成系统
    - PDF/Excel多格式导出
    - 专业可视化图表
    - 数据驱动决策建议
    """)

st.markdown("---")

# 快速开始
st.header("🚀 快速开始")
st.markdown("""
1. **📈 智能需求预测**: 分析历史数据，预测未来需求趋势
2. **🏭 智能供应商选择**: 使用TOPSIS算法选择最优供应商
3. **📦 智能库存规划**: 优化库存水平，降低持有成本
4. **📋 智能订单管理**: 实时监控订单，预测订单量
5. **📄 智能报告生成**: 生成专业分析报告，支持多格式导出
6. **🎯 开始使用**: 点击左侧导航栏选择相应功能模块
""")

# 技术架构
st.header("🏗️ 技术架构")
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    #### 前端技术
    - **Streamlit**: 快速构建数据应用
    - **Plotly**: 交互式数据可视化
    - **Bootstrap**: 响应式UI组件
    """)

with col2:
    st.markdown("""
    #### 后端技术
    - **Pandas**: 数据处理和分析
    - **NumPy**: 数值计算
    - **Scikit-learn**: 机器学习算法
    """)

# 数据流程
st.header("📊 数据流程")
st.markdown("""
```
原始数据 → 数据清洗 → 特征工程 → 模型训练 → 预测分析 → 决策支持 → 报告生成
    ↓           ↓           ↓           ↓           ↓           ↓           ↓
历史订单    标准化处理    时间序列    Prophet     需求预测    供应商选择    智能报告
供应商数据  异常检测      季节性      TOPSIS      库存优化    风险评估      可视化
市场数据    数据验证      趋势分析    AHP权重     成本分析    决策建议      导出功能
```
""")

# 支持的产品类别
st.header("🛍️ 支持的产品类别")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    #### 📱 电子产品
    - 智能手机
    - 平板电脑
    - 笔记本电脑
    - 智能穿戴设备
    """)

with col2:
    st.markdown("""
    #### 👗 女装系列
    - 连衣裙、半身裙
    - 上衣、外套
    - 裤装、内衣
    - 鞋履、包包、首饰
    """)

with col3:
    st.markdown("""
    #### 🏠 其他类别
    - 服装配饰
    - 家居用品
    - 运动户外
    - 美妆护肤
    """)

# 应用场景
st.header("🎯 应用场景")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    #### 🏫 教学应用
    - 数据科学课程
    - 运营管理教学
    - 商业智能实训
    - 电子商务案例
    """)

with col2:
    st.markdown("""
    #### 🏢 企业应用
    - 需求规划
    - 供应链管理
    - 库存优化
    - 决策支持
    """)

with col3:
    st.markdown("""
    #### 🔬 研究应用
    - 算法验证
    - 模型比较
    - 数据分析
    - 效果评估
    """)

st.sidebar.success("请在上方选择一个功能模块。")

# 版本信息
st.sidebar.markdown("---")
st.sidebar.markdown("""
### 📋 版本信息
- **版本**: v2.0
- **更新时间**: 2025年8月
""")



# 页脚
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>© 2024 智链云：智能决策系统 | 专为跨境电商设计的智能决策支持平台</p>
    <p>Powered by Streamlit | Built with ❤️ for Education & Business</p>
</div>
""", unsafe_allow_html=True)
