#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中金所爬虫程序测试脚本
"""

import sys
import json
from cffex_spider import CFFEXSpider

def test_spider():
    """测试爬虫基本功能"""
    print("开始测试中金所爬虫程序...")
    print("=" * 50)
    
    # 创建爬虫实例 (使用非无头模式便于观察)
    spider = CFFEXSpider(headless=False)
    
    try:
        # 测试1: 检查可用产品
        print("测试1: 获取可用产品列表")
        products = spider.get_available_products()
        print(f"可用产品数量: {len(products)}")
        for code, name in products.items():
            print(f"  {code}: {name}")
        print()
        
        # 测试2: 尝试获取IM产品数据
        print("测试2: 获取IM产品数据")
        result = spider.get_product_data("IM")
        
        if result:
            print("获取结果:")
            if result.get('success'):
                print("✓ 成功获取数据")
                print(f"  产品ID: {result.get('product_id')}")
                print(f"  日期: {result.get('date')}")
                print(f"  数据表格数量: {len(result.get('data', []))}")
                
                # 尝试保存到Excel
                filename = spider.save_to_excel(result, "test_output.xlsx")
                if filename:
                    print(f"✓ 数据已保存到: {filename}")
                else:
                    print("✗ 保存Excel失败")
                    
            else:
                print("✗ 获取数据失败")
                print(f"  错误信息: {result.get('error', '未知错误')}")
                
                # 如果是"没有查询到数据"，这可能是正常的（非交易日或数据未更新）
                if "没有" in str(result.get('error', '')):
                    print("  注意: 这可能是因为当前非交易时间或数据未更新")
        else:
            print("✗ 未获取到任何结果")
        
        print()
        
        # 测试3: 测试错误处理
        print("测试3: 测试错误处理（使用无效产品ID）")
        invalid_result = spider.get_product_data("INVALID")
        if invalid_result and 'error' in invalid_result:
            print("✓ 错误处理正常")
            print(f"  错误信息: {invalid_result.get('error')}")
        else:
            print("✗ 错误处理异常")
        
        print()
        print("测试完成!")
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        return False
    finally:
        spider.close()
        print("爬虫已关闭")
    
    return True

def test_without_browser():
    """测试不依赖浏览器的功能"""
    print("\n测试基础功能（无浏览器）...")
    print("=" * 30)
    
    try:
        # 只测试不需要浏览器的功能
        spider = CFFEXSpider(headless=True)
        
        # 测试产品列表
        products = spider.get_available_products()
        print(f"✓ 产品列表获取成功，共{len(products)}个产品")
        
        # 测试会话设置
        print(f"✓ HTTP会话已建立")
        print(f"  User-Agent: {spider.session.headers.get('User-Agent', 'N/A')[:50]}...")
        
        spider.close()
        return True
        
    except Exception as e:
        print(f"✗ 基础功能测试失败: {e}")
        return False

if __name__ == "__main__":
    print("中金所爬虫程序测试")
    print("=" * 50)
    
    # 首先测试基础功能
    basic_test = test_without_browser()
    
    if basic_test:
        print("\n基础功能测试通过!")
        
        # 询问是否进行完整测试
        try:
            choice = input("\n是否进行完整测试（需要Chrome浏览器）？(y/n): ").lower().strip()
            if choice in ['y', 'yes', '是']:
                full_test = test_spider()
                if full_test:
                    print("\n所有测试完成!")
                else:
                    print("\n完整测试失败!")
                    sys.exit(1)
            else:
                print("跳过完整测试")
        except KeyboardInterrupt:
            print("\n用户中断测试")
    else:
        print("\n基础功能测试失败!")
        sys.exit(1)