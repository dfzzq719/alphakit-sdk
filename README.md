![AlphaKit SDK：把市场数据接进你的程序](https://raw.githubusercontent.com/dfzzq719/docs/6713a76dfe329b26fdf845a8e0bdd1f7f26ddac6/images/alphakit-sdk-wide-banner-20261025.webp)

# AlphaKit SDK：Python A 股数据

**把行情、估值和行业数据接入 Python，让研究从一张可用的数据表开始。**

AlphaKit SDK 是 AlphaKit 数据服务的 Python 客户端，安装包名为 `alphakit-sdk`，导入名为 `alphakit`。A 股查询返回 `pandas.DataFrame`，查询后即可继续排序、合并、分析和保存。

自 `0.2.22` 起，SDK 默认通过 `https://alphakit.cn` 连接。旧版可在 `AlphaKit()` 中显式设置 `base_url="https://alphakit.cn"`，使用自定义 `ALPHAKIT_BASE_URL` 的脚本也需更新环境变量。

- **从价格走到估值：** 查询日线、PE、PB、市值与复权因子，按证券代码和日期整理研究样本。
- **把个股放回行业与市场：** 结合申万行业、同花顺板块、指数和 ETF 数据，为历史比较补充参照。

## 申请访问

通过微信 **dfzzq719** 联系，申请时请注明：SDK。

**通过微信申请，可享 30 天免费试用。** 获取有效的 Token 和 HTTPS 数据服务地址后即可使用；申请时可了解数据范围、配额与使用条件。

## 数据服务套餐与价格

SDK 客户端免费下载；以下为数据服务费用，价格均为人民币。开通相应套餐并获取有效 Token 后，即可通过 SDK 查询已授权的数据。

**先试用，再选套餐：通过微信申请的用户可享 30 天免费试用，试用后可按需选择月付或年付。**

| 数据服务套餐 | 月付价格 | 年付价格 |
|---|---|---|
| A 股数据 | 20 元 / 月 | 180 元 / 年（折合 15 元 / 月） |

试用及付费服务的数据范围、接口权限、历史范围、请求频率与每日配额，请在开通前确认。

## 页内目录

- [申请访问](#申请访问)
- [数据服务套餐与价格](#数据服务套餐与价格)
- [SDK、MCP、网页怎么选](#sdkmcp网页怎么选)
- [数据能力](#可以查询什么)
- [按研究任务找入口](#按研究任务找入口)
- [安装与首次查询](#几行代码拿到第一份历史日线)
- [查询结果长什么样](#查询结果长什么样)
- [价格与估值对齐](#继续一步把价格与-pepb-放进同一张表)
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
| 期权与通用查询 | 获取期权基础资料、日线，或调用服务端支持的其他数据接口 | `opt_basic()`、`opt_daily()`、`query()` |

可用接口、字段、历史范围和配额以接口说明及账户权限为准。仅供个人学习与研究使用。

## 按研究任务找入口

| 研究任务 | 从哪里开始 | 阅读位置 |
|---|---|---|
| 整理某只 A 股的历史价格序列 | 用 `daily()` 指定证券代码与日期范围，再按交易日排序 | [首次日线查询](#几行代码拿到第一份历史日线) |
| 把价格与 PE、PB 放进同一张表 | 分别查询 `daily()`、`daily_basic()`，按证券代码与日期合并 | [行情与估值对齐示例](#继续一步把价格与-pepb-放进同一张表) |
| 按行业归属组织研究样本 | 用 `sw_stock_industry()` 补充当前行业归属，再结合行业资料分组 | [行业与板块方法](#可以查询什么) |
| 给个股研究补充指数或 ETF 历史参照 | 从 `index_daily()`、`etf_daily()` 获取相应行情，再按日期对齐 | [指数与 ETF 方法](#可以查询什么) |

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

## 查询与错误处理

`query(api_name, **params)` 可调用服务端支持且账户有权访问的其他接口。`weekly`、`monthly`、`fina_indicator` 没有对应的专用客户端方法；通用查询的可用范围由服务端及账户权限决定。

```python
from alphakit.exceptions import AlphaKitError

try:
    result = api.stock_basic(ts_code="000001.SZ")
except AlphaKitError as exc:
    print(f"查询失败，错误码：{exc.code}")
```

A 股及通用方法将连接失败、超时和 HTTP 错误响应包装为 `AlphaKitError(code=9999)`，包括 HTTP 401、403、429。HTTP 请求成功、响应包含非零业务码时，保留该业务码：1001 为 Token 无效，1002 为无接口权限，1003 为 IP 限制，1004 为限频，1005 为当日配额用尽，1006 为参数错误，1500 为服务端错误。排查时结合错误消息、凭证、权限和配额检查，联系支持时提供发生时间、接口名与脱敏后的错误信息。

## 配套 MCP：让 AI 对话连接金融数据

除了用 Python 编写查询，你也可以通过 AlphaKit MCP 服务，在支持远程 SSE 与 Bearer 认证的 AI 客户端中发起数据研究。

- **用自然语言开展 A 股研究：** 支持个股分析、双股比较与估值条件筛选，例如“分析贵州茅台”“贵州茅台与五粮液对比”，或“筛选 PE 小于 30 且市值大于 100 亿的股票”。
- **把盘中数据带入对话：** 查询单只 A 股或 ETF 的最新可用报价、当日分钟线，支持 1、5、15、30、60 分钟周期。
- **从对话探索衔接到 Python 分析：** 先在 AI 客户端中明确研究问题，再通过 SDK 按证券代码和日期获取所需数据，在 pandas 中继续清洗、合并、计算和保存。

MCP 需在 AI 客户端中单独配置，使用 AlphaKit Token 认证；SDK 与 MCP 服务权限按账户分别授权，工具与数据范围以账户权限为准。行情时效以返回的数据时间为准。

接入方式与平台配置：登录 [AlphaKit 官网](https://alphakit.cn/)，进入「数据服务」，查看「MCP 接入」与「平台配置」。

## 配套网页研究工具

![AlphaKit SDK 数据研究与配套 AlphaView 网页工具的真实 K 线界面](https://raw.githubusercontent.com/dfzzq719/docs/08aa78d3e21deddea3e100451f6a14c732448b9d/images/alphakit-sdk-saas-promo-20261022.webp)

图中为配套网页工具 AlphaView 的产品实景。Python SDK 提供数据查询接口，网页工具提供行情图表、技术指标与历史分位查看，具体范围按账户权限开放。

## 常见问题

**安装后就能直接查询吗？**

SDK 客户端可免费下载。通过微信申请可享 30 天免费试用；开通后配置有效的 AlphaKit Token、HTTPS 数据服务地址，以及对应的 SDK 服务权限与数据权限，即可查询已授权的数据。试用后可按「数据服务套餐与价格」选择相应服务；申请方式见正文前部的「申请访问」。

**SDK 和 MCP 可以使用同一个 Token 吗？**

可以使用自己的 AlphaKit Token 认证，SDK 与 MCP 的服务权限分别检查。已有某一入口的访问权限时，仍需确认另一个入口及所需数据是否已授权；MCP 还需在 AI 客户端中单独配置。

**可以获取实时行情吗？**

SDK 的 A 股日线用于历史数据研究。A 股或 ETF 的最新可用报价、当日分钟线可通过 MCP 查询，时效以返回的数据时间为准。

**查询为空或报错时，先检查什么？**

先核对证券代码、日期参数、服务权限、数据权限与配额，再按错误码处理。空结果或缺失值不等于零。联系支持时提供接口名、发生时间和脱敏后的错误信息，避免发送完整 Token。

## 文档与联系

通过微信 **dfzzq719** 联系，申请时请注明：SDK。

[SDK 使用文档](https://alphakit.cn/help/sdk/quick-start.html)

## 可运行示例与问题反馈

[运行两个 Python 研究示例](EXAMPLES.md) · [反馈问题](SUPPORT.md) · [版本记录](releases/)

本仓库公开使用文档、调用示例与离线测试。示例代码采用 MIT 许可；SDK 安装包沿用各版本的许可声明。AlphaKit 服务端与核心业务实现保持私有，数据访问按账户授权。详见 [公开范围与许可](COPYRIGHT.md)。
