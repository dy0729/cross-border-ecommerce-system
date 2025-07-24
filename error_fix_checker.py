import os
import re
import glob

def check_and_fix_plotly_errors():
    """检查和修复Plotly相关错误"""
    print("🔍 检查Plotly方法错误...")
    
    # 常见的错误映射
    error_mappings = {
        'update_xaxis': 'update_xaxes',
        'update_yaxis': 'update_yaxes',
        'update_layout': 'update_layout',  # 这个是正确的
    }
    
    files = glob.glob('跨境电商/pages/*.py')
    fixes_made = 0
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # 检查和修复错误
            for wrong_method, correct_method in error_mappings.items():
                if wrong_method in content and wrong_method != correct_method:
                    # 使用正则表达式精确匹配方法调用
                    pattern = rf'\.{wrong_method}\('
                    replacement = f'.{correct_method}('
                    
                    if re.search(pattern, content):
                        content = re.sub(pattern, replacement, content)
                        print(f"✅ 修复 {file_path}: {wrong_method} -> {correct_method}")
                        fixes_made += 1
            
            # 如果有修改，写回文件
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"💾 已保存修复: {file_path}")
        
        except Exception as e:
            print(f"❌ 处理文件失败 {file_path}: {e}")
    
    return fixes_made

def check_pandas_errors():
    """检查Pandas相关错误"""
    print("\n🔍 检查Pandas方法错误...")
    
    files = glob.glob('跨境电商/pages/*.py')
    issues_found = 0
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines, 1):
                # 检查pd.to_numeric没有errors参数
                if 'pd.to_numeric' in line and 'errors=' not in line and '(' in line:
                    print(f"⚠️ {file_path}:{i} - pd.to_numeric可能需要errors参数")
                    issues_found += 1
                
                # 检查日期转换
                if 'pd.to_datetime' in line and 'errors=' not in line and '(' in line:
                    print(f"💡 {file_path}:{i} - pd.to_datetime建议添加errors参数")
        
        except Exception as e:
            print(f"❌ 检查文件失败 {file_path}: {e}")
    
    return issues_found

def check_streamlit_errors():
    """检查Streamlit相关错误"""
    print("\n🔍 检查Streamlit使用错误...")
    
    files = glob.glob('跨境电商/pages/*.py')
    issues_found = 0
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否缺少streamlit导入
            if 'st.' in content and 'import streamlit' not in content:
                print(f"❌ {file_path} - 缺少streamlit导入")
                issues_found += 1
            
            # 检查是否有重复的page_config设置
            page_config_count = content.count('st.set_page_config')
            if page_config_count > 1:
                print(f"⚠️ {file_path} - 多次设置page_config ({page_config_count}次)")
                issues_found += 1
        
        except Exception as e:
            print(f"❌ 检查文件失败 {file_path}: {e}")
    
    return issues_found

def check_data_loading_errors():
    """检查数据加载错误"""
    print("\n🔍 检查数据加载错误...")
    
    required_files = [
        '跨境电商/data/enhanced_customer_orders.csv',
        '跨境电商/data/enhanced_supplier_data.csv',
        '跨境电商/data/crawled_suppliers.csv'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ 缺少数据文件:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return len(missing_files)
    else:
        print("✅ 所有数据文件存在")
        return 0

def check_import_errors():
    """检查导入错误"""
    print("\n🔍 检查导入错误...")
    
    files = glob.glob('跨境电商/pages/*.py')
    issues_found = 0
    
    required_imports = {
        'streamlit': ['st.'],
        'pandas': ['pd.', 'DataFrame', 'Series'],
        'numpy': ['np.', 'numpy'],
        'plotly.express': ['px.'],
        'plotly.graph_objects': ['go.'],
    }
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for module, usage_patterns in required_imports.items():
                # 检查是否使用了模块但没有导入
                module_used = any(pattern in content for pattern in usage_patterns)
                module_imported = f'import {module}' in content or f'from {module}' in content
                
                if module_used and not module_imported:
                    print(f"❌ {file_path} - 使用了{module}但未导入")
                    issues_found += 1
        
        except Exception as e:
            print(f"❌ 检查文件失败 {file_path}: {e}")
    
    return issues_found

def main():
    print("🚀 开始错误检查和修复...")
    print("="*60)
    
    total_fixes = 0
    total_issues = 0
    
    # 修复Plotly错误
    fixes = check_and_fix_plotly_errors()
    total_fixes += fixes
    
    # 检查其他错误
    total_issues += check_pandas_errors()
    total_issues += check_streamlit_errors()
    total_issues += check_data_loading_errors()
    total_issues += check_import_errors()
    
    print("\n" + "="*60)
    print("📋 检查结果总结")
    print("="*60)
    print(f"🔧 已修复错误: {total_fixes}")
    print(f"⚠️ 发现问题: {total_issues}")
    
    if total_fixes > 0:
        print(f"\n✅ 已自动修复 {total_fixes} 个错误")
        print("💡 建议重启Streamlit应用以应用修复")
    
    if total_issues == 0:
        print("\n🎉 没有发现其他问题，系统状态良好！")
    else:
        print(f"\n💡 发现 {total_issues} 个潜在问题，建议检查")
    
    print("\n🚀 检查完成！")

if __name__ == "__main__":
    main()
