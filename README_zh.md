# AKShare One MCP 服务器

<div align="center">
  <a href="README.md">English</a> |
  <a href="README_zh.md">中文</a>
</div>

[![smithery badge](https://smithery.ai/badge/@zwldarren/akshare-one-mcp)](https://smithery.ai/server/@zwldarren/akshare-one-mcp)

[![PyPI version](https://img.shields.io/pypi/v/akshare-one-mcp)](https://pypi.org/project/akshare-one-mcp/)
[![PyPI downloads](https://img.shields.io/pypi/dm/akshare-one-mcp)](https://pypi.org/project/akshare-one-mcp/)
[![Python versions](https://img.shields.io/pypi/pyversions/akshare-one-mcp)](https://pypi.org/project/akshare-one-mcp/)
[![License: MIT](https://img.shields.io/github/license/zwldarren/akshare-one-mcp)](https://github.com/zwldarren/akshare-one-mcp/blob/main/LICENSE)

这是一个基于 [akshare-one](https://github.com/zwldarren/akshare-one) 的 MCP (Model Context Protocol) 服务器，为中国股票市场提供全面的数据接口服务。

<a href="https://glama.ai/mcp/servers/@zwldarren/akshare-one-mcp">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@zwldarren/akshare-one-mcp/badge" alt="akshare-one-mcp MCP 服务器" />
</a>

## 功能特性

- **历史数据**: 获取股票历史行情数据，支持多种时间周期和复权方式
- **实时数据**: 提供实时股票行情信息
- **新闻资讯**: 获取股票相关的最新新闻资讯
- **财务报表**: 查看公司资产负债表、利润表、现金流量表
- **分析指标**: 计算关键财务指标和技术分析指标
- **自动降级**: 首选数据源失败或没有数据时，自动按顺序尝试同领域的其他数据源

## 工具说明

### 数据源自动降级

除 `get_news_data` 和 `get_inner_trade_data`（上游只有一个数据源）外，每个工具的 `source` 参数都可以指定首选数据源，`fallback` 参数（默认开启）决定首选数据源**报错**或**返回空数据**时，是否继续尝试同领域的其他数据源：

| 领域 | 尝试顺序 |
| --- | --- |
| 历史行情 | `eastmoney` → `eastmoney_direct` → `sina` |
| 实时行情 | `eastmoney_direct` → `eastmoney` → `xueqiu`（未指定股票代码时跳过 `xueqiu`） |
| 财务报表 | `sina` ⇄ `eastmoney_direct` |

指定的 `source` 始终排在第一位，顺序只是降级时的尝试次序。akshare-one 会把每个数据源的结果对齐到该领域声明的列，因此降级不会改变返回的字段名和字段顺序。所有数据源都失败时会抛出错误并逐一列出失败原因；如果全部数据源都成功但都没有数据，则返回空结果。把 `fallback` 设为 `false` 可以固定单一数据源，此时数据源出错会直接报错，便于确认数据到底来自哪里。

每个工具通过日志（`akshare_one_mcp.providers`）记录实际提供数据的数据源。

### 市场数据

#### `get_hist_data` - 获取历史股票数据
获取指定股票的历史行情数据，支持多种数据源和复权方式。

<details>
<summary>参数说明</summary>

- `symbol` (string, 必填): 股票代码，如 '000001'
- `interval` (string, 可选): 时间周期，可选值：'minute'(分钟)、'hour'(小时)、'day'(日线)、'week'(周线)、'month'(月线)、'year'(年线)，默认 'day'
- `interval_multiplier` (number, 可选): 时间周期倍数（如 5 表示 5 分钟），默认 1
- `start_date` (string, 可选): 开始日期，格式：YYYY-MM-DD，默认 '1970-01-01'
- `end_date` (string, 可选): 结束日期，格式：YYYY-MM-DD，默认 '2030-12-31'
- `adjust` (string, 可选): 复权方式，'none'(不复权)、'qfq'(前复权)、'hfq'(后复权)，默认 'none'
- `source` (string, 可选): 数据源，'eastmoney'(东方财富)、'eastmoney_direct'(东方财富直连)、'sina'(新浪)，默认 'eastmoney'
- `fallback` (boolean, 可选): 首选数据源失败或没有数据时，是否按 'eastmoney'、'eastmoney_direct'、'sina' 的顺序尝试其他数据源，默认 true
- `indicators_list` (list, 可选): 技术指标列表
- `recent_n` (number, 可选): 返回最新记录数，默认 100

</details>

#### `get_realtime_data` - 获取实时股票数据

<details>
<summary>参数说明</summary>

- `symbol` (string, 可选): 股票代码，留空获取所有股票概览
- `source` (string, 可选): 数据源，'eastmoney_direct'(东方财富直连)、'eastmoney'(东方财富)、'xueqiu'(雪球)，默认 'eastmoney_direct'
- `fallback` (boolean, 可选): 首选数据源失败或没有数据时，是否按 'eastmoney_direct'、'eastmoney'、'xueqiu' 的顺序尝试其他数据源，默认 true（未指定股票代码时不会尝试 'xueqiu'，它只能查询单只股票）

</details>

### 新闻资讯

#### `get_news_data` - 获取股票新闻

<details>
<summary>参数说明</summary>

- `symbol` (string, 必填): 股票代码
- `recent_n` (number, 可选): 返回最新记录数，默认 10

</details>

### 财务报表

#### `get_balance_sheet` - 获取资产负债表

<details>
<summary>参数说明</summary>

- `symbol` (string, 必填): 股票代码
- `source` (string, 可选): 数据源，'sina'(新浪)、'eastmoney_direct'(东方财富直连)，默认 'sina'
- `fallback` (boolean, 可选): 首选数据源失败或没有数据时，是否尝试另一个数据源，默认 true
- `recent_n` (number, 可选): 返回最新记录数，默认 10

</details>

#### `get_income_statement` - 获取利润表

<details>
<summary>参数说明</summary>

- `symbol` (string, 必填): 股票代码
- `source` (string, 可选): 数据源，'sina'(新浪)、'eastmoney_direct'(东方财富直连)，默认 'sina'
- `fallback` (boolean, 可选): 首选数据源失败或没有数据时，是否尝试另一个数据源，默认 true
- `recent_n` (number, 可选): 返回最新记录数，默认 10

</details>

#### `get_cash_flow` - 获取现金流量表


<details>
<summary>参数说明</summary>

- `symbol` (string, 必填): 股票代码
- `source` (string, 可选): 数据源，'sina'(新浪)、'eastmoney_direct'(东方财富直连)，默认 'sina'
- `fallback` (boolean, 可选): 首选数据源失败或没有数据时，是否尝试另一个数据源，默认 true
- `recent_n` (number, 可选): 返回最新记录数，默认 10

</details>

### 分析指标

#### `get_inner_trade_data` - 获取内部交易数据


<details>
<summary>参数说明</summary>

- `symbol` (string, 必填): 股票代码

</details>

#### `get_financial_metrics` - 获取财务指标

<details>
<summary>参数说明</summary>

- `symbol` (string, 必填): 股票代码
- `source` (string, 可选): 数据源，'sina'(新浪)、'eastmoney_direct'(东方财富直连)，默认 'eastmoney_direct'
- `fallback` (boolean, 可选): 首选数据源失败或没有数据时，是否尝试另一个数据源，默认 true
- `recent_n` (number, 可选): 返回最新记录数，默认 10

</details>

#### `get_time_info` - 获取时间信息

获取当前时间、时间戳和最近一个交易日信息。


## 运行模式

服务器支持两种运行模式：**stdio** 和 **streamable-http**

### 命令行参数
- `--streamable-http`: 启用 HTTP 模式 (默认为 stdio 模式)
- `--host`: HTTP 模式绑定的主机地址 (默认: 0.0.0.0)
- `--port`: HTTP 模式监听的端口 (默认: 8081)

> **说明:** 启用 streamable-http 模式后，MCP 服务器将在 `http://{host}:{port}/mcp` 提供服务。默认地址为 `http://0.0.0.0:8081/mcp`

## 安装指南

### 通过 Smithery 安装

通过 [Smithery](https://smithery.ai/server/@zwldarren/akshare-one-mcp) 自动安装，适用于 Claude Desktop：

```bash
npx -y @smithery/cli install @zwldarren/akshare-one-mcp --client claude
```

### 快速安装

如果尚未安装 [uv](https://docs.astral.sh/uv/getting-started/installation/)，请先安装。

`uvx` 会从 [PyPI](https://pypi.org/project/akshare-one-mcp/) 安装包，并需要 Python 3.12 或更高版本。

在 MCP 客户端配置中添加以下设置：

```json
{
  "mcpServers": {
    "akshare-one-mcp": {
      "command": "uvx",
      "args": ["akshare-one-mcp"]
    }
  }
}
```

### 通过代码库本地安装

1. **克隆仓库**
   ```bash
   git clone https://github.com/zwldarren/akshare-one-mcp.git
   cd akshare-one-mcp
   ```

2. **安装依赖**
   ```bash
   uv sync
   ```

3. **配置 MCP 客户端**
   ```json
   {
     "mcpServers": {
       "akshare-one-mcp": {
         "command": "uv",
         "args": [
           "--directory",
           "/path/to/akshare-one-mcp",
           "run",
           "akshare-one-mcp"
         ]
       }
     }
   }
   ```

## 技术指标

`get_hist_data` 工具支持下面这些技术分析指标：

### 趋势指标
- **移动平均**: SMA (简单移动平均)、EMA (指数移动平均)
- **趋势跟踪**: MACD (指数平滑异同移动平均线)、APO (价格振荡器)、PPO (百分比价格振荡器)
- **变化率**: ROC (变化率)、ROCP (变化率百分比)、ROCR (变化率比率)、ROCR100
- **其他**: TRIX (三重指数平滑移动平均)、ULTOSC (终极振荡器)

### 动量指标
- **相对强弱**: RSI (相对强弱指数)、CCI (商品通道指数)
- **趋势强度**: ADX (平均趋向指数)、DX (趋向指数)
- **资金流向**: MFI (资金流量指标)、MOM (动量)、CMO (钱德动量摆动指标)、WILLR (威廉指标)

### 波动率指标
- **布林带**: BOLL (布林带)
- **真实波幅**: ATR (平均真实波幅)
- **抛物线**: SAR (抛物线转向)

### 成交量指标
- **成交量**: OBV (能量潮)、AD (累积/派发线)、ADOSC (累积/派发振荡器)

### 其他指标
- **随机指标**: STOCH (随机振荡器)
- **阿隆指标**: AROON (阿隆指标)、AROONOSC (阿隆振荡器)
- **平衡动能**: BOP (平衡动能)
- **趋向指标**: MINUS_DI、MINUS_DM、PLUS_DI、PLUS_DM
- **时间序列**: TSF (时间序列预测)
