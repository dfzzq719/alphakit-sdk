![AlphaKit SDK：把市场数据接进你的程序，连接 A 股、港股与美股数据研究](https://raw.githubusercontent.com/dfzzq719/docs/6713a76dfe329b26fdf845a8e0bdd1f7f26ddac6/images/alphakit-sdk-wide-banner-20261025.webp)

# AlphaKit SDK：Python A 股、港股与美股数据

**把行情、估值和行业数据接入 Python，让研究从一张可用的数据表开始。**

AlphaKit SDK 是 AlphaKit 数据服务的 Python 客户端，安装包名为 `alphakit-sdk`，导入名为 `alphakit`。A 股查询与港美股历史日线返回 `pandas.DataFrame`，查询后即可继续排序、合并、分析和保存；港美股搜索、行情及覆盖查询返回包含元数据的字典。

- **从价格走到估值：** 查询日线、PE、PB、市值与复权因子，按证券代码和日期整理研究样本。
- **把个股放回行业与市场：** 结合申万行业、同花顺板块、指数和 ETF 数据，为历史比较补充参照。
- **在同一个客户端研究不同市场：** 查询 A 股数据，以及港股、美股的证券目录、单标的行情和历史日线。

## 申请访问

通过微信 **dfzzq719** 联系，申请时请注明：SDK。

获取有效的 Token 和 HTTPS 数据服务地址后即可使用；申请时可了解数据范围、配额与使用条件。

## 页内目录

- [申请访问](#申请访问)
- [SDK、MCP、网页怎么选](#sdkmcp网页怎么选)
- [数据能力](#可以查询什么)
- [按研究任务找入口](#按研究任务找入口)
- [安装与首次查询](#几行代码拿到第一份历史日线)
- [查询结果长什么样](#查询结果长什么样)
- [价格与估值对齐](#继续一步把价格与-pepb-放进同一张表)
- [港美股查询与覆盖](#港股与美股查覆盖取日线保留元数据)
- [错误处理](#查询与错误处理)
- [MCP 特色与接入](#配套-mcp让-ai-对话连接金融数据)
- [网页工具实景](#配套网页研究工具)
- [常见问题](#常见问题)
- [文档与联系](#文档与联系)

## SDK、MCP、网页怎么选

| 你想做什么 | 推荐入口 | 怎样开始 |
|---|---|---|
| 在 Python 中获取数据、整理样本和计算 | Python SDK | 安装 `alphakit-sdk`，配置 Token 与 HTTPS 数据服务地址，在自己的脚本中调用查询方法 |
| 用自然语言研究 A 股，或在 AI 客户端调用行情工具 | MCP 服务 | 在支持相应连接方式的 AI 客户端中配置 AlphaKit MCP，启用获授权的工具 |
| 直接查看 K 线、技术指标与历史分位 | AlphaView 网页工具 | 登录 AlphaKit，在浏览器中打开 AlphaView 查看图表 |

三种入口可以配合使用，服务与数据范围按账户分别授权。SDK 的查询方法、MCP 工具与网页功能各有适用范围。

## 可以查询什么

| 数据能力 | 适合怎样的研究 | 方法示例 |
|---|---|---|
| A 股基础信息与日线 | 查找证券资料，获取指定日期或区间的行情 | `stock_basic()`、`daily()` |
| 每日估值、复权与技术因子 | 将 PE、PB、市值与价格对齐，补充复权因子和技术因子 | `daily_basic()`、`adj_factor()`、`stk_factor()` |
| 行业与板块 | 按申万三级行业或同花顺板块组织研究分组，查看行业、板块走势与成分 | `sw_l1()`、`sw_l2()`、`sw_l3()`、`sw_daily()`、`sw_stock_industry()`、`ths_index()`、`ths_daily()`、`ths_member()` |
| 指数与 ETF | 用指数、ETF 行情作历史参照，补充净值、份额和主题资料 | `index_daily()`、`index_dailybasic()`、`etf_basic()`、`etf_daily()`、`etf_nav()`、`etf_share()`、`etf_theme_map()` |
| 资金流与市场行为 | 为量价研究补充资金流、两融、涨跌停、龙虎榜及停复牌信息 | `moneyflow()`、`moneyflow_dc()`、`margin()`、`margin_detail()`、`limit_list_d()`、`top_list()`、`hm_detail()`、`kpl_list()`、`suspend_d()` |
| 港股与美股 | 按代码查找研究标的，查询单标的行情、历史日线和数据覆盖范围 | `overseas_search()`、`overseas_quote()`、`overseas_daily()`、`overseas_coverage()` |
| 期权与通用查询 | 获取期权基础资料、日线，或调用服务端支持的其他数据接口 | `opt_basic()`、`opt_daily()`、`query()` |

可用接口、字段、历史范围和配额以接口说明及账户权限为准。仅供个人学习与研究使用。

## 按研究任务找入口

| 研究任务 | 从哪里开始 | 阅读位置 |
|---|---|---|
| 整理某只 A 股的历史价格序列 | 用 `daily()` 指定证券代码与日期范围，再按交易日排序 | [首次日线查询](#几行代码拿到第一份历史日线) |
| 把价格与 PE、PB 放进同一张表 | 分别查询 `daily()`、`daily_basic()`，按证券代码与日期合并 | [行情与估值对齐示例](#继续一步把价格与-pepb-放进同一张表) |
| 按行业归属组织研究样本 | 用 `sw_stock_industry()` 补充当前行业归属，再结合行业资料分组 | [行业与板块方法](#可以查询什么) |
| 给个股研究补充指数或 ETF 历史参照 | 从 `index_daily()`、`etf_daily()` 获取相应行情，再按日期对齐 | [指数与 ETF 方法](#可以查询什么) |
| 查询港美股某段历史数据 | 先用 `overseas_coverage()` 看范围，再用 `overseas_daily()` 取日线并保留元数据 | [港美股查询示例](#港股与美股查覆盖取日线保留元数据) |

## 几行代码，拿到第一份历史日线

需要 Python 3.8 或以上：

```bash
python -m pip install --upgrade alphakit-sdk
```

将凭证保存为环境变量 `ALPHAKIT_TOKEN` 和 `ALPHAKIT_BASE_URL`；在代码中读取环境变量，避免将 Token 写入公开代码、截图或仓库。

```python
import os
import alphakit as ak

api = ak.AlphaKit(
    token=os.environ["ALPHAKIT_TOKEN"],
    base_url=os.environ["ALPHAKIT_BASE_URL"],
)

df = api.daily(
    ts_code="000001.SZ",
    start_date="20260101",
    end_date="20260630",
)
if df.empty:
    print("本次没有返回数据，请核对代码、日期与账户可用范围。")
else:
    df = df.sort_values("trade_date").reset_index(drop=True)
    print(df[["ts_code", "trade_date", "close", "vol"]].tail(3))
```

A 股日期使用 `YYYYMMDD`，证券代码带交易所后缀，如 `000001.SZ`、`600519.SH`。仅向 `daily()` 传入 `ts_code`、不带日期参数时，默认查询最近 365 天；为了复现研究，建议显式指定日期。

### 查询结果长什么样

`daily()` 返回 `pandas.DataFrame`。选取部分列后，可以像下面这样查看数据；以下是**格式示意（合成数据，非真实行情）**，实际数值、行数和字段以查询响应为准：

```text
     ts_code trade_date  close   vol
0  000001.SZ   20260105   10.0  1000
1  000001.SZ   20260106   10.5  1200
2  000001.SZ   20260107   10.2  1100
```

拿到表格后，可继续按日期排序、选择列、合并估值数据，或用 `df.to_csv("daily.csv", index=False)` 保存为 CSV。字段单位与价格口径请查看对应接口说明，缺失值按原样保留。

## 继续一步：把价格与 PE、PB 放进同一张表

沿用上面的客户端与日线结果，再查询同一证券、同一日期范围的估值数据：

```python
valuation = api.daily_basic(
    ts_code="000001.SZ",
    start_date="20260101",
    end_date="20260630",
)

if not df.empty and not valuation.empty:
    research = df.merge(
        valuation,
        on=["ts_code", "trade_date"],
        how="left",
        suffixes=("", "_valuation"),
    )
    print(research[["ts_code", "trade_date", "close", "pe", "pb"]].tail())
```

这样可以保留日线记录，并按交易日对齐 PE、PB；没有对应估值的日期保留为空值。实际字段以接口响应为准。行业映射可继续通过 `api.sw_stock_industry(ts_code="000001.SZ")` 查询，用于补充当前行业归属。

## 港股与美股：查覆盖、取日线、保留元数据

使用 0.2.9 或以上版本，显式配置 HTTPS 数据服务地址。公共网关为 `https://alphakit.cn`，账户需要 SDK 服务权限与相应数据权限。

```python
# 沿用已配置 HTTPS 服务地址的 api。
coverage = api.overseas_coverage("US")
print(coverage["coverage"])

us = api.overseas_daily("US", "AAPL", since="20260101", to="20260630")
hk = api.overseas_daily("HK", "00700", since="20260101", to="20260630")
spy = api.overseas_daily("US", "SPY", since="20260101", to="20260630")
print(us.tail())
print(us.attrs["metadata"])

securities = api.overseas_search("US", "AAPL")
quote = api.overseas_quote("US", "SPY", instrument="etf")
```

港股使用五位证券代码，美股使用证券代码；ETF 单标的行情显式传入 `instrument="etf"`。历史日线字段为 `trade_date`、`open`、`high`、`low`、`close`、`volume`。

日期支持 `YYYYMMDD` 或 `YYYY-MM-DD`。`to` 省略时为当天，`since` 省略时为 `to` 所属年份的 1 月 1 日，因此不传日期默认查询本年度。单次最多返回 2,000 行；超出 `limit` 时返回最近的记录，`DataFrame.attrs["metadata"]` 中的 `truncated` 会标明截断。空结果也保留元数据和股票状态。

### 怎样理解可查询范围

| 覆盖信息 | 怎样使用 |
|---|---|
| `complete_through` | 历史日线的完整更新截止日期，日线查询按这一范围返回 |
| `available_through` | 数据源的最新可用日期，部分更新的数据会在完整更新后纳入历史日线查询 |
| `published_years` | 数据源已发布的年份，具体可查询情况以服务端数据准备状态为准 |

指定 `symbol` 的覆盖查询默认查看本年度。跨年范围内任一年缓存未就绪时返回 `AlphaKitError(code=503)`，请稍后重试；接口不会因缓存缺失而省略该年份。返回元数据包含本次实际起止日期，便于核对研究区间。

港美股历史日线采用原始、不复权价格，缺失值按原样保留。覆盖日期表示更新进度，不能直接推定全市场、逐交易日或历史成分覆盖。行情请结合响应中的数据时间和交易状态使用，时效以返回时间为准。

证券搜索基于最近完整年度的历史目录，名称搜索仅覆盖已有名称信息的证券，目录范围可能与实时上市名单不同。查询遵循账户权限、IP 绑定、请求频率、每日配额及股票参与规则；研究查询保留资料并返回当前股票状态。

## 查询与错误处理

`query(api_name, **params)` 可调用服务端支持且账户有权访问的其他接口。`weekly`、`monthly`、`fina_indicator` 没有对应的专用客户端方法；通用查询的可用范围由服务端及账户权限决定。

```python
from alphakit.exceptions import AlphaKitError

try:
    result = api.stock_basic(ts_code="000001.SZ")
except AlphaKitError as exc:
    print(f"查询失败，错误码：{exc.code}")
```

港美股方法保留服务端 HTTP 错误码：401 为凭证无效，403 为权限或 IP 受限，409 为查询期间股票参与规则变化，422 为参数错误，429 为限频或配额限制，503 为数据未就绪、服务关闭或上游暂不可用。客户端不自动重试；网络失败、超时或无法解析响应时使用 `code=9999`。

A 股及通用方法将连接失败、超时和 HTTP 错误响应包装为 `AlphaKitError(code=9999)`，包括 HTTP 401、403、429。HTTP 请求成功、响应包含非零业务码时，保留该业务码：1001 为 Token 无效，1002 为无接口权限，1003 为 IP 限制，1004 为限频，1005 为当日配额用尽，1006 为参数错误，1500 为服务端错误。排查时结合错误消息、凭证、权限和配额检查，联系支持时提供发生时间、接口名与脱敏后的错误信息。

## 配套 MCP：让 AI 对话连接金融数据

除了用 Python 编写查询，你也可以通过 AlphaKit MCP 服务，在支持远程 SSE 与 Bearer 认证的 AI 客户端中发起数据研究。

- **用自然语言开展 A 股研究：** 支持个股分析、双股比较与估值条件筛选，例如“分析贵州茅台”“贵州茅台与五粮液对比”，或“筛选 PE 小于 30 且市值大于 100 亿的股票”。
- **把盘中数据带入对话：** 查询单只 A 股或 ETF 的最新可用报价、当日分钟线，支持 1、5、15、30、60 分钟周期。
- **在同一入口查询港股与美股：** 搜索证券，获取单标的行情、历史日线和数据覆盖范围，结合返回的数据日期与状态开展研究。
- **从对话探索衔接到 Python 分析：** 先在 AI 客户端中明确研究问题，再通过 SDK 按证券代码和日期获取所需数据，在 pandas 中继续清洗、合并、计算和保存。

MCP 需在 AI 客户端中单独配置，使用 AlphaKit Token 认证；SDK 与 MCP 服务权限按账户分别授权，工具与数据范围以账户权限为准。行情时效以返回的数据时间为准。

接入方式与平台配置：登录 [AlphaKit 官网](https://alphakit.cn/)，进入「数据服务」，查看「MCP 接入」与「平台配置」。

## 配套网页研究工具

![AlphaKit SDK 数据研究与配套 AlphaView 网页工具的真实 K 线界面](https://raw.githubusercontent.com/dfzzq719/docs/08aa78d3e21deddea3e100451f6a14c732448b9d/images/alphakit-sdk-saas-promo-20261022.webp)

图中为配套网页工具 AlphaView 的产品实景。Python SDK 提供数据查询接口，网页工具提供行情图表、技术指标与历史分位查看，具体范围按账户权限开放。

## 常见问题

**安装后就能直接查询吗？**

安装提供 Python 客户端。真实查询还需要有效的 AlphaKit Token、HTTPS 数据服务地址，以及对应的 SDK 服务权限与数据权限；申请方式见正文前部的「申请访问」。

**SDK 和 MCP 可以使用同一个 Token 吗？**

可以使用自己的 AlphaKit Token 认证，SDK 与 MCP 的服务权限分别检查。已有某一入口的访问权限时，仍需确认另一个入口及所需数据是否已授权；MCP 还需在 AI 客户端中单独配置。

**可以获取实时行情吗？**

SDK 的 A 股日线用于历史数据研究；A 股或 ETF 的最新可用报价、当日分钟线可通过 MCP 查询。港美股行情和历史日线请结合响应中的数据日期、交易状态与覆盖范围使用，时效以返回的数据时间为准。

**查询为空或报错时，先检查什么？**

先核对证券代码、市场、日期参数、服务权限、数据权限与配额；港美股历史查询可先查看覆盖信息，再按错误码处理。空结果或缺失值不等于零。联系支持时提供接口名、发生时间和脱敏后的错误信息，避免发送完整 Token。

## 文档与联系

通过微信 **dfzzq719** 联系，申请时请注明：SDK。

[SDK 使用文档](https://alphakit.cn/help/sdk/quick-start.html)

## 可运行示例与问题反馈

[运行两个 Python 研究示例](EXAMPLES.md) · [反馈问题](SUPPORT.md) · [版本记录](releases/)

本仓库公开使用文档、调用示例与离线测试。示例代码采用 MIT 许可；SDK 安装包沿用各版本的许可声明。AlphaKit 服务端与核心业务实现保持私有，数据访问按账户授权。详见 [公开范围与许可](COPYRIGHT.md)。
