import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# 设置随机种子以确保结果可重现
np.random.seed(42)
random.seed(42)

def generate_enhanced_orders():
    """生成增强的订单数据，包含更多维度和季节性"""
    
    # 扩展产品列表，包含更多类别
    products = {
        "女装": ["女装短袖T恤", "女装短裤", "女装连衣裙", "女装牛仔裤", "女装卫衣", "女装毛衣", "女装外套", "女装裙子"],
        "男装": ["男装短袖T恤", "男装短裤", "男装衬衫", "男装牛仔裤", "男装外套", "男装毛衣", "男装夹克"],
        "童装": ["儿童T恤", "儿童连衣裙", "儿童短裤", "儿童外套", "儿童鞋子", "儿童帽子", "儿童背包"],
        "电子产品": ["手机壳", "蓝牙耳机", "充电器", "数据线", "手机支架", "平板保护套", "智能手表"],
        "美妆用品": ["化妆品套装", "护肤品", "香水", "口红", "面膜", "洗面奶", "精华液"],
        "家居用品": ["收纳盒", "装饰画", "抱枕", "毛毯", "台灯", "花瓶", "餐具"]
    }
    
    # 展平产品列表
    all_products = []
    product_categories = {}
    for category, items in products.items():
        all_products.extend(items)
        for item in items:
            product_categories[item] = category
    
    # 生成日期范围（过去2年）
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)
    
    orders = []
    order_id = 1
    
    # 为每个产品生成订单数据
    for product in all_products:
        category = product_categories[product]
        # 每个产品生成80-300个订单
        num_orders = random.randint(80, 300)
        
        for _ in range(num_orders):
            # 随机生成订单日期
            random_days = random.randint(0, 730)
            order_date = start_date + timedelta(days=random_days)
            
            # 生成订单量（考虑季节性和趋势）
            base_quantity = random.randint(1, 25)
            
            # 添加季节性影响
            month = order_date.month
            if category in ["女装", "男装"] and month in [6, 7, 8]:  # 夏季服装
                base_quantity *= random.uniform(1.3, 2.2)
            elif category == "童装" and month in [8, 9]:  # 开学季
                base_quantity *= random.uniform(1.4, 2.0)
            elif category == "电子产品" and month in [11, 12]:  # 购物季
                base_quantity *= random.uniform(1.6, 2.8)
            elif category == "美妆用品" and month in [2, 11, 12]:  # 情人节和购物季
                base_quantity *= random.uniform(1.3, 2.1)
            elif category == "家居用品" and month in [3, 4, 10, 11]:  # 春季装修和年末
                base_quantity *= random.uniform(1.2, 1.8)
            
            # 添加周末效应
            if order_date.weekday() in [5, 6]:  # 周末
                base_quantity *= random.uniform(1.1, 1.4)
            
            quantity = max(1, int(base_quantity))
            
            # 生成价格（基于产品类别）
            price_ranges = {
                "女装": (15, 85),
                "男装": (18, 90),
                "童装": (12, 55),
                "电子产品": (8, 120),
                "美妆用品": (25, 180),
                "家居用品": (10, 75)
            }
            
            min_price, max_price = price_ranges[category]
            price = random.uniform(min_price, max_price)
            
            # 生成详细的客户地区信息
            detailed_regions = {
                '北美': {
                    '美国': ['加利福尼亚州', '纽约州', '德克萨斯州', '佛罗里达州', '伊利诺伊州', '宾夕法尼亚州', '俄亥俄州', '乔治亚州'],
                    '加拿大': ['安大略省', '魁北克省', '不列颠哥伦比亚省', '阿尔伯塔省', '马尼托巴省'],
                    '墨西哥': ['墨西哥城', '哈利斯科州', '新莱昂州', '普埃布拉州']
                },
                '欧洲': {
                    '德国': ['巴伐利亚州', '北莱茵-威斯特法伦州', '巴登-符腾堡州', '下萨克森州', '黑森州'],
                    '英国': ['英格兰', '苏格兰', '威尔士', '北爱尔兰'],
                    '法国': ['法兰西岛大区', '奥弗涅-罗纳-阿尔卑斯大区', '新阿基坦大区', '奥克西塔尼大区'],
                    '意大利': ['伦巴第大区', '拉齐奥大区', '坎帕尼亚大区', '西西里大区'],
                    '西班牙': ['马德里自治区', '加泰罗尼亚自治区', '安达卢西亚自治区', '巴伦西亚自治区']
                },
                '亚洲': {
                    '日本': ['东京都', '大阪府', '神奈川县', '爱知县', '埼玉县', '千叶县'],
                    '韩国': ['首尔特别市', '釜山广域市', '仁川广域市', '大邱广域市', '大田广域市'],
                    '新加坡': ['新加坡'],
                    '马来西亚': ['吉隆坡', '雪兰莪州', '柔佛州', '槟城州'],
                    '泰国': ['曼谷', '春武里府', '清迈府', '普吉府']
                },
                '澳洲': {
                    '澳大利亚': ['新南威尔士州', '维多利亚州', '昆士兰州', '西澳大利亚州', '南澳大利亚州'],
                    '新西兰': ['奥克兰大区', '惠灵顿大区', '坎特伯雷大区']
                },
                '南美': {
                    '巴西': ['圣保罗州', '里约热内卢州', '米纳斯吉拉斯州', '巴伊亚州'],
                    '阿根廷': ['布宜诺斯艾利斯省', '科尔多瓦省', '圣菲省'],
                    '智利': ['圣地亚哥首都大区', '瓦尔帕莱索大区', '比奥比奥大区']
                }
            }

            # 选择大区
            region_weights = [0.35, 0.25, 0.25, 0.10, 0.05]  # 北美和欧洲是主要市场
            selected_region = np.random.choice(list(detailed_regions.keys()), p=region_weights)

            # 选择国家
            countries = list(detailed_regions[selected_region].keys())
            selected_country = random.choice(countries)

            # 选择省份/州
            states = detailed_regions[selected_region][selected_country]
            selected_state = random.choice(states)
            
            orders.append({
                'order_id': order_id,
                'order_date': order_date.strftime('%Y-%m-%d'),
                'product_name': product,
                'product_category': category,
                'quantity': quantity,
                'unit_price': round(price, 2),
                'total_amount': round(price * quantity, 2),
                'customer_region': selected_region,
                'customer_country': selected_country,
                'customer_state': selected_state,
                'customer_location': f"{selected_country} - {selected_state}",
                'sales_channel': random.choice(['Amazon', 'eBay', '独立站', 'Shopify', 'Wish', 'AliExpress']),
                'customer_type': random.choice(['新客户', '老客户', 'VIP客户']),
                'shipping_method': random.choice(['标准配送', '快速配送', '经济配送']),
                'order_status': random.choice(['已完成', '已发货', '处理中', '已取消']),
                'profit_margin': round(random.uniform(0.15, 0.45), 2)  # 利润率
            })
            
            order_id += 1
    
    return pd.DataFrame(orders)

