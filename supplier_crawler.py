import pandas as pd
import numpy as np
import random
import time
from datetime import datetime
import json

class SupplierCrawler:
    """供应商数据爬虫类 - 模拟从多个平台获取供应商数据"""
    
    def __init__(self):
        self.platforms = {
            "1688": "https://www.1688.com",
            "阿里巴巴": "https://www.alibaba.com", 
            "慧聪网": "https://www.hc360.com",
            "中国制造网": "https://www.made-in-china.com"
        }
        
        # 模拟真实的供应商数据模板
        self.real_suppliers_template = [
            {
                "platform": "1688",
                "name": "广州市白云区时尚服饰厂",
                "category": "女装",
                "location": "广东广州",
                "years": 8,
                "rating": 4.7,
                "reviews": 15680,
                "min_order": 100,
                "capacity": 50000,
                "delivery_time": 7,
                "certifications": ["BSCI", "ISO9001"],
                "price_level": "中价",
                "quality_level": "优质"
            },
            {
                "platform": "阿里巴巴",
                "name": "深圳市龙华新区优质电子厂",
                "category": "电子产品", 
                "location": "广东深圳",
                "years": 12,
                "rating": 4.8,
                "reviews": 28900,
                "min_order": 500,
                "capacity": 100000,
                "delivery_time": 10,
                "certifications": ["CE", "FCC", "RoHS"],
                "price_level": "低价",
                "quality_level": "标准"
            },
            {
                "platform": "1688",
                "name": "义乌市小商品批发中心",
                "category": "家居用品",
                "location": "浙江义乌",
                "years": 15,
                "rating": 4.5,
                "reviews": 45200,
                "min_order": 200,
                "capacity": 80000,
                "delivery_time": 5,
                "certifications": ["ISO9001"],
                "price_level": "低价",
                "quality_level": "标准"
            }
        ]
    
    def simulate_crawl_1688(self, category, max_results=20):
        """模拟从1688爬取供应商数据"""
        print(f"🕷️ 正在爬取1688平台 - {category}类别供应商...")
        time.sleep(1)  # 模拟网络延迟
        
        suppliers = []
        base_names = [
            "广州时尚", "深圳优质", "东莞精品", "佛山国际", "中山制造",
            "珠海设计", "惠州纺织", "江门出口", "汕头集团", "潮州工厂"
        ]
        
        suffixes = ["有限公司", "制造厂", "贸易公司", "工厂", "企业", "集团"]
        
        for i in range(max_results):
            name = f"{random.choice(base_names)}{category}{random.choice(suffixes)}"
            
            supplier = {
                "platform": "1688",
                "name": name,
                "category": category,
                "location": random.choice(["广东", "浙江", "江苏", "福建", "山东"]),
                "years": random.randint(3, 20),
                "rating": round(random.uniform(4.0, 5.0), 1),
                "reviews": random.randint(1000, 50000),
                "min_order": random.randint(50, 1000),
                "capacity": random.randint(5000, 100000),
                "delivery_time": random.randint(5, 25),
                "certifications": random.sample(["ISO9001", "BSCI", "WRAP", "OEKO-TEX", "CE", "FCC"], 
                                              random.randint(1, 3)),
                "price_level": random.choice(["低价", "中价", "高价"]),
                "quality_level": random.choice(["标准", "优质", "精品"]),
                "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            suppliers.append(supplier)
        
        return suppliers
    
    def simulate_crawl_alibaba(self, category, max_results=15):
        """模拟从阿里巴巴爬取供应商数据"""
        print(f"🕷️ 正在爬取阿里巴巴平台 - {category}类别供应商...")
        time.sleep(1.5)  # 模拟网络延迟
        
        suppliers = []
        regions = ["Guangdong", "Zhejiang", "Jiangsu", "Fujian", "Shandong"]
        
        for i in range(max_results):
            name = f"{category} Manufacturer Co., Ltd"
            
            supplier = {
                "platform": "阿里巴巴",
                "name": name,
                "category": category,
                "location": random.choice(regions),
                "years": random.randint(5, 25),
                "rating": round(random.uniform(4.2, 5.0), 1),
                "reviews": random.randint(2000, 80000),
                "min_order": random.randint(100, 2000),
                "capacity": random.randint(10000, 200000),
                "delivery_time": random.randint(7, 30),
                "certifications": random.sample(["ISO9001", "BSCI", "WRAP", "CE", "FCC", "RoHS"], 
                                              random.randint(2, 4)),
                "price_level": random.choice(["低价", "中价", "高价"]),
                "quality_level": random.choice(["标准", "优质", "精品"]),
                "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "export_experience": True,
                "trade_assurance": True
            }
            suppliers.append(supplier)
        
        return suppliers
    
    def crawl_suppliers_by_category(self, category, total_results=50):
        """按类别爬取供应商数据"""
        all_suppliers = []
        
        # 从不同平台爬取数据
        suppliers_1688 = self.simulate_crawl_1688(category, max_results=total_results//2)
        suppliers_alibaba = self.simulate_crawl_alibaba(category, max_results=total_results//2)
        
        all_suppliers.extend(suppliers_1688)
        all_suppliers.extend(suppliers_alibaba)
        
        # 添加一些真实模板数据
        for template in self.real_suppliers_template:
            if template["category"] == category:
                all_suppliers.append(template.copy())
        
        return all_suppliers
    
    def crawl_all_categories(self):
        """爬取所有类别的供应商数据"""
        categories = ["女装", "男装", "童装", "电子产品", "美妆用品", "家居用品"]
        all_data = []
        
        print("🚀 开始全面爬取供应商数据...")
        
        for category in categories:
            print(f"\n📂 处理类别: {category}")
            suppliers = self.crawl_suppliers_by_category(category, total_results=30)
            all_data.extend(suppliers)
            
            # 模拟爬取间隔
            time.sleep(0.5)
        
        return all_data
    
    def save_to_dataframe(self, suppliers_data):
        """将爬取的数据转换为DataFrame格式"""
        processed_data = []
        
        for supplier in suppliers_data:
            processed_supplier = {
                '店铺名称': supplier['name'],
                '平台来源': supplier['platform'],
                '店铺年份': f"{supplier['years']}年",
                '店铺评分': supplier['rating'],
                '店铺评论数量': f"{supplier['reviews']:,}",
                '主营产品': supplier['category'],
                '月产能': f"{supplier['capacity']}件",
                '最小起订量': f"{supplier['min_order']}件",
                '交货周期': f"{supplier['delivery_time']}天",
                '所在地区': supplier['location'],
                '认证情况': ', '.join(supplier['certifications']) if supplier['certifications'] else '无认证',
                '价格等级': supplier['price_level'],
                '质量等级': supplier['quality_level'],
                '爬取时间': supplier.get('crawl_time', datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                '合作年限': f"{random.randint(1, supplier['years'])}年",
                '退货率': f"{round(random.uniform(0.5, 5.0), 1)}%",
                '准时交货率': f"{round(random.uniform(85, 99), 1)}%"
            }
            
            # 添加特殊字段（如果存在）
            if 'export_experience' in supplier:
                processed_supplier['出口经验'] = '是' if supplier['export_experience'] else '否'
            if 'trade_assurance' in supplier:
                processed_supplier['贸易保障'] = '是' if supplier['trade_assurance'] else '否'
            
            processed_data.append(processed_supplier)
        
        return pd.DataFrame(processed_data)
    
    def update_supplier_database(self, output_file='跨境电商/data/crawled_suppliers.csv'):
        """更新供应商数据库"""
        print("🔄 开始更新供应商数据库...")
        
        # 爬取最新数据
        suppliers_data = self.crawl_all_categories()
        
        # 转换为DataFrame
        df = self.save_to_dataframe(suppliers_data)
        
        # 保存到文件
        df.to_csv(output_file, index=False, encoding='utf-8')
        
        print(f"✅ 成功爬取并保存了 {len(df)} 条供应商数据到 {output_file}")
        
        # 显示统计信息
        print("\n📊 爬取数据统计:")
        print(f"总供应商数量: {len(df)}")
        print(f"平台分布: {df['平台来源'].value_counts().to_dict()}")
        print(f"类别分布: {df['主营产品'].value_counts().to_dict()}")
        print(f"地区分布: {df['所在地区'].value_counts().to_dict()}")
        
        return df

def main():
    """主函数 - 演示爬虫功能"""
    crawler = SupplierCrawler()
    
    # 更新供应商数据库
    df = crawler.update_supplier_database()
    
    # 显示前几条数据
    print("\n📋 爬取数据预览:")
    print(df.head())
    
    return df

if __name__ == "__main__":
    main()
