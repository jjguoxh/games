# 中金所持仓数据爬虫程序

## 功能介绍

本程序用于爬取中国金融期货交易所(CFFEX)的持仓排名数据，支持多种期货产品的数据获取。

**🆕 新增功能：**
- ✅ **自动点击日期选择器** - 智能识别并选择指定日期
- ✅ **自动点击合约选择器** - 自动选择指定合约月份
- ✅ **自动点击查询按钮** - 自动触发数据查询
- ✅ **动态网页处理** - 完美处理JavaScript动态加载的内容

## 支持的产品

- **IF**: 沪深300股指期货
- **IC**: 中证500股指期货  
- **IM**: 中证1000股指期货
- **IH**: 上证50股指期货
- **T**: 10年期国债期货
- **TF**: 5年期国债期货
- **TS**: 2年期国债期货

## 安装依赖

```bash
pip install -r requirements_spider.txt
```

## 安装Chrome浏览器和ChromeDriver

1. 下载并安装Chrome浏览器
2. 下载对应版本的ChromeDriver: https://chromedriver.chromium.org/
3. 将ChromeDriver添加到系统PATH中

## 使用方法

### 1. 交互式运行

```bash
python cffex_spider.py
```

程序会提示输入产品代码和查询日期。

### 2. 增强功能演示

```bash
python enhanced_spider_demo.py
```

提供三种演示模式：
- 自动点击演示
- 批量查询演示  
- 交互式演示

### 3. 编程方式使用

#### 基础用法
```python
from cffex_spider import CFFEXSpider

# 创建爬虫实例
spider = CFFEXSpider(headless=True)

try:
    # 获取IM产品的最新数据
    result = spider.get_product_data("IM")
    
    if result and result.get('success'):
        print("获取数据成功!")
        # 保存到Excel
        spider.save_to_excel(result)
    else:
        print(f"获取数据失败: {result.get('error')}")
        
finally:
    spider.close()
```

#### 🆕 使用自动点击功能
```python
from cffex_spider import CFFEXSpider

spider = CFFEXSpider(headless=False)  # 可视化模式便于观察

try:
    # 指定日期和合约的查询
    result = spider.get_product_data(
        product_id="IM",
        date="2024-01-15",           # 自动选择日期
        contract_month="2024-12"     # 自动选择合约
    )
    
    if result and result.get('success'):
        print("自动点击查询成功!")
        spider.save_to_excel(result)
    
finally:
    spider.close()
```

### 4. 批量爬取

```python
from cffex_spider import CFFEXSpider

spider = CFFEXSpider()
try:
    # 爬取多个产品的数据
    results = spider.run_daily_crawl(["IM", "IF", "IC"])
    print("批量爬取完成")
finally:
    spider.close()
```

## 🆕 自动点击功能详解

### 支持的操作类型

1. **日期选择器自动点击**
   - 支持 `input[type="date"]` 元素
   - 支持自定义日期选择器
   - 支持日期链接点击
   - 自动触发change事件

2. **合约选择器自动点击**
   - 支持 `<select>` 下拉框
   - 支持自定义下拉组件
   - 支持合约链接点击
   - 智能匹配合约名称

3. **查询按钮自动点击**
   - 支持各种查询按钮样式
   - 支持提交表单
   - 支持回车键触发
   - 自动等待结果加载

### 智能识别策略

程序使用多种策略自动识别页面元素：

```python
# 日期选择器识别策略
date_selectors = [
    "//input[@type='date']",
    "//input[contains(@class, 'date')]",
    "//input[contains(@id, 'date')]",
    "//input[contains(@name, 'date')]",
    # ... 更多策略
]

# 合约选择器识别策略  
contract_selectors = [
    "//select[contains(@name, 'contract')]",
    "//select[contains(@id, 'contract')]",
    "//div[contains(@class, 'contract-select')]//select",
    # ... 更多策略
]

# 查询按钮识别策略
query_buttons = [
    "//button[contains(text(), '查询')]",
    "//input[@type='submit' and contains(@value, '查询')]",
    "//button[contains(@class, 'search')]",
    # ... 更多策略
]
```

## 输出格式

### 成功获取数据时的返回格式:

```json
{
    "success": true,
    "product_id": "IM",
    "date": "2024-01-15",
    "data": [
        {
            "headers": ["排名", "会员简称", "成交量", "增减量"],
            "rows": [
                {"排名": "1", "会员简称": "某期货公司", "成交量": "1000", "增减量": "+50"},
                ...
            ],
            "total_rows": 20
        }
    ],
    "timestamp": "2024-01-15T10:30:00"
}
```

### 获取数据失败时的返回格式:

```json
{
    "error": "没有查询到数据",
    "product_id": "IM",
    "date": "2024-01-15"
}
```

## 注意事项

1. **网站限制**: 中金所网站可能有反爬虫机制，建议:
   - 设置合理的请求间隔
   - 使用真实的浏览器User-Agent
   - 避免频繁请求

2. **数据可用性**: 
   - 持仓数据通常在交易日收盘后更新
   - 周末和节假日可能没有新数据
   - 部分历史数据可能不可用

3. **Chrome依赖**: 
   - 程序依赖Chrome浏览器和ChromeDriver
   - 确保版本匹配，否则可能无法正常运行

4. **网络环境**: 
   - 确保能够正常访问中金所官网
   - 网络不稳定时可能导致爬取失败

5. **🆕 自动点击功能**:
   - 建议首次使用时设置 `headless=False` 观察点击过程
   - 不同网站的页面结构可能需要调整识别策略
   - 自动点击失败时程序会继续尝试获取默认数据

## 故障排除

### 1. ChromeDriver相关错误
- 检查Chrome浏览器版本
- 下载匹配的ChromeDriver版本
- 确保ChromeDriver在PATH中

### 2. 网站访问失败
- 检查网络连接
- 尝试手动访问目标网站
- 检查是否被网站屏蔽

### 3. 数据解析失败
- 网站结构可能发生变化
- 查看生成的调试HTML文件
- 根据实际结构调整解析逻辑

### 4. 🆕 自动点击失败
- 检查页面元素是否存在
- 查看日志中的详细错误信息
- 尝试调整元素识别策略
- 使用非无头模式观察点击过程

## 日志文件

程序运行时会生成 `cffex_spider.log` 日志文件，记录详细的运行信息，包括：
- 页面访问记录
- 自动点击操作日志
- 数据获取状态
- 错误信息详情

## 法律声明

本程序仅供学习和研究使用，使用者应遵守相关网站的使用条款和法律法规。请合理使用，避免对目标网站造成过大负担。