def generate_enhanced_suppliers():
    """生成增强的供应商数据"""
    
    suppliers_data = [
        {"name": "广州时尚服饰有限公司", "category": "女装", "region": "广东"},
        {"name": "深圳优质纺织厂", "category": "男装", "region": "广东"},
        {"name": "东莞精品制衣厂", "category": "童装", "region": "广东"},
        {"name": "佛山国际贸易公司", "category": "女装", "region": "广东"},
        {"name": "中山服装制造商", "category": "男装", "region": "广东"},
        {"name": "珠海时装设计工厂", "category": "女装", "region": "广东"},
        {"name": "惠州纺织品公司", "category": "家居用品", "region": "广东"},
        {"name": "江门服饰出口商", "category": "童装", "region": "广东"},
        {"name": "汕头制衣集团", "category": "女装", "region": "广东"},
        {"name": "潮州服装工厂", "category": "男装", "region": "广东"},
        {"name": "杭州丝绸企业", "category": "女装", "region": "浙江"},
        {"name": "义乌小商品公司", "category": "电子产品", "region": "浙江"},
        {"name": "宁波纺织集团", "category": "家居用品", "region": "浙江"},
        {"name": "温州制鞋厂", "category": "童装", "region": "浙江"},
        {"name": "苏州丝绸工厂", "category": "女装", "region": "江苏"},
        {"name": "南通家纺公司", "category": "家居用品", "region": "江苏"},
        {"name": "常州电子厂", "category": "电子产品", "region": "江苏"},
        {"name": "泉州制衣企业", "category": "男装", "region": "福建"},
        {"name": "厦门贸易公司", "category": "美妆用品", "region": "福建"},
        {"name": "青岛纺织厂", "category": "家居用品", "region": "山东"}
    ]
    
    supplier_list = []
    
    for supplier_info in suppliers_data:
        supplier_list.append({
            '店铺名称': supplier_info["name"],
            '店铺年份': f"{random.randint(3, 25)}年",
            '店铺评分': round(random.uniform(4.0, 5.0), 1),
            '店铺评论数量': f"{random.randint(500, 50000):,}",
            '主营产品': supplier_info["category"],
            '月产能': f"{random.randint(1000, 50000)}件",
            '最小起订量': f"{random.randint(50, 500)}件",
            '交货周期': f"{random.randint(7, 30)}天",
            '所在地区': supplier_info["region"],
            '认证情况': random.choice(['ISO9001', 'BSCI', 'WRAP', 'OEKO-TEX', '无认证']),
            '价格等级': random.choice(['低价', '中价', '高价']),
            '质量等级': random.choice(['标准', '优质', '精品']),
            '合作年限': f"{random.randint(1, 10)}年",
            '退货率': f"{round(random.uniform(0.5, 5.0), 1)}%",
            '准时交货率': f"{round(random.uniform(85, 99), 1)}%"
        })
    
    return pd.DataFrame(supplier_list)

if __name__ == "__main__":
    print("🚀 开始生成增强版数据...")
    
    # 生成增强的客户订单数据
    print("📦 生成订单数据...")
    orders_df = generate_enhanced_orders()
    orders_df.to_csv('跨境电商/data/enhanced_customer_orders.csv', index=False, encoding='utf-8')
    print(f"✅ 生成了 {len(orders_df)} 条增强订单数据")
    
    # 生成增强的供应商数据
    print("🏭 生成供应商数据...")
    suppliers_df = generate_enhanced_suppliers()
    suppliers_df.to_csv('跨境电商/data/enhanced_supplier_data.csv', index=False, encoding='utf-8')
    print(f"✅ 生成了 {len(suppliers_df)} 条增强供应商数据")
    
    print("\n📊 数据概览:")
    print("订单数据:")
    print(orders_df.head())
    print(f"\n产品种类: {orders_df['product_name'].nunique()}")
    print(f"产品类别: {orders_df['product_category'].unique()}")
    print(f"日期范围: {orders_df['order_date'].min()} 到 {orders_df['order_date'].max()}")
    print(f"客户地区: {orders_df['customer_region'].unique()}")
    
    print("\n供应商数据:")
    print(suppliers_df.head())
    print(f"\n供应商数量: {len(suppliers_df)}")
    print(f"主营产品类别: {suppliers_df['主营产品'].unique()}")
    print(f"地区分布: {suppliers_df['所在地区'].unique()}")
