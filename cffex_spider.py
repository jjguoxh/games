#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中金所持仓数据爬虫程序
目标网站: http://www.cffex.com.cn/ccpm/?productid=IM
功能: 爬取期货持仓排名数据
"""

import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cffex_spider.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class CFFEXSpider:
    def __init__(self, headless=True):
        """
        初始化爬虫
        Args:
            headless: 是否使用无头模式
        """
        self.base_url = "http://www.cffex.com.cn/ccpm/"
        self.session = requests.Session()
        self.setup_headers()
        self.setup_driver(headless)
        
    def setup_headers(self):
        """设置请求头"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def setup_driver(self, headless=True):
        """设置Selenium WebDriver"""
        try:
            chrome_options = Options()
            if headless:
                chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 10)
            logging.info("WebDriver初始化成功")
        except Exception as e:
            logging.error(f"WebDriver初始化失败: {e}")
            self.driver = None
    
    def get_product_data(self, product_id="IM", date=None, contract_month=None):
        """
        获取指定产品的持仓数据
        Args:
            product_id: 产品ID (IM=中证1000股指期货)
            date: 查询日期，格式YYYY-MM-DD，默认为最新交易日
            contract_month: 合约月份，如"2024-12"，默认为主力合约
        Returns:
            dict: 包含持仓数据的字典
        """
        try:
            # 构造页面URL
            page_url = f"http://www.cffex.com.cn/ccpm/?productid={product_id}"
            logging.info(f"正在访问页面: {page_url}")
            
            # 访问页面
            self.driver.get(page_url)
            
            # 等待页面加载
            time.sleep(3)
            
            # 设置日期
            if date:
                try:
                    date_input = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.ID, "inputdate"))
                    )
                    # 清空并输入日期
                    date_input.clear()
                    date_input.send_keys(date)
                    logging.info(f"已设置日期: {date}")
                except Exception as e:
                    logging.warning(f"设置日期失败: {e}")
            
            # 点击查询按钮
            try:
                query_button = self.driver.find_element(By.XPATH, "//button[contains(text(), '查询')]")
                query_button.click()
                logging.info("已点击查询按钮")
                
                # 等待数据加载
                time.sleep(5)
            except Exception as e:
                logging.warning(f"点击查询按钮失败: {e}")
            
            # 检查是否有"无数据"提示
            try:
                no_data_element = self.driver.find_element(By.CLASS_NAME, "no_data")
                if no_data_element.is_displayed() and no_data_element.text.strip():
                    logging.info("页面显示无数据")
                    return {
                        "success": False,
                        "error": f"该日期({date or 'latest'})无数据",
                        "product_id": product_id,
                        "date": date or 'latest'
                    }
            except:
                pass  # 没有找到无数据提示，继续处理
            
            # 等待数据表格加载
            try:
                # 先等待页面完全加载
                time.sleep(3)
                
                # 尝试多种可能的表格选择器
                table_selectors = [
                    "//table[contains(@class, 'table')]",
                    "//table",
                    "//div[contains(@class, 'table')]//table",
                    "//div[@id='data']//table",
                    "//div[contains(@class, 'data')]//table"
                ]
                
                table_found = False
                for selector in table_selectors:
                    try:
                        WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, selector))
                        )
                        logging.info(f"数据表格已加载，使用选择器: {selector}")
                        table_found = True
                        break
                    except:
                        continue
                
                if not table_found:
                    # 如果找不到表格，打印页面源码用于调试
                    logging.warning("未找到数据表格，打印页面内容用于调试")
                    page_source = self.driver.page_source
                    logging.debug(f"页面源码: {page_source[:2000]}...")  # 只打印前2000字符
                    
            except Exception as e:
                logging.warning(f"等待数据表格超时: {e}")
            
            # 解析页面数据
            parsed_data = self.parse_page_data()
            
            if parsed_data and any(parsed_data.values()):
                logging.info(f"成功获取数据: {product_id}, 日期: {date or 'latest'}")
                return {
                    "success": True,
                    "data": parsed_data,
                    "product_id": product_id,
                    "date": date or 'latest',
                    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            else:
                logging.error("未能获取到有效数据")
                return {
                    "success": False,
                    "error": "未能获取到有效数据",
                    "product_id": product_id,
                    "date": date or 'latest'
                }
                
        except Exception as e:
            logging.error(f"获取数据时发生错误: {e}")
            return {
                "success": False,
                "error": f"获取数据时发生错误: {e}",
                "product_id": product_id,
                "date": date or 'latest'
            }
    
    def parse_page_data(self):
        """
        解析页面中的成交持仓排名数据
        Returns:
            dict: 解析后的数据
        """
        try:
            result = {
                "volume_ranking": [],      # 成交量排名
                "buy_position_ranking": [], # 持买单量排名  
                "sell_position_ranking": [] # 持卖单量排名
            }
            
            # 尝试多种可能的表格选择器
            table_selectors = [
                "//table[contains(@class, 'table')]",
                "//table",
                "//div[contains(@class, 'table')]//table",
                "//div[@id='data']//table",
                "//div[contains(@class, 'data')]//table"
            ]
            
            tables = []
            for selector in table_selectors:
                try:
                    found_tables = self.driver.find_elements(By.XPATH, selector)
                    if found_tables:
                        tables = found_tables
                        logging.info(f"找到 {len(tables)} 个表格，使用选择器: {selector}")
                        break
                except:
                    continue
            
            if not tables:
                logging.warning("未找到任何数据表格")
                # 尝试查找其他可能的数据容器
                try:
                    # 查找可能包含数据的div元素
                    data_divs = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'data') or contains(@id, 'data')]")
                    if data_divs:
                        logging.info(f"找到 {len(data_divs)} 个数据容器")
                        for div in data_divs:
                            logging.debug(f"数据容器内容: {div.text[:200]}...")
                except:
                    pass
                return result
            
            for i, table in enumerate(tables):
                try:
                    # 获取表格标题或类型
                    table_type = None
                    
                    # 尝试从表格前的标题获取类型
                    try:
                        # 查找表格前面的标题元素
                        title_elements = self.driver.find_elements(By.XPATH, f"//table[{i+1}]/preceding-sibling::*")
                        for title_element in title_elements[-3:]:  # 检查前3个兄弟元素
                            title_text = title_element.text.strip()
                            if title_text:
                                logging.info(f"表格 {i} 标题: {title_text}")
                                if "成交量" in title_text:
                                    table_type = "volume_ranking"
                                elif "持买" in title_text or "买单" in title_text:
                                    table_type = "buy_position_ranking"
                                elif "持卖" in title_text or "卖单" in title_text:
                                    table_type = "sell_position_ranking"
                                break
                    except Exception as e:
                        logging.debug(f"获取表格标题失败: {e}")
                    
                    # 如果无法从标题判断，根据表格顺序判断
                    if not table_type:
                        if i == 0:
                            table_type = "volume_ranking"
                        elif i == 1:
                            table_type = "buy_position_ranking"
                        elif i == 2:
                            table_type = "sell_position_ranking"
                        else:
                            continue
                    
                    logging.info(f"解析表格 {i}，类型: {table_type}")
                    
                    # 解析表格数据
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    logging.info(f"表格 {i} 共有 {len(rows)} 行")
                    
                    if len(rows) <= 1:  # 只有表头或没有数据
                        logging.warning(f"表格 {i} 没有数据行")
                        continue
                    
                    for row_idx, row in enumerate(rows[1:], 1):  # 跳过表头
                        cells = row.find_elements(By.TAG_NAME, "td")
                        if len(cells) >= 4:
                            record = {
                                "rank": cells[0].text.strip(),
                                "member_name": cells[1].text.strip(),
                                "volume": cells[2].text.strip(),
                                "change": cells[3].text.strip()
                            }
                            result[table_type].append(record)
                            logging.debug(f"表格 {i} 第 {row_idx} 行: {record}")
                        else:
                            logging.debug(f"表格 {i} 第 {row_idx} 行列数不足: {len(cells)}")
                    
                    logging.info(f"解析表格 {table_type}: {len(result[table_type])} 条记录")
                    
                except Exception as e:
                    logging.warning(f"解析表格 {i} 时发生错误: {e}")
                    continue
            
            # 统计总记录数
            total_records = sum(len(records) for records in result.values())
            logging.info(f"总共解析到 {total_records} 条记录")
            
            return result
            
        except Exception as e:
            logging.error(f"解析页面数据时发生错误: {e}")
            return None
        """
        自动点击选择日期和合约
        Args:
            target_date: 目标日期，格式YYYY-MM-DD
            contract_month: 合约月份，如"2024-12"
        Returns:
            bool: 操作是否成功
        """
        try:
            success_count = 0
            
            # 1. 处理日期选择
            if target_date:
                date_success = self.click_date_selector(target_date)
                if date_success:
                    success_count += 1
                    logging.info(f"成功选择日期: {target_date}")
                else:
                    logging.warning(f"选择日期失败: {target_date}")
            
            # 2. 处理合约选择
            if contract_month:
                contract_success = self.click_contract_selector(contract_month)
                if contract_success:
                    success_count += 1
                    logging.info(f"成功选择合约: {contract_month}")
                else:
                    logging.warning(f"选择合约失败: {contract_month}")
            
            # 3. 点击查询按钮
            query_success = self.click_query_button()
            if query_success:
                success_count += 1
                logging.info("成功点击查询按钮")
            else:
                logging.warning("点击查询按钮失败")
            
            return success_count > 0
            
        except Exception as e:
            logging.error(f"自动点击操作发生错误: {e}")
            return False
    
    def click_date_selector(self, target_date):
        """点击日期选择器"""
        try:
            # 专门针对CFFEX网站的My97DatePicker日期选择器
            try:
                # 首先尝试找到actualDate输入框
                date_element = self.wait.until(EC.element_to_be_clickable((By.ID, "actualDate")))
                
                # 清空并输入日期
                date_element.clear()
                time.sleep(0.5)
                
                # 转换日期格式为YYYY-MM-DD
                formatted_date = target_date
                date_element.send_keys(formatted_date)
                
                # 触发多种事件确保日期被正确设置
                self.driver.execute_script("""
                    var element = arguments[0];
                    var date = arguments[1];
                    element.value = date;
                    element.dispatchEvent(new Event('input', {bubbles: true}));
                    element.dispatchEvent(new Event('change', {bubbles: true}));
                    element.dispatchEvent(new Event('blur', {bubbles: true}));
                """, date_element, formatted_date)
                
                time.sleep(1)
                logging.info(f"成功设置日期为: {formatted_date}")
                return True
                
            except (TimeoutException, NoSuchElementException):
                logging.warning("未找到actualDate输入框，尝试其他日期选择器")
            
            # 备用的日期选择器定位方式
            date_selectors = [
                "//input[@name='actualDate']",
                "//input[contains(@class, 'Wdate')]",
                "//input[@type='text' and contains(@onfocus, 'WdatePicker')]",
                "//input[@type='date']",
                "//input[contains(@class, 'date')]",
                "//input[contains(@id, 'date')]",
                "//input[contains(@name, 'date')]"
            ]
            
            for selector in date_selectors:
                try:
                    date_element = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    
                    # 清空并输入日期
                    date_element.clear()
                    time.sleep(0.5)
                    date_element.send_keys(target_date)
                    
                    # 触发事件
                    self.driver.execute_script("""
                        var element = arguments[0];
                        var date = arguments[1];
                        element.value = date;
                        element.dispatchEvent(new Event('input', {bubbles: true}));
                        element.dispatchEvent(new Event('change', {bubbles: true}));
                        element.dispatchEvent(new Event('blur', {bubbles: true}));
                    """, date_element, target_date)
                    
                    time.sleep(1)
                    logging.info(f"通过选择器 {selector} 成功设置日期为: {target_date}")
                    return True
                    
                except (TimeoutException, NoSuchElementException):
                    continue
            
            logging.warning("所有日期选择器尝试都失败了")
            return False
            
        except Exception as e:
            logging.error(f"点击日期选择器时发生错误: {e}")
            return False
    
    def click_contract_selector(self, contract_month):
        """点击合约选择器"""
        try:
            # 常见的合约选择器元素定位方式
            contract_selectors = [
                "//select[contains(@name, 'contract')]",
                "//select[contains(@id, 'contract')]",
                "//select[contains(@class, 'contract')]",
                "//div[contains(@class, 'contract-select')]//select",
                "//div[contains(@class, 'dropdown')]//select"
            ]
            
            for selector in contract_selectors:
                try:
                    select_element = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    
                    # 使用Selenium的Select类
                    from selenium.webdriver.support.ui import Select
                    select = Select(select_element)
                    
                    # 尝试按值选择
                    try:
                        select.select_by_value(contract_month)
                        return True
                    except:
                        pass
                    
                    # 尝试按可见文本选择
                    try:
                        select.select_by_visible_text(contract_month)
                        return True
                    except:
                        pass
                    
                    # 尝试部分匹配
                    for option in select.options:
                        if contract_month in option.text or contract_month in option.get_attribute('value'):
                            option.click()
                            return True
                    
                except (TimeoutException, NoSuchElementException):
                    continue
            
            # 尝试点击合约链接或按钮
            contract_links = [
                f"//a[contains(text(), '{contract_month}')]",
                f"//button[contains(text(), '{contract_month}')]",
                f"//span[contains(text(), '{contract_month}')]",
                f"//li[contains(text(), '{contract_month}')]",
                f"//option[contains(text(), '{contract_month}')]"
            ]
            
            for link_selector in contract_links:
                try:
                    contract_link = self.wait.until(EC.element_to_be_clickable((By.XPATH, link_selector)))
                    contract_link.click()
                    time.sleep(1)
                    return True
                except (TimeoutException, NoSuchElementException):
                    continue
            
            return False
            
        except Exception as e:
            logging.error(f"点击合约选择器时发生错误: {e}")
            return False
    
    def click_query_button(self):
        """点击查询按钮"""
        try:
            # 专门针对CFFEX网站的查询按钮
            try:
                # 首先尝试找到具有data-bind="click:getDatas"的按钮
                query_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-query[data-bind*='getDatas']")))
                query_button.click()
                time.sleep(3)  # 等待查询结果加载
                logging.info("成功点击查询按钮")
                return True
                
            except (TimeoutException, NoSuchElementException):
                logging.warning("未找到主查询按钮，尝试其他查询按钮")
            
            # 备用的查询按钮定位方式
            query_selectors = [
                "//button[contains(@class, 'btn-query')]",
                "//button[contains(text(), '查询')]",
                "//input[@type='submit' and contains(@value, '查询')]",
                "//input[@type='button' and contains(@value, '查询')]",
                "//button[contains(@data-bind, 'getDatas')]",
                "//a[contains(text(), '查询')]",
                "//span[contains(text(), '查询')]"
            ]
            
            for selector in query_selectors:
                try:
                    query_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    
                    # 使用JavaScript点击，避免元素被遮挡的问题
                    self.driver.execute_script("arguments[0].click();", query_button)
                    time.sleep(3)  # 等待查询结果加载
                    
                    logging.info(f"通过选择器 {selector} 成功点击查询按钮")
                    return True
                    
                except (TimeoutException, NoSuchElementException):
                    continue
            
            # 如果没找到查询按钮，尝试按回车键触发查询
            try:
                from selenium.webdriver.common.keys import Keys
                body = self.driver.find_element(By.TAG_NAME, "body")
                body.send_keys(Keys.ENTER)
                time.sleep(3)
                logging.info("通过回车键触发查询")
                return True
            except:
                pass
            
            logging.warning("所有查询按钮尝试都失败了")
            return False
            
        except Exception as e:
            logging.error(f"点击查询按钮时发生错误: {e}")
            return False
    
    def parse_table(self, table_element):
        """解析HTML表格"""
        try:
            rows = table_element.find_elements(By.TAG_NAME, "tr")
            if len(rows) < 2:  # 至少需要表头和一行数据
                return None
            
            # 获取表头
            headers = []
            header_row = rows[0]
            header_cells = header_row.find_elements(By.TAG_NAME, "th")
            if not header_cells:
                header_cells = header_row.find_elements(By.TAG_NAME, "td")
            
            for cell in header_cells:
                headers.append(cell.text.strip())
            
            if not headers:
                return None
            
            # 获取数据行
            data_rows = []
            for row in rows[1:]:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) == len(headers):
                    row_data = {}
                    for i, cell in enumerate(cells):
                        row_data[headers[i]] = cell.text.strip()
                    data_rows.append(row_data)
            
            return {
                "headers": headers,
                "rows": data_rows,
                "total_rows": len(data_rows)
            }
            
        except Exception as e:
            logging.error(f"解析表格时发生错误: {e}")
            return None
    
    def parse_data_container(self, container_element):
        """解析数据容器"""
        try:
            # 这里可以根据实际的HTML结构来解析
            text_content = container_element.text
            if text_content and len(text_content.strip()) > 0:
                return {"content": text_content.strip()}
            return None
        except Exception as e:
            logging.error(f"解析数据容器时发生错误: {e}")
            return None
    
    def check_ajax_requests(self, product_id, date):
        """检查并尝试获取Ajax请求的数据"""
        try:
            # 执行JavaScript来获取可能的Ajax数据
            script = """
            var ajaxData = null;
            if (typeof window.ajaxResponse !== 'undefined') {
                ajaxData = window.ajaxResponse;
            }
            return ajaxData;
            """
            ajax_result = self.driver.execute_script(script)
            
            if ajax_result:
                return {"ajax_data": ajax_result}
            
            # 尝试直接请求可能的API端点
            api_endpoints = [
                f"/api/ccpm/data?productid={product_id}",
                f"/ccpm/api/data?productid={product_id}",
                f"/data/ccpm?productid={product_id}"
            ]
            
            for endpoint in api_endpoints:
                try:
                    api_url = f"http://www.cffex.com.cn{endpoint}"
                    if date:
                        api_url += f"&date={date}"
                    
                    response = self.session.get(api_url, timeout=10)
                    if response.status_code == 200:
                        try:
                            json_data = response.json()
                            return {"api_data": json_data, "endpoint": endpoint}
                        except:
                            if response.text and len(response.text.strip()) > 0:
                                return {"api_text": response.text, "endpoint": endpoint}
                except:
                    continue
            
            return None
            
        except Exception as e:
            logging.error(f"检查Ajax请求时发生错误: {e}")
            return None
    
    def get_available_products(self):
        """获取可用的产品列表"""
        products = {
            "IF": "沪深300股指期货",
            "IC": "中证500股指期货", 
            "IM": "中证1000股指期货",
            "IH": "上证50股指期货",
            "T": "10年期国债期货",
            "TF": "5年期国债期货",
            "TS": "2年期国债期货"
        }
        return products
    
    def save_to_excel(self, data, filename=None):
        """保存数据到Excel文件"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cffex_data_{timestamp}.xlsx"
        
        try:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                if isinstance(data, dict) and 'data' in data:
                    for i, table_data in enumerate(data['data']):
                        if 'rows' in table_data:
                            df = pd.DataFrame(table_data['rows'])
                            sheet_name = f"Table_{i+1}"
                            df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # 添加元数据sheet
                metadata = {
                    'Product ID': [data.get('product_id', '')],
                    'Date': [data.get('date', '')],
                    'Timestamp': [data.get('timestamp', '')],
                    'Success': [data.get('success', False)]
                }
                meta_df = pd.DataFrame(metadata)
                meta_df.to_excel(writer, sheet_name='Metadata', index=False)
            
            logging.info(f"数据已保存到: {filename}")
            return filename
            
        except Exception as e:
            logging.error(f"保存Excel文件时发生错误: {e}")
            return None
    
    def save_to_csv(self, data, filename=None):
        """
        将数据保存为CSV格式
        Args:
            data: 要保存的数据
            filename: 文件名，如果为None则自动生成
        Returns:
            str: 保存的文件路径
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"cffex_data_{timestamp}.csv"
            
            # 检查数据格式
            if not isinstance(data, dict) or "data" not in data:
                logging.error("数据格式不正确，无法保存")
                return None
            
            # 准备CSV数据
            csv_data = []
            
            # 添加元数据注释
            csv_data.append([f"# 产品代码: {data.get('product_id', 'N/A')}"])
            csv_data.append([f"# 查询日期: {data.get('date', 'N/A')}"])
            csv_data.append([f"# 生成时间: {data.get('timestamp', 'N/A')}"])
            csv_data.append([f"# 查询状态: {'成功' if data.get('success', False) else '失败'}"])
            csv_data.append([])  # 空行分隔
            
            # 检查是否有错误
            if "error" in data:
                csv_data.append([f"# 错误信息: {data['error']}"])
                csv_data.append([])
            else:
                # 添加成交量排名数据
                if data["data"]["volume_ranking"]:
                    csv_data.append(["成交量排名"])
                    csv_data.append(["名次", "会员简称", "成交量", "比上交易日增减"])
                    for record in data["data"]["volume_ranking"]:
                        csv_data.append([
                            record["rank"],
                            record["member_name"],
                            record["volume"],
                            record["change"]
                        ])
                    csv_data.append([])  # 空行分隔
                
                # 添加持买单量排名数据
                if data["data"]["buy_position_ranking"]:
                    csv_data.append(["持买单量排名"])
                    csv_data.append(["名次", "会员简称", "持买单量", "比上交易日增减"])
                    for record in data["data"]["buy_position_ranking"]:
                        csv_data.append([
                            record["rank"],
                            record["member_name"],
                            record["volume"],
                            record["change"]
                        ])
                    csv_data.append([])  # 空行分隔
                
                # 添加持卖单量排名数据
                if data["data"]["sell_position_ranking"]:
                    csv_data.append(["持卖单量排名"])
                    csv_data.append(["名次", "会员简称", "持卖单量", "比上交易日增减"])
                    for record in data["data"]["sell_position_ranking"]:
                        csv_data.append([
                            record["rank"],
                            record["member_name"],
                            record["volume"],
                            record["change"]
                        ])
            
            # 保存到CSV文件
            df = pd.DataFrame(csv_data)
            df.to_csv(filename, index=False, header=False, encoding='utf-8-sig')
            
            logging.info(f"数据已保存到CSV文件: {filename}")
            return filename
            
        except Exception as e:
            logging.error(f"保存CSV文件时发生错误: {e}")
            return None
    
    def run_daily_crawl(self, product_ids=None, save_excel=True):
        """执行日常爬取任务"""
        if not product_ids:
            product_ids = ["IM", "IF", "IC", "IH"]  # 默认爬取主要股指期货
        
        results = {}
        
        for product_id in product_ids:
            logging.info(f"开始爬取产品: {product_id}")
            try:
                data = self.get_product_data(product_id)
                results[product_id] = data
                
                if save_excel and data and data.get('success'):
                    filename = f"cffex_{product_id}_{datetime.now().strftime('%Y%m%d')}.xlsx"
                    self.save_to_excel(data, filename)
                
                # 避免请求过于频繁
                time.sleep(2)
                
            except Exception as e:
                logging.error(f"爬取产品{product_id}时发生错误: {e}")
                results[product_id] = {"error": str(e)}
        
        return results
    
    def close(self):
        """关闭爬虫，释放资源"""
        if self.driver:
            self.driver.quit()
        self.session.close()
        logging.info("爬虫已关闭")

