#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中金所增强版爬虫演示程序
展示自动点击日期和合约选择功能，以及CSV导出功能
"""

from cffex_spider import CFFEXSpider
import time

def demo_auto_click():
    """演示自动点击功能"""
    print("增强版中金所爬虫演示")
    print("=" * 50)
    print("功能特点:")
    print("1. 自动选择查询日期")
    print("2. 自动选择合约月份")
    print("3. 自动点击查询按钮")
    print("4. 智能处理动态加载内容")
    print()
    
    # 创建爬虫实例
    spider = CFFEXSpider(headless=False)  # 非无头模式便于观察
    
    try:
        # 演示1: 指定日期和合约的查询
        print("演示1: 指定日期和合约查询")
        print("-" * 30)
        
        # 计算前一个工作日
        today = datetime.now()
        days_back = 1
        while days_back <= 7:  # 最多往前找7天
            target_date = today - timedelta(days=days_back)
            if target_date.weekday() < 5:  # 周一到周五
                break
            days_back += 1
        
        date_str = target_date.strftime("%Y-%m-%d")
        contract_month = target_date.strftime("%Y-%m")  # 当月合约
        
        print(f"查询日期: {date_str}")
        print(f"合约月份: {contract_month}")
        print("开始查询...")
        
        result1 = spider.get_product_data(
            product_id="IM", 
            date=date_str, 
            contract_month=contract_month
        )
        
        if result1:
            print("查询结果:")
            if result1.get('success'):
                print("✓ 成功获取数据")
                print(f"  数据表格数量: {len(result1.get('data', []))}")
            else:
                print(f"✗ 查询失败: {result1.get('error')}")
        
        print()
        
        # 演示2: 只指定日期，使用默认合约
        print("演示2: 只指定日期查询")
        print("-" * 30)
        
        print(f"查询日期: {date_str}")
        print("合约: 使用默认主力合约")
        print("开始查询...")
        
        result2 = spider.get_product_data(
            product_id="IF",  # 换个产品
            date=date_str
        )
        
        if result2:
            print("查询结果:")
            if result2.get('success'):
                print("✓ 成功获取数据")
                print(f"  数据表格数量: {len(result2.get('data', []))}")
            else:
                print(f"✗ 查询失败: {result2.get('error')}")
        
        print()
        
        # 演示3: 使用最新数据
        print("演示3: 获取最新数据")
        print("-" * 30)
        
        print("使用默认设置获取最新数据...")
        
        result3 = spider.get_product_data(product_id="IC")
        
        if result3:
            print("查询结果:")
            if result3.get('success'):
                print("✓ 成功获取数据")
                print(f"  数据表格数量: {len(result3.get('data', []))}")
                
                # 保存数据
                filename = spider.save_to_excel(result3, "demo_latest_data.xlsx")
                if filename:
                    print(f"✓ 数据已保存到: {filename}")
            else:
                print(f"✗ 查询失败: {result3.get('error')}")
        
        print()
        print("演示完成!")
        
    except Exception as e:
        print(f"演示过程中发生错误: {e}")
    finally:
        spider.close()

def demo_batch_query():
    """演示批量查询不同合约"""
    print("\n批量查询演示")
    print("=" * 30)
    
    spider = CFFEXSpider(headless=True)  # 批量查询使用无头模式
    
    try:
        # 定义要查询的合约列表
        contracts = [
            {"product": "IM", "month": "2024-12"},
            {"product": "IM", "month": "2025-01"},
            {"product": "IM", "month": "2025-03"},
        ]
        
        results = {}
        
        for contract in contracts:
            print(f"正在查询 {contract['product']} {contract['month']}...")
            
            result = spider.get_product_data(
                product_id=contract['product'],
                contract_month=contract['month']
            )
            
            results[f"{contract['product']}_{contract['month']}"] = result
            
            if result and result.get('success'):
                print(f"✓ {contract['product']} {contract['month']} 查询成功")
            else:
                print(f"✗ {contract['product']} {contract['month']} 查询失败")
        
        print(f"\n批量查询完成，共查询 {len(contracts)} 个合约")
        
        # 统计成功率
        success_count = sum(1 for r in results.values() if r and r.get('success'))
        print(f"成功率: {success_count}/{len(contracts)} ({success_count/len(contracts)*100:.1f}%)")
        
    except Exception as e:
        print(f"批量查询过程中发生错误: {e}")
    finally:
        spider.close()

def interactive_demo():
    """交互式演示"""
    print("\n交互式演示")
    print("=" * 30)
    
    spider = CFFEXSpider(headless=False)
    
    try:
        # 获取用户输入
        print("请输入查询参数:")
        
        product_id = input("产品代码 (IM/IF/IC/IH, 默认IM): ").strip().upper()
        if not product_id:
            product_id = "IM"
        
        date_input = input("查询日期 (YYYY-MM-DD, 回车使用最新): ").strip()
        date = date_input if date_input else None
        
        contract_input = input("合约月份 (YYYY-MM, 回车使用默认): ").strip()
        contract_month = contract_input if contract_input else None
        
        print(f"\n开始查询 {product_id} 的数据...")
        if date:
            print(f"日期: {date}")
        if contract_month:
            print(f"合约: {contract_month}")
        
        result = spider.get_product_data(
            product_id=product_id,
            date=date,
            contract_month=contract_month
        )
        
        if result:
            print("\n查询结果:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
            if result.get('success'):
                save_choice = input("\n是否保存到Excel文件? (y/n): ").lower().strip()
                if save_choice in ['y', 'yes', '是']:
                    filename = spider.save_to_excel(result)
                    if filename:
                        print(f"数据已保存到: {filename}")
        else:
            print("未获取到任何数据")
    
    except KeyboardInterrupt:
        print("\n用户中断演示")
    except Exception as e:
        print(f"交互式演示过程中发生错误: {e}")
    finally:
        spider.close()

if __name__ == "__main__":
    print("中金所增强版爬虫演示程序")
    print("=" * 50)
    
    try:
        choice = input("选择演示模式:\n1. 自动点击演示\n2. 批量查询演示\n3. 交互式演示\n请输入选择 (1-3): ").strip()
        
        if choice == "1":
            demo_auto_click()
        elif choice == "2":
            demo_batch_query()
        elif choice == "3":
            interactive_demo()
        else:
            print("无效选择，运行默认演示...")
            demo_auto_click()
            
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序执行出错: {e}")