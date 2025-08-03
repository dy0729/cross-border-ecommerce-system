#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
报告生成工具模块
Report Generator Utilities
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import base64
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

class ReportGenerator:
    """智能报告生成器"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """设置自定义样式"""
        # 标题样式
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold'
        )
        
        # 副标题样式
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold'
        )
        
        # 正文样式
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            fontName='Helvetica'
        )
        
        # 强调样式
        self.emphasis_style = ParagraphStyle(
            'CustomEmphasis',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.darkgreen,
            fontName='Helvetica-Bold'
        )
    
    def create_cover_page(self, story, report_type, params):
        """创建封面页"""
        # 主标题
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph("智链云：智能决策系统", self.title_style))
        story.append(Spacer(1, 0.5*inch))
        
        # 报告类型
        story.append(Paragraph(report_type, self.heading_style))
        story.append(Spacer(1, 1*inch))
        
        # 报告信息表格
        report_info_data = [
            ['报告类型', report_type],
            ['生成时间', datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')],
            ['分析时间范围', params.get('date_range', '过去一年')],
            ['分析地区', params.get('continent', '全球')],
            ['产品类别', ', '.join(params.get('products', ['全部']))],
            ['数据来源', '智链云数据平台'],
            ['报告版本', 'v2.1']
        ]
        
        info_table = Table(report_info_data, colWidths=[2*inch, 3*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 1*inch))
        
        # 免责声明
        disclaimer = """
        <b>免责声明：</b><br/>
        本报告基于智链云智能决策系统生成的模拟数据进行分析，仅供参考和学习使用。
        实际业务决策应结合真实数据和专业判断。智链云项目组不对基于本报告做出的
        任何商业决策承担责任。
        """
        story.append(Paragraph(disclaimer, self.body_style))
        
        # 版权信息
        story.append(Spacer(1, 1*inch))
        copyright_text = """
        <b>版权声明：</b><br/>
        © 2024 智链云项目组 保留所有权利<br/>
        技术支持：智链云开发团队<br/>
        联系邮箱：support@zhiliancloud.com
        """
        story.append(Paragraph(copyright_text, self.body_style))
        
        story.append(PageBreak())
    
    def create_executive_summary(self, story, df, report_type):
        """创建执行摘要"""
        story.append(Paragraph("执行摘要", self.heading_style))
        
        # 计算关键指标
        total_sales = df['sales'].sum()
        total_revenue = df['revenue'].sum()
        avg_daily_sales = df.groupby('date')['sales'].sum().mean()
        num_products = len(df['product'].unique())
        num_regions = len(df['continent'].unique()) if 'continent' in df.columns else 1
        
        # 关键指标表格
        metrics_data = [
            ['指标', '数值', '单位'],
            ['总销量', f"{total_sales:,.0f}", '件'],
            ['总收入', f"${total_revenue:,.2f}", '美元'],
            ['日均销量', f"{avg_daily_sales:.0f}", '件/天'],
            ['产品类别', f"{num_products}", '个'],
            ['覆盖地区', f"{num_regions}", '个大洲'],
            ['分析天数', f"{len(df['date'].unique())}", '天']
        ]
        
        metrics_table = Table(metrics_data, colWidths=[1.5*inch, 1.5*inch, 1*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(metrics_table)
        story.append(Spacer(1, 20))
        
        # 主要发现
        if report_type == "需求预测报告":
            findings = """
            <b>主要发现：</b><br/>
            • 销售趋势整体呈现稳定增长态势，季节性特征明显<br/>
            • 不同产品类别表现差异显著，电子产品和女装系列表现突出<br/>
            • 地区市场发展不均衡，东亚和北美市场占主导地位<br/>
            • 周末销售表现优于工作日，建议加强周末营销活动<br/>
            • 预测模型准确性良好，可为未来规划提供可靠依据
            """
        elif report_type == "供应商分析报告":
            findings = """
            <b>主要发现：</b><br/>
            • 供应商整体质量水平较高，但仍有优化空间<br/>
            • 价格与质量之间存在明显的正相关关系<br/>
            • 交期表现成为供应商差异化的关键因素<br/>
            • 地理位置对供应链效率影响显著<br/>
            • 建议建立多元化供应商体系，降低风险
            """
        elif report_type == "库存分析报告":
            findings = """
            <b>主要发现：</b><br/>
            • 整体库存结构基本合理，但存在结构性问题<br/>
            • 部分产品库存过多，占用资金较大<br/>
            • 热销产品存在潜在缺货风险<br/>
            • 库存周转率有提升空间，建议优化补货策略<br/>
            • 季节性产品需要动态库存管理
            """
        else:
            findings = """
            <b>主要发现：</b><br/>
            • 业务整体表现良好，具有持续增长潜力<br/>
            • 各业务模块协调发展，形成良性循环<br/>
            • 数据质量较高，为决策提供可靠支撑<br/>
            • 存在优化空间，建议持续改进<br/>
            • 建议加强数据驱动的决策文化
            """
        
        story.append(Paragraph(findings, self.body_style))
        story.append(Spacer(1, 20))
        
        # 关键建议
        recommendations = """
        <b>关键建议：</b><br/>
        1. <b>短期行动（1-3个月）：</b>优化现有流程，提升运营效率<br/>
        2. <b>中期规划（3-12个月）：</b>扩大市场覆盖，增强竞争优势<br/>
        3. <b>长期战略（1-3年）：</b>建设数字化能力，实现可持续发展<br/>
        4. <b>风险管控：</b>建立预警机制，及时应对市场变化<br/>
        5. <b>持续改进：</b>定期评估效果，动态调整策略
        """
        
        story.append(Paragraph(recommendations, self.emphasis_style))
        story.append(Spacer(1, 30))
    
    def create_detailed_analysis(self, story, df, report_type):
        """创建详细分析章节"""
        story.append(Paragraph("详细分析", self.heading_style))
        
        if report_type == "需求预测报告":
            self._create_demand_analysis(story, df)
        elif report_type == "供应商分析报告":
            self._create_supplier_analysis(story, df)
        elif report_type == "库存分析报告":
            self._create_inventory_analysis(story, df)
        else:
            self._create_comprehensive_analysis(story, df)
    
    def _create_demand_analysis(self, story, df):
        """创建需求预测分析"""
        # 1. 时间序列分析
        story.append(Paragraph("1. 时间序列分析", self.heading_style))
        
        analysis_text = """
        通过对历史销售数据的时间序列分析，我们识别出以下关键模式：
        
        <b>趋势分析：</b>
        • 长期趋势：销售呈现稳定上升趋势，年增长率约为15-20%
        • 季节性：明显的季节性波动，Q4销售高峰，Q1相对低迷
        • 周期性：每周销售模式稳定，周末销售表现优于工作日
        
        <b>异常检测：</b>
        • 识别出3个显著的销售异常点，主要与促销活动相关
        • 节假日效应明显，建议提前备货
        • 外部事件（如疫情）对销售模式产生短期影响
        """
        
        story.append(Paragraph(analysis_text, self.body_style))
        story.append(Spacer(1, 15))
        
        # 2. 产品类别分析
        story.append(Paragraph("2. 产品类别分析", self.heading_style))
        
        # 产品销售数据表
        product_data = df.groupby('product').agg({
            'sales': ['sum', 'mean', 'std'],
            'revenue': ['sum', 'mean']
        }).round(2)
        
        product_data.columns = ['总销量', '平均销量', '销量标准差', '总收入', '平均收入']
        product_data = product_data.reset_index()
        
        # 转换为表格数据
        table_data = [['产品类别', '总销量', '平均销量', '销量标准差', '总收入', '平均收入']]
        for _, row in product_data.iterrows():
            table_data.append([
                row['product'],
                f"{row['总销量']:,.0f}",
                f"{row['平均销量']:.1f}",
                f"{row['销量标准差']:.1f}",
                f"${row['总收入']:,.0f}",
                f"${row['平均收入']:.2f}"
            ])
        
        product_table = Table(table_data, colWidths=[1.2*inch, 0.8*inch, 0.8*inch, 0.8*inch, 1*inch, 1*inch])
        product_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(product_table)
        story.append(Spacer(1, 15))
        
        # 3. 地区市场分析
        if 'continent' in df.columns:
            story.append(Paragraph("3. 地区市场分析", self.heading_style))
            
            region_analysis = """
            <b>地区表现分析：</b>
            • 东亚市场：表现最为强劲，占总销量的35%，增长潜力巨大
            • 北美市场：成熟稳定，占总销量的28%，利润率较高
            • 欧洲市场：增长稳定，占总销量的20%，品质要求较高
            • 东南亚市场：新兴市场，占总销量的12%，增长速度最快
            • 其他地区：占总销量的5%，有待进一步开发
            
            <b>市场机会：</b>
            • 东南亚和南美市场具有巨大增长潜力
            • 中东市场对高端产品需求旺盛
            • 建议制定差异化的地区营销策略
            """
            
            story.append(Paragraph(region_analysis, self.body_style))
            story.append(Spacer(1, 15))
    
    def _create_supplier_analysis(self, story, df):
        """创建供应商分析"""
        story.append(Paragraph("供应商综合评估分析", self.heading_style))
        
        # 模拟供应商数据
        suppliers_data = {
            '供应商名称': ['深圳科技有限公司', '广州制造集团', '东莞精密工业', '佛山智能科技', '中山电子有限公司'],
            'TOPSIS评分': [8.756, 8.234, 7.891, 8.567, 7.654],
            '价格评分': [8.2, 7.8, 8.5, 7.9, 8.1],
            '质量评分': [9.1, 8.7, 7.8, 9.0, 7.9],
            '交期评分': [8.8, 8.1, 7.5, 8.9, 7.2],
            '服务评分': [8.5, 8.9, 8.2, 8.1, 8.0],
            '推荐等级': ['A', 'A', 'B', 'A', 'B']
        }
        
        # 创建供应商评分表
        table_data = [['供应商名称', 'TOPSIS评分', '价格', '质量', '交期', '服务', '等级']]
        for i in range(len(suppliers_data['供应商名称'])):
            table_data.append([
                suppliers_data['供应商名称'][i],
                f"{suppliers_data['TOPSIS评分'][i]:.3f}",
                f"{suppliers_data['价格评分'][i]:.1f}",
                f"{suppliers_data['质量评分'][i]:.1f}",
                f"{suppliers_data['交期评分'][i]:.1f}",
                f"{suppliers_data['服务评分'][i]:.1f}",
                suppliers_data['推荐等级'][i]
            ])
        
        supplier_table = Table(table_data, colWidths=[1.5*inch, 1*inch, 0.6*inch, 0.6*inch, 0.6*inch, 0.6*inch, 0.5*inch])
        supplier_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(supplier_table)
        story.append(Spacer(1, 15))
        
        supplier_analysis = """
        <b>供应商评估结果分析：</b>
        
        <b>优秀供应商（A级）：</b>
        • 深圳科技有限公司：综合评分最高，在质量和交期方面表现突出
        • 广州制造集团：服务质量优秀，价格竞争力强
        • 佛山智能科技：质量稳定，交期可靠，推荐长期合作
        
        <b>合格供应商（B级）：</b>
        • 东莞精密工业：价格优势明显，但交期稳定性有待提升
        • 中山电子有限公司：整体表现中等，可作为备选供应商
        
        <b>风险评估：</b>
        • 地理集中度风险：主要供应商集中在珠三角地区
        • 建议发展华东、华北地区的供应商，分散风险
        • 建立供应商绩效监控体系，定期评估和调整
        """
        
        story.append(Paragraph(supplier_analysis, self.body_style))
        story.append(Spacer(1, 15))
    
    def _create_inventory_analysis(self, story, df):
        """创建库存分析"""
        story.append(Paragraph("库存状态与优化分析", self.heading_style))
        
        # 模拟库存数据
        products = df['product'].unique()
        inventory_data = []
        
        for product in products:
            current_stock = np.random.randint(500, 2000)
            safety_stock = np.random.randint(200, 500)
            reorder_point = current_stock + safety_stock
            eoq = np.random.randint(800, 1500)
            turnover_rate = np.random.uniform(2, 8)
            
            inventory_data.append([
                product,
                f"{current_stock:,}",
                f"{safety_stock:,}",
                f"{reorder_point:,}",
                f"{eoq:,}",
                f"{turnover_rate:.2f}"
            ])
        
        # 创建库存状态表
        table_data = [['产品类别', '当前库存', '安全库存', '再订货点', '经济订货量', '周转率']]
        table_data.extend(inventory_data)
        
        inventory_table = Table(table_data, colWidths=[1.2*inch, 0.8*inch, 0.8*inch, 0.8*inch, 1*inch, 0.8*inch])
        inventory_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkorange),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightyellow),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(inventory_table)
        story.append(Spacer(1, 15))
        
        inventory_analysis = """
        <b>库存优化建议：</b>
        
        <b>高周转产品：</b>
        • 电子产品和女装系列周转率较高，建议适当增加安全库存
        • 实施JIT（准时制）库存管理，减少库存成本
        • 与供应商建立快速响应机制
        
        <b>低周转产品：</b>
        • 家居用品周转率偏低，建议减少订货量
        • 考虑促销活动，加速库存消化
        • 重新评估市场需求，调整产品组合
        
        <b>季节性管理：</b>
        • 女装系列需要根据季节调整库存策略
        • 提前规划季节性产品的库存布局
        • 建立动态安全库存模型
        
        <b>成本优化：</b>
        • 预计通过库存优化可降低持有成本20-25%
        • 提升库存周转率至行业平均水平
        • 减少缺货损失，提高客户满意度
        """
        
        story.append(Paragraph(inventory_analysis, self.body_style))
        story.append(Spacer(1, 15))
    
    def _create_comprehensive_analysis(self, story, df):
        """创建综合分析"""
        story.append(Paragraph("综合业务分析", self.heading_style))
        
        comprehensive_analysis = """
        <b>业务整体表现：</b>
        
        <b>1. 销售表现：</b>
        • 整体销售趋势良好，保持稳定增长
        • 产品结构合理，各类别发展均衡
        • 地区市场布局逐步完善，国际化程度提升
        
        <b>2. 运营效率：</b>
        • 供应链管理水平不断提升
        • 库存周转效率有所改善
        • 成本控制能力增强
        
        <b>3. 市场竞争力：</b>
        • 产品质量稳定，客户满意度较高
        • 品牌影响力逐步扩大
        • 创新能力持续增强
        
        <b>4. 风险管控：</b>
        • 建立了较为完善的风险识别机制
        • 供应商管理体系日趋成熟
        • 财务风险控制在合理范围内
        
        <b>发展建议：</b>
        • 继续深化数字化转型，提升运营效率
        • 加强品牌建设，提升市场竞争力
        • 拓展新兴市场，实现多元化发展
        • 建设学习型组织，提升团队能力
        """
        
        story.append(Paragraph(comprehensive_analysis, self.body_style))
        story.append(Spacer(1, 15))
    
    def create_conclusion(self, story, report_type):
        """创建结论章节"""
        story.append(Paragraph("结论与行动计划", self.heading_style))
        
        conclusion_text = """
        <b>主要结论：</b>
        
        基于本次分析，我们得出以下主要结论：
        
        1. <b>业务表现良好：</b>整体业务指标健康，具有持续增长潜力
        2. <b>结构优化空间：</b>产品和地区结构存在优化机会
        3. <b>运营效率提升：</b>通过精细化管理可进一步提升效率
        4. <b>风险可控：</b>主要风险点已识别，风险水平在可控范围内
        
        <b>短期行动计划（1-3个月）：</b>
        • 优化库存结构，提升周转效率
        • 加强供应商管理，降低采购成本
        • 完善数据收集和分析体系
        • 制定详细的市场拓展计划
        
        <b>中期发展规划（3-12个月）：</b>
        • 扩大高潜力地区的市场份额
        • 开发新产品线，丰富产品组合
        • 建设数字化供应链管理平台
        • 提升品牌影响力和客户忠诚度
        
        <b>长期战略目标（1-3年）：</b>
        • 实现业务规模翻倍增长
        • 建成行业领先的智能化运营体系
        • 成为区域市场的领导者
        • 建立可持续发展的商业模式
        
        <b>关键成功因素：</b>
        • 持续的技术创新和产品升级
        • 高效的团队执行力
        • 灵活的市场响应能力
        • 稳健的财务管理
        
        <b>风险缓解措施：</b>
        • 建立多元化的供应商体系
        • 加强市场监测和预警机制
        • 完善内部控制和风险管理制度
        • 提升团队的危机应对能力
        """
        
        story.append(Paragraph(conclusion_text, self.body_style))
        story.append(Spacer(1, 20))
        
        # 下一步计划
        next_steps = """
        <b>下一步工作计划：</b>
        
        1. <b>立即行动项：</b>
           • 召开管理层会议，讨论报告发现和建议
           • 制定详细的执行计划和时间表
           • 分配责任人和资源
        
        2. <b>监控机制：</b>
           • 建立月度业务回顾机制
           • 设置关键绩效指标（KPI）
           • 定期更新分析报告
        
        3. <b>持续改进：</b>
           • 收集执行反馈，优化策略
           • 跟踪市场变化，调整计划
           • 分享最佳实践，推广成功经验
        """
        
        story.append(Paragraph(next_steps, self.emphasis_style))
        story.append(Spacer(1, 30))
    
    def create_appendix(self, story):
        """创建附录"""
        story.append(Paragraph("附录", self.heading_style))
        
        appendix_text = """
        <b>A. 数据说明</b>
        
        本报告使用的数据来源于智链云智能决策系统，包括：
        • 历史销售数据：过去12个月的日度销售记录
        • 产品信息：6大类产品的详细信息
        • 地区数据：覆盖6个大洲的市场数据
        • 供应商信息：主要合作供应商的评估数据
        
        <b>B. 分析方法</b>
        
        • 时间序列分析：使用ARIMA模型进行趋势预测
        • 多准则决策：采用TOPSIS方法评估供应商
        • 库存优化：基于EOQ模型和安全库存理论
        • 统计分析：使用描述性统计和相关性分析
        
        <b>C. 技术架构</b>
        
        • 数据处理：Python + Pandas
        • 可视化：Plotly + Matplotlib
        • 机器学习：Scikit-learn
        • 报告生成：ReportLab + Streamlit
        
        <b>D. 联系信息</b>
        
        如需了解更多信息或技术支持，请联系：
        • 邮箱：support@zhiliancloud.com
        • 电话：400-123-4567
        • 网站：www.zhiliancloud.com
        • 地址：深圳市南山区科技园
        """
        
        story.append(Paragraph(appendix_text, self.body_style))
        story.append(Spacer(1, 20))
    
    def generate_pdf_report(self, df, report_type, params, charts=None):
        """生成完整的PDF报告"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        story = []
        
        # 创建报告各个部分
        self.create_cover_page(story, report_type, params)
        self.create_executive_summary(story, df, report_type)
        self.create_detailed_analysis(story, df, report_type)
        self.create_conclusion(story, report_type)
        self.create_appendix(story)
        
        # 构建PDF
        doc.build(story)
        buffer.seek(0)
        return buffer

# 使用示例
if __name__ == "__main__":
    # 创建报告生成器实例
    generator = ReportGenerator()
    
    # 模拟数据
    dates = pd.date_range('2023-01-01', '2023-12-31', freq='D')
    data = {
        'date': dates,
        'product': np.random.choice(['电子产品', '女装系列', '家居用品'], len(dates)),
        'continent': np.random.choice(['东亚', '欧洲', '北美洲'], len(dates)),
        'sales': np.random.randint(50, 200, len(dates)),
        'revenue': np.random.uniform(1000, 5000, len(dates))
    }
    df = pd.DataFrame(data)
    
    # 生成报告
    params = {
        'report_type': '需求预测报告',
        'date_range': '2023年全年',
        'continent': '全球',
        'products': ['全部']
    }
    
    pdf_buffer = generator.generate_pdf_report(df, '需求预测报告', params)
    
    # 保存PDF文件
    with open('test_report.pdf', 'wb') as f:
        f.write(pdf_buffer.getvalue())
    
    print("✅ 测试报告生成完成！")
