#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬虫调试脚本
用于诊断CFFEX网站数据获取问题
"""

from cffex_spider import CFFEXSpider
import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import logging

def debug_page_structure(spider, product_id="IM"):
    """调试页面结构"""
    print(f"调试产品 {product_id} 的页面结构")
    print("=" * 50)
    
    try:
        # 访问页面
        url = f"http://www.cffex.com.cn/ccpm/?productid={product_id}"
        print(f"访问URL: {url}")
        spider.driver.get(url)
        time.sleep(5)
        
        # 获取页面标题
        title = spider.driver.title
        print(f"页面标题: {title}")
        
        # 检查页面是否正确加载
        current_url = spider.driver.current_url
        print(f"当前URL: {current_url}")
        
        # 查找所有表格
        tables = spider.driver.find_elements(By.TAG_NAME, "table")
        print(f"找到 {len(tables)} 个表格元素")
        
        for i, table in enumerate(tables):
            print(f"\n表格 {i+1}:")
            try:
                rows = table.find_elements(By.TAG_NAME, "tr")
                print(f"  行数: {len(rows)}")
                if rows:
                    first_row = rows[0]
                    cells = first_row.find_elements(By.TAG_NAME, "th") or first_row.find_elements(By.TAG_NAME, "td")
                    print(f"  列数: {len(cells)}")
                    if cells:
                        headers = [cell.text.strip() for cell in cells]
                        print(f"  表头: {headers}")
            except Exception as e:
                print(f"  解析表格时出错: {e}")
        
        # 查找可能的数据容器
        print(f"\n查找数据容器:")
        container_selectors = [
            ".data-table",
            ".table-container", 
            ".content-table",
            "[class*='table']",
            "[class*='data']"
        ]
        
        for selector in container_selectors:
            try:
                elements = spider.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"  找到 {len(elements)} 个 '{selector}' 元素")
            except Exception as e:
                print(f"  查找 '{selector}' 时出错: {e}")
        
        # 检查是否有"没有数据"的提示
        no_data_texts = [
            "没有您所查询的数据",
            "暂无数据",
            "无数据",
            "No data"
        ]
        
        print(f"\n检查无数据提示:")
        for text in no_data_texts:
            try:
                elements = spider.driver.find_elements(By.XPATH, f"//*[contains(text(), '{text}')]")
                if elements:
                    print(f"  发现提示: '{text}' ({len(elements)} 个元素)")
            except Exception as e:
                print(f"  检查 '{text}' 时出错: {e}")
        
        # 查找所有可能的交互元素
        print(f"\n查找交互元素:")
        interactive_selectors = [
            "input[type='date']",
            "select",
            "button",
            "[onclick]",
            ".btn",
            ".button"
        ]
        
        for selector in interactive_selectors:
            try:
                elements = spider.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"  找到 {len(elements)} 个 '{selector}' 元素")
                    for i, elem in enumerate(elements[:3]):  # 只显示前3个
                        try:
                            text = elem.text.strip() or elem.get_attribute('value') or elem.get_attribute('placeholder')
                            print(f"    元素{i+1}: {text}")
                        except:
                            pass
            except Exception as e:
                print(f"  查找 '{selector}' 时出错: {e}")
        
        # 保存页面源码
        page_source = spider.driver.page_source
        debug_filename = f"debug_page_{product_id}.html"
        with open(debug_filename, 'w', encoding='utf-8') as f:
            f.write(page_source)
        print(f"\n页面源码已保存到: {debug_filename}")
        
        return True
        
    except Exception as e:
        print(f"调试过程中发生错误: {e}")
        return False

def test_different_products():
    """测试不同产品的数据获取"""
    print("测试不同产品的数据获取")
    print("=" * 50)
    
    products = ["IM", "IF", "IC", "IH", "T", "TF", "TS"]
    spider = CFFEXSpider(headless=False)  # 使用可视化模式便于调试
    
    try:
        for product in products:
            print(f"\n测试产品: {product}")
            print("-" * 30)
            
            result = spider.get_product_data(product_id=product)
            
            if result:
                if result.get("success"):
                    print(f"✅ {product}: 成功获取 {len(result.get('data', []))} 个数据表")
                elif result.get("error"):
                    print(f"❌ {product}: {result['error']}")
                else:
                    print(f"⚠️  {product}: 未知状态")
            else:
                print(f"❌ {product}: 返回None")
            
            time.sleep(2)  # 避免请求过快
            
    finally:
        spider.close()

def test_manual_interaction():
    """测试手动交互流程"""
    print("测试手动交互流程")
    print("=" * 50)
    
    spider = CFFEXSpider(headless=False)
    
    try:
        # 访问页面
        url = "http://www.cffex.com.cn/ccpm/?productid=IM"
        print(f"访问: {url}")
        spider.driver.get(url)
        
        print("页面已加载，请手动操作...")
        print("1. 选择日期")
        print("2. 选择合约")
        print("3. 点击查询")
        print("4. 观察结果")
        
        input("完成手动操作后按回车继续...")
        
        # 检查结果
        tables = spider.driver.find_elements(By.TAG_NAME, "table")
        print(f"操作后找到 {len(tables)} 个表格")
        
        for i, table in enumerate(tables):
            try:
                rows = table.find_elements(By.TAG_NAME, "tr")
                if len(rows) > 1:  # 有数据行
                    print(f"表格 {i+1}: {len(rows)} 行数据")
                    # 显示前几行数据
                    for j, row in enumerate(rows[:3]):
                        cells = row.find_elements(By.TAG_NAME, "td") or row.find_elements(By.TAG_NAME, "th")
                        cell_texts = [cell.text.strip() for cell in cells]
                        print(f"  行{j+1}: {cell_texts}")
            except Exception as e:
                print(f"解析表格 {i+1} 时出错: {e}")
        
    finally:
        spider.close()

def main():
    """主调试函数"""
    print("CFFEX爬虫调试工具")
    print("=" * 50)
    
    while True:
        print("\n请选择调试选项:")
        print("1. 调试页面结构 (IM产品)")
        print("2. 调试页面结构 (IF产品)")
        print("3. 测试所有产品")
        print("4. 手动交互测试")
        print("5. 退出")
        
        choice = input("请输入选项 (1-5): ").strip()
        
        if choice == "1":
            spider = CFFEXSpider(headless=False)
            try:
                debug_page_structure(spider, "IM")
            finally:
                spider.close()
                
        elif choice == "2":
            spider = CFFEXSpider(headless=False)
            try:
                debug_page_structure(spider, "IF")
            finally:
                spider.close()
                
        elif choice == "3":
            test_different_products()
            
        elif choice == "4":
            test_manual_interaction()
            
        elif choice == "5":
            print("退出调试工具")
            break
            
        else:
            print("无效选项，请重新选择")

if __name__ == "__main__":
    main()