# AKShare One MCP Server

<div align="center">
  <a href="README.md">English</a> | 
  <a href="README_zh.md">中文</a>
</div>

<!-- mcp-name: io.github.zwldarren/akshare-one-mcp -->

[![smithery badge](https://smithery.ai/badge/@zwldarren/akshare-one-mcp)](https://smithery.ai/server/@zwldarren/akshare-one-mcp)

[![PyPI version](https://img.shields.io/pypi/v/akshare-one-mcp)](https://pypi.org/project/akshare-one-mcp/)
[![PyPI downloads](https://img.shields.io/pypi/dm/akshare-one-mcp)](https://pypi.org/project/akshare-one-mcp/)
[![Python versions](https://img.shields.io/pypi/pyversions/akshare-one-mcp)](https://pypi.org/project/akshare-one-mcp/)
[![License: MIT](https://img.shields.io/github/license/zwldarren/akshare-one-mcp)](https://github.com/zwldarren/akshare-one-mcp/blob/main/LICENSE)

## Overview

An MCP server based on [akshare-one](https://github.com/zwldarren/akshare-one), providing comprehensive interfaces for China stock market data. It offers a set of powerful tools for retrieving financial information including historical stock data, real-time data, news data, and financial statements.

<a href="https://glama.ai/mcp/servers/@zwldarren/akshare-one-mcp">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@zwldarren/akshare-one-mcp/badge" alt="akshare-one-mcp MCP server" />
</a>

## Available Tools

### Automatic source fallback

Except for `get_news_data` and `get_inner_trade_data`, whose upstream exposes a single source, every tool takes a `source` parameter for the preferred data source and a `fallback` parameter (on by default) that decides whether the other sources of the same domain are tried when that source **raises** or **returns an empty frame**:

| Domain | Order tried |
| --- | --- |
| Historical | `eastmoney` → `eastmoney_direct` → `sina` |
| Real-time | `eastmoney_direct` → `eastmoney` → `xueqiu` (skipped when no symbol is given) |
| Financial statements | `sina` ⇄ `eastmoney_direct` |

The requested `source` is always tried first; the order only governs the fallback. Because akshare-one projects every source onto its domain's declared columns, falling back cannot change the field names or their order. When every source fails, the error lists each one and why it failed; when every source succeeds but has no data, an empty result is returned. Set `fallback` to `false` to pin a single source — a failure then surfaces directly, which is useful when you need to know exactly where the numbers came from.

The source that actually served a call is logged under the `akshare_one_mcp.providers` logger.

### Market Data Tools

#### `get_hist_data`
Get historical stock market data with support for multiple time periods and adjustment methods.

<details>
<summary>Parameters</summary>

- `symbol` (string, required): Stock code (e.g. '000001')
- `interval` (string, optional): Time interval ('minute','hour','day','week','month','year') (default: 'day')
- `interval_multiplier` (number, optional): Interval multiplier (default: 1)
- `start_date` (string, optional): Start date in YYYY-MM-DD format (default: '1970-01-01')
- `end_date` (string, optional): End date in YYYY-MM-DD format (default: '2030-12-31')
- `adjust` (string, optional): Adjustment type ('none', 'qfq', 'hfq') (default: 'none')
- `source` (string, optional): Data source ('eastmoney', 'eastmoney_direct', 'sina') (default: 'eastmoney')
- `fallback` (boolean, optional): Try 'eastmoney', 'eastmoney_direct' and 'sina' in order when the chosen source fails or has no data (default: true)
- `indicators_list` (list, optional): Technical indicators to add
- `recent_n` (number, optional): Number of most recent records to return (default: 100)

</details>

#### `get_realtime_data`
Get real-time stock market data.

<details>
<summary>Parameters</summary>

- `symbol` (string, optional): Stock code
- `source` (string, optional): Data source ('eastmoney_direct', 'eastmoney', 'xueqiu') (default: 'eastmoney_direct')
- `fallback` (boolean, optional): Try 'eastmoney_direct', 'eastmoney' and 'xueqiu' in order when the chosen source fails or has no data (default: true; 'xueqiu' is skipped when no symbol is given, as it quotes one symbol at a time)

</details>

### News & Information Tools

#### `get_news_data`
Get stock-related news data.

<details>
<summary>Parameters</summary>

- `symbol` (string, required): Stock code
- `recent_n` (number, optional): Number of most recent records to return (default: 10)

</details>

### Financial Statement Tools

#### `get_balance_sheet`
Get company balance sheet data.

<details>
<summary>Parameters</summary>

- `symbol` (string, required): Stock code
- `source` (string, optional): Data source ('sina', 'eastmoney_direct') (default: 'sina')
- `fallback` (boolean, optional): Try the other source when the chosen one fails or has no data (default: true)
- `recent_n` (number, optional): Number of most recent records to return (default: 10)

</details>

#### `get_income_statement`
Get company income statement data.

<details>
<summary>Parameters</summary>

- `symbol` (string, required): Stock code
- `source` (string, optional): Data source ('sina', 'eastmoney_direct') (default: 'sina')
- `fallback` (boolean, optional): Try the other source when the chosen one fails or has no data (default: true)
- `recent_n` (number, optional): Number of most recent records to return (default: 10)

</details>

#### `get_cash_flow`
Get company cash flow statement data.

<details>
<summary>Parameters</summary>

- `symbol` (string, required): Stock code
- `source` (string, optional): Data source ('sina', 'eastmoney_direct') (default: 'sina')
- `fallback` (boolean, optional): Try the other source when the chosen one fails or has no data (default: true)
- `recent_n` (number, optional): Number of most recent records to return (default: 10)

</details>

### Analysis & Metrics Tools

#### `get_inner_trade_data`
Get company insider trading data.

<details>
<summary>Parameters</summary>

- `symbol` (string, required): Stock code

</details>

#### `get_financial_metrics`
Get key financial metrics from the three major financial statements.

<details>
<summary>Parameters</summary>

- `symbol` (string, required): Stock code
- `source` (string, optional): Data source ('sina', 'eastmoney_direct') (default: 'eastmoney_direct')
- `fallback` (boolean, optional): Try the other source when the chosen one fails or has no data (default: true)
- `recent_n` (number, optional): Number of most recent records to return (default: 10)

</details>

#### `get_time_info`
Get current time with ISO format, timestamp, and the last trading day.

## Installation & Setup

### Running Modes

The server supports two modes: stdio and streamable-http

**Command Line Arguments:**
- `--streamable-http`: Enable HTTP mode (default: stdio mode)
- `--host`: Host to bind to in HTTP mode (default: 0.0.0.0)
- `--port`: Port to listen on in HTTP mode (default: 8081)

> **Note:** When using streamable-http mode, the MCP server will be available at `http://{host}:{port}/mcp`. For the default configuration, this would be `http://0.0.0.0:8081/mcp`.

### Installation Options

#### Option 1: Via Smithery
To install akshare-one-mcp for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@zwldarren/akshare-one-mcp):

```bash
npx -y @smithery/cli install @zwldarren/akshare-one-mcp --client claude
```

#### Option 2: Via `uv`
Install [uv](<https://docs.astral.sh/uv/getting-started/installation/>) if you haven't already.

`uvx` installs the package from [PyPI](https://pypi.org/project/akshare-one-mcp/) and runs it on Python 3.12 or newer.

Add the following configuration to your MCP Client settings:

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

#### Option 3: Local Development Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/zwldarren/akshare-one-mcp.git
   cd akshare-one-mcp
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Add the following configuration to your MCP Client settings:
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

## Technical Indicators Reference

The `get_hist_data` tool supports the following technical indicators:

### Trend Indicators
- **Moving Averages**: SMA (Simple Moving Average), EMA (Exponential Moving Average)
- **Trend Tracking**: MACD (Moving Average Convergence Divergence), APO (Absolute Price Oscillator), PPO (Percentage Price Oscillator)
- **Rate of Change**: ROC (Rate of Change), ROCP (Rate of Change Percentage), ROCR (Rate of Change Ratio), ROCR100
- **Other**: TRIX (Triple Exponential Moving Average), ULTOSC (Ultimate Oscillator)

### Momentum Indicators
- **Relative Strength**: RSI (Relative Strength Index), CCI (Commodity Channel Index)
- **Trend Strength**: ADX (Average Directional Index), DX (Directional Index)
- **Money Flow**: MFI (Money Flow Index), MOM (Momentum), CMO (Chande Momentum Oscillator), WILLR (Williams %R)

### Volatility Indicators
- **Bollinger Bands**: BOLL (Bollinger Bands)
- **Average True Range**: ATR (Average True Range)
- **Parabolic SAR**: SAR (Parabolic Stop and Reverse)

### Volume Indicators
- **Volume**: OBV (On-Balance Volume), AD (Accumulation/Distribution Line), ADOSC (Accumulation/Distribution Oscillator)

### Other Indicators
- **Stochastic**: STOCH (Stochastic Oscillator)
- **Aroon**: AROON (Aroon Indicator), AROONOSC (Aroon Oscillator)
- **Balance of Power**: BOP (Balance of Power)
- **Directional Indicators**: MINUS_DI, MINUS_DM, PLUS_DI, PLUS_DM
- **Time Series Forecast**: TSF (Time Series Forecast)