def main():
    """主函数"""
    print("中金所持仓数据爬虫程序")
    print("=" * 50)
    
    # 创建爬虫实例
    spider = CFFEXSpider(headless=False)  # 设置为False以便调试
    
    try:
        # 显示可用产品
        products = spider.get_available_products()
        print("可用产品:")
        for code, name in products.items():
            print(f"  {code}: {name}")
        print()
        
        # 获取用户输入
        product_id = input("请输入产品代码 (默认IM): ").strip().upper()
        if not product_id:
            product_id = "IM"
        
        # 固定使用2025-09-13日期进行测试（因为当天数据还未生成）
        date = "2025-09-12"
        print(f"使用固定测试日期: {date}")
        
        print(f"\n开始爬取产品 {product_id} 的数据...")
        
        # 执行爬取
        result = spider.get_product_data(product_id, date)
        
        if result:
            print("\n爬取结果:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
            # 保存为CSV格式
            if result.get('success'):
                csv_filename = spider.save_to_csv(result)
                if csv_filename:
                    print(f"\n✅ CSV数据已保存到: {csv_filename}")
                    print(f"\n🎉 数据保存成功")
                else:
                    print("\n❌ 文件保存失败")
            else:
                print(f"\n爬取失败: {result.get('error', '未知错误')}")
        else:
            print("未获取到任何数据")
    
    except KeyboardInterrupt:
        print("\n用户中断程序")
    except Exception as e:
        print(f"程序执行出错: {e}")
    finally:
        spider.close()

if __name__ == "__main__":
    main()