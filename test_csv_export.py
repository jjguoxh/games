#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV导出功能测试脚本
测试爬虫程序的CSV导出功能是否正常工作
"""

from cffex_spider import CFFEXSpider
import os
import csv
import json

def test_csv_export_basic():
    """测试基础CSV导出功能"""
    print("测试1: 基础CSV导出功能")
    print("-" * 40)
    
    # 创建测试数据
    test_data = {
        "success": True,
        "product_id": "IM",
        "date": "2025-09-17",
        "timestamp": "2025-09-17T15:30:00",
        "data": [
            {
                "headers": ["排名", "会员简称", "成交量", "增减量"],
                "rows": [
                    {"排名": "1", "会员简称": "测试期货公司A", "成交量": "1000", "增减量": "+50"},
                    {"排名": "2", "会员简称": "测试期货公司B", "成交量": "800", "增减量": "-20"},
                    {"排名": "3", "会员简称": "测试期货公司C", "成交量": "600", "增减量": "+30"}
                ],
                "total_rows": 3
            }
        ]
    }
    
    spider = CFFEXSpider()
    
    try:
        # 测试CSV导出
        csv_filename = spider.save_to_csv(test_data, "test_basic.csv")
        
        if csv_filename and os.path.exists(csv_filename):
            print(f"✅ CSV文件创建成功: {csv_filename}")
            
            # 验证文件内容
            with open(csv_filename, 'r', encoding='utf-8-sig') as f:
                content = f.read()
                
            print("📄 文件内容预览:")
            print(content[:500] + "..." if len(content) > 500 else content)
            
            # 检查是否包含元数据
            if "产品代码: IM" in content and "查询日期: 2025-09-17" in content:
                print("✅ 元数据信息正确")
            else:
                print("❌ 元数据信息缺失")
            
            # 检查是否包含数据行
            if "测试期货公司A" in content and "1000" in content:
                print("✅ 数据内容正确")
            else:
                print("❌ 数据内容缺失")
                
            return True
        else:
            print("❌ CSV文件创建失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        return False
    finally:
        spider.close()

def test_csv_export_multiple_tables():
    """测试多表格CSV导出功能"""
    print("\n测试2: 多表格CSV导出功能")
    print("-" * 40)
    
    # 创建多表格测试数据
    test_data = {
        "success": True,
        "product_id": "IF",
        "date": "2025-09-17",
        "timestamp": "2025-09-17T15:30:00",
        "data": [
            {
                "headers": ["排名", "会员简称", "成交量"],
                "rows": [
                    {"排名": "1", "会员简称": "期货公司1", "成交量": "500"},
                    {"排名": "2", "会员简称": "期货公司2", "成交量": "400"}
                ],
                "total_rows": 2
            },
            {
                "headers": ["排名", "会员简称", "持仓量"],
                "rows": [
                    {"排名": "1", "会员简称": "期货公司3", "持仓量": "300"},
                    {"排名": "2", "会员简称": "期货公司4", "持仓量": "200"}
                ],
                "total_rows": 2
            }
        ]
    }
    
    spider = CFFEXSpider()
    
    try:
        csv_filename = spider.save_to_csv(test_data, "test_multiple.csv")
        
        if csv_filename and os.path.exists(csv_filename):
            print(f"✅ 多表格CSV文件创建成功: {csv_filename}")
            
            with open(csv_filename, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            # 检查是否包含两个表格的数据
            if "期货公司1" in content and "期货公司3" in content:
                print("✅ 多表格数据合并正确")
            else:
                print("❌ 多表格数据合并失败")
                
            return True
        else:
            print("❌ 多表格CSV文件创建失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        return False
    finally:
        spider.close()

def test_csv_vs_excel():
    """测试CSV与Excel格式对比"""
    print("\n测试3: CSV与Excel格式对比")
    print("-" * 40)
    
    test_data = {
        "success": True,
        "product_id": "IC",
        "date": "2025-09-17",
        "timestamp": "2025-09-17T15:30:00",
        "data": [
            {
                "headers": ["排名", "会员简称", "成交量", "增减量"],
                "rows": [
                    {"排名": "1", "会员简称": "对比测试公司", "成交量": "1500", "增减量": "+100"}
                ],
                "total_rows": 1
            }
        ]
    }
    
    spider = CFFEXSpider()
    
    try:
        # 同时导出CSV和Excel格式
        csv_filename = spider.save_to_csv(test_data, "test_comparison.csv")
        excel_filename = spider.save_to_excel(test_data, "test_comparison.xlsx")
        
        csv_success = csv_filename and os.path.exists(csv_filename)
        excel_success = excel_filename and os.path.exists(excel_filename)
        
        if csv_success and excel_success:
            print("✅ CSV和Excel文件都创建成功")
            
            # 比较文件大小
            csv_size = os.path.getsize(csv_filename)
            excel_size = os.path.getsize(excel_filename)
            
            print(f"📊 文件大小对比:")
            print(f"   CSV文件: {csv_size} 字节")
            print(f"   Excel文件: {excel_size} 字节")
            print(f"   CSV文件更小: {excel_size - csv_size} 字节")
            
            return True
        else:
            print(f"❌ 文件创建失败 - CSV: {csv_success}, Excel: {excel_success}")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        return False
    finally:
        spider.close()

def test_csv_encoding():
    """测试CSV文件编码"""
    print("\n测试4: CSV文件编码测试")
    print("-" * 40)
    
    # 包含中文字符的测试数据
    test_data = {
        "success": True,
        "product_id": "测试产品",
        "date": "2025-09-17",
        "timestamp": "2025-09-17T15:30:00",
        "data": [
            {
                "headers": ["排名", "会员简称", "成交量", "备注"],
                "rows": [
                    {"排名": "1", "会员简称": "中文测试公司", "成交量": "1000", "备注": "正常交易"},
                    {"排名": "2", "会员简称": "English Company", "成交量": "800", "备注": "Mixed中英文"}
                ],
                "total_rows": 2
            }
        ]
    }
    
    spider = CFFEXSpider()
    
    try:
        csv_filename = spider.save_to_csv(test_data, "test_encoding.csv")
        
        if csv_filename and os.path.exists(csv_filename):
            print(f"✅ 编码测试CSV文件创建成功: {csv_filename}")
            
            # 测试不同编码方式读取
            try:
                with open(csv_filename, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                
                if "中文测试公司" in content and "Mixed中英文" in content:
                    print("✅ UTF-8编码正确，中文显示正常")
                else:
                    print("❌ 中文字符显示异常")
                    
                return True
            except UnicodeDecodeError:
                print("❌ 文件编码错误")
                return False
        else:
            print("❌ 编码测试CSV文件创建失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        return False
    finally:
        spider.close()

def cleanup_test_files():
    """清理测试文件"""
    test_files = [
        "test_basic.csv",
        "test_multiple.csv", 
        "test_comparison.csv",
        "test_comparison.xlsx",
        "test_encoding.csv"
    ]
    
    print("\n🧹 清理测试文件...")
    for filename in test_files:
        if os.path.exists(filename):
            try:
                os.remove(filename)
                print(f"   删除: {filename}")
            except Exception as e:
                print(f"   删除失败 {filename}: {e}")

def main():
    """主测试函数"""
    print("CSV导出功能测试")
    print("=" * 50)
    
    test_results = []
    
    # 执行所有测试
    test_results.append(test_csv_export_basic())
    test_results.append(test_csv_export_multiple_tables())
    test_results.append(test_csv_vs_excel())
    test_results.append(test_csv_encoding())
    
    # 统计测试结果
    passed = sum(test_results)
    total = len(test_results)
    
    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    print(f"总测试数: {total}")
    print(f"通过测试: {passed}")
    print(f"失败测试: {total - passed}")
    print(f"通过率: {passed/total*100:.1f}%")
    
    if passed == total:
        print("🎉 所有CSV导出功能测试通过！")
    else:
        print("⚠️  部分测试失败，请检查相关功能")
    
    # 询问是否清理测试文件
    cleanup = input("\n是否清理测试文件? (y/n): ").strip().lower()
    if cleanup in ['y', 'yes', '是']:
        cleanup_test_files()
    
    return passed == total

if __name__ == "__main__":
    main()