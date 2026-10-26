# 从第一张数据表开始

这两个示例帮助你完成实际的数据整理：查询一只股票的历史日线，以及把价格、PE、PB 按证券代码和日期放到同一张表中。

## 安装

需要 Python 3.8 或以上。在本仓库根目录运行：

```console
python -m pip install -r requirements.txt
python examples/sdk/daily_history.py --help
```

## 无需 Token 的合成演示

```console
python examples/sdk/daily_history.py --demo
python examples/sdk/valuation_alignment.py --demo --csv
```

演示使用人为构造的小样本，不是真实行情，也不会发起网络请求。样本保留缺失 PE/PB、负 PE 和两张表中不同的日期，便于理解数据对齐。

第二个脚本采用一对一外合并：`both` 表示两张表都有该日期，`left_only` 表示只有行情，`right_only` 表示只有估值。不会用零填充缺失值，不会删掉负 PE，也不会补造交易日。返回重复的证券代码与日期时会明确报错。

## 使用已授权的数据服务

通过微信 **dfzzq719** 联系，申请时请注明：SDK。

获得 Token、完整的 HTTPS 数据服务基址及对应权限后，在本地环境中设置 `ALPHAKIT_TOKEN` 和 `ALPHAKIT_BASE_URL`。使用管理方提供的基址，不要把官网地址或完整查询端点直接当作基址。

```console
python examples/sdk/daily_history.py --ts-code 000001.SZ --start-date 20250102 --end-date 20250108
python examples/sdk/valuation_alignment.py --ts-code 000001.SZ --start-date 20250102 --end-date 20250108 --csv
```

日期采用 `YYYYMMDD`，证券代码带交易所后缀。示例代码仅说明输入格式。查询范围、历史覆盖、配额和使用条件以账户权限为准。价格保留服务返回口径，示例没有计算复权价格。

默认只打印结果；`--csv` 将结果写入运行目录下的 `outputs/sdk-examples/`，可通过 `--output-dir` 更改。重复使用同一输出目录会覆盖同名结果。

可选图表需要先安装 `matplotlib`：

```console
python -m pip install matplotlib
python examples/sdk/valuation_alignment.py --demo --csv --plot
```

## 验证与反馈

```console
python -m pip install pytest
python -m pytest tests/test_sdk_examples.py -q
```

测试覆盖重复键、日期范围、缺失值、负 PE、合成演示和异常信息脱敏。离线测试不代表真实账户已经获得接口权限。遇到问题请查看 [支持说明](SUPPORT.md)；不要在 Issue、代码或截图中公开 Token。

示例与对应离线测试的代码采用 MIT 许可，见 [示例许可证](examples/sdk/LICENSE)。数据和服务使用条件另行适用。
