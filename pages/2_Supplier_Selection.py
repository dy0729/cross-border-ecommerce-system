import streamlit as st
import pandas as pd
import numpy as np
import os

st.set_page_config(page_title="供应商选择", layout="wide")

st.title("🤝 供应商选择模块")
st.write("基于多准则决策分析的智能供应商评估系统")

# 检查数据文件
data_file = 'data/enhanced_supplier_data.csv'

try:
    # 显示当前目录信息
    st.info(f"📁 当前工作目录：{os.getcwd()}")
    
    # 检查文件是否存在
    if os.path.exists(data_file):
        st.success(f"✅ 找到数据文件：{data_file}")
        
        # 加载数据
        df = pd.read_csv(data_file)
        
        # 数据清洗
        if '店铺评论数量' in df.columns:
            df['店铺评论数量'] = df['店铺评论数量'].astype(str).str.replace(',', '').astype(int)

        # 清理店铺年份列（移除"年"字符）
        if '店铺年份' in df.columns:
            df['店铺年份'] = df['店铺年份'].astype(str).str.replace('年', '').astype(float)
        
        st.success("✅ 数据加载成功！")
        
        # 显示数据概览
        st.subheader("📊 供应商数据概览")
        st.dataframe(df)
        
        # 基本统计信息
        st.subheader("📈 数据统计")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("供应商总数", len(df))
        
        with col2:
            avg_rating = df['店铺评分'].mean()
            st.metric("平均评分", f"{avg_rating:.2f}")
        
        with col3:
            avg_years = df['店铺年份'].mean()
            st.metric("平均经营年限", f"{avg_years:.1f}年")
        
        with col4:
            total_reviews = df['店铺评论数量'].sum()
            st.metric("总评论数", f"{total_reviews:,}")
        
        # 简单的供应商排名
        st.subheader("🏆 供应商简单排名")
        
        # 计算综合得分（简化版本）
        df_score = df.copy()
        
        # 标准化各项指标（0-1范围）
        df_score['年份得分'] = (df['店铺年份'] - df['店铺年份'].min()) / (df['店铺年份'].max() - df['店铺年份'].min())
        df_score['评分得分'] = (df['店铺评分'] - df['店铺评分'].min()) / (df['店铺评分'].max() - df['店铺评分'].min())
        df_score['评论得分'] = (df['店铺评论数量'] - df['店铺评论数量'].min()) / (df['店铺评论数量'].max() - df['店铺评论数量'].min())
        
        # 计算综合得分（等权重）
        df_score['综合得分'] = (df_score['年份得分'] + df_score['评分得分'] + df_score['评论得分']) / 3
        
        # 排序
        df_ranked = df_score.sort_values('综合得分', ascending=False).reset_index(drop=True)
        df_ranked['排名'] = range(1, len(df_ranked) + 1)
        
        # 显示排名结果
        display_cols = ['排名', '店铺名称', '店铺年份', '店铺评分', '店铺评论数量', '综合得分']
        st.dataframe(df_ranked[display_cols].round(3))
        
        # 推荐供应商
        st.subheader("⭐ 推荐供应商")
        top_supplier = df_ranked.iloc[0]
        
        st.success(f"""
        **推荐供应商：{top_supplier['店铺名称']}**
        
        - 🏆 排名：第 {top_supplier['排名']} 名
        - ⭐ 评分：{top_supplier['店铺评分']} 分
        - 📅 经营年限：{top_supplier['店铺年份']} 年
        - 💬 评论数量：{top_supplier['店铺评论数量']:,} 条
        - 📊 综合得分：{top_supplier['综合得分']:.3f}
        """)
        
    else:
        st.error(f"❌ 未找到数据文件：{data_file}")
        st.write("📂 当前目录内容：")
        if os.path.exists('.'):
            for item in os.listdir('.'):
                st.write(f"  - {item}")
        
        # 智能供应商匹配
        st.subheader("🤖 智能供应商匹配系统")

        # 加载爬取的供应商数据
        try:
            crawled_df = pd.read_csv('data/crawled_suppliers.csv')
            st.success(f"✅ 加载了 {len(crawled_df)} 条爬取的供应商数据")

            # 合并数据源
            all_suppliers = pd.concat([df, crawled_df], ignore_index=True)
            st.info(f"📊 总供应商数据: {len(all_suppliers)} 条")

        except FileNotFoundError:
            st.warning("⚠️ 未找到爬取的供应商数据，仅使用本地数据")
            all_suppliers = df

        # 需求输入
        st.markdown("### 📝 输入您的采购需求")

        col1, col2, col3 = st.columns(3)

        with col1:
            required_category = st.selectbox(
                "产品类别",
                ["女装", "男装", "童装", "电子产品", "美妆用品", "家居用品"]
            )

        with col2:
            required_quantity = st.number_input(
                "需求数量 (件)",
                min_value=1,
                max_value=100000,
                value=1000
            )

        with col3:
            max_delivery_time = st.slider(
                "最大交货时间 (天)",
                min_value=5,
                max_value=60,
                value=20
            )

        if st.button("🔍 开始智能匹配", type="primary"):
            # 筛选符合条件的供应商
            filtered_suppliers = all_suppliers.copy()

            # 筛选产品类别
            if '主营产品' in filtered_suppliers.columns:
                filtered_suppliers = filtered_suppliers[
                    filtered_suppliers['主营产品'] == required_category
                ]

            if len(filtered_suppliers) > 0:
                st.success(f"🎯 找到 {len(filtered_suppliers)} 家 {required_category} 类别的供应商")

                # 显示筛选结果
                display_columns = ['店铺名称', '店铺评分', '月产能', '最小起订量', '交货周期', '所在地区']
                available_columns = [col for col in display_columns if col in filtered_suppliers.columns]

                if available_columns:
                    st.dataframe(filtered_suppliers[available_columns].head(20), use_container_width=True)
                else:
                    st.dataframe(filtered_suppliers.head(20), use_container_width=True)

            else:
                st.error(f"😔 没有找到主营 '{required_category}' 的供应商")

        if os.path.exists('data'):
            st.write("📂 data 目录内容：")
            for item in os.listdir('data'):
                st.write(f"  - {item}")
        else:
            st.error("❌ data 目录不存在")

except Exception as e:
    st.error(f"❌ 发生错误：{e}")
    import traceback
    st.code(traceback.format_exc())
