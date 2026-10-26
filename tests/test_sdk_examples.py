"""Offline checks for the public SDK examples; never call a live account."""

import pandas as pd
import pytest

from examples.sdk import common, daily_history, valuation_alignment


def test_outer_alignment_preserves_unmatched_dates_nulls_and_negative_pe():
    daily, basic = common.synthetic_tables()
    result = common.align_tables(daily, basic, common.DEMO_QUERY).set_index("trade_date")
    assert list(result.index) == ["20250102", "20250103", "20250106", "20250107", "20250108"]
    assert result.loc["20250103", "alignment"] == "left_only"
    assert pd.isna(result.loc["20250103", "pe"])
    assert pd.isna(result.loc["20250107", "pe"])
    assert pd.isna(result.loc["20250107", "pb"])
    assert result.loc["20250106", "pe"] == -5.0
    assert result.loc["20250108", "alignment"] == "right_only"
    assert pd.isna(result.loc["20250108", "close"])


@pytest.mark.parametrize("which", ["daily", "daily_basic"])
def test_duplicate_observation_keys_are_rejected_before_merge(which):
    daily, basic = common.synthetic_tables()
    if which == "daily":
        daily = pd.concat([daily, daily.iloc[[0]]], ignore_index=True)
    else:
        basic = pd.concat([basic, basic.iloc[[0]]], ignore_index=True)
    with pytest.raises(common.ExampleError, match="duplicate.*keys"):
        common.align_tables(daily, basic, common.DEMO_QUERY)


@pytest.mark.parametrize("field,value,message", [
    ("ts_code", "600519.SH", "different stock"),
    ("trade_date", "20250101", "outside"),
    ("trade_date", "20250230", "invalid"),
    ("trade_date", None, "invalid"),
    ("close", "not-a-price", "non-numeric"),
    ("close", None, "present and strictly positive"),
    ("close", 0, "present and strictly positive"),
    ("close", -1.0, "present and strictly positive"),
])
def test_single_stock_response_validation(field, value, message):
    daily, _ = common.synthetic_tables()
    daily[field] = daily[field].astype(object)
    daily.loc[0, field] = value
    with pytest.raises(common.ExampleError, match=message):
        common.validate_table(daily, common.DEMO_QUERY, "daily", ["close"])


def test_daily_sort_and_empty_response_handling():
    daily, _ = common.synthetic_tables()
    checked = common.validate_table(daily, common.DEMO_QUERY, "daily", ["close"])
    assert checked["trade_date"].is_monotonic_increasing
    empty = common.align_tables(pd.DataFrame(), pd.DataFrame(), common.DEMO_QUERY)
    assert empty.empty
    assert set(["ts_code", "trade_date", "close", "pe", "pb", "alignment"]).issubset(empty.columns)


def test_daily_basic_close_is_kept_without_overwriting_daily_close():
    daily, basic = common.synthetic_tables()
    basic["close"] = 999.0
    result = common.align_tables(daily, basic, common.DEMO_QUERY).set_index("trade_date")
    assert result.loc["20250102", "close"] == 10.1
    assert result.loc["20250102", "close_basic"] == 999.0


@pytest.mark.parametrize("entrypoint", [daily_history.main, valuation_alignment.main])
def test_demo_does_not_need_credentials_or_call_requests(entrypoint, monkeypatch, capsys):
    import requests

    monkeypatch.delenv("ALPHAKIT_TOKEN", raising=False)
    monkeypatch.delenv("ALPHAKIT_BASE_URL", raising=False)

    def no_network(*args, **kwargs):
        raise AssertionError("Demo must not create any network request")

    monkeypatch.setattr(requests.sessions.Session, "request", no_network)
    monkeypatch.setattr(common, "live_client", no_network)
    assert entrypoint(["--demo"]) == 0
    captured = capsys.readouterr()
    assert "SYNTHETIC DEMO" in captured.out
    assert "NOT real market data" in captured.out
    assert not captured.err


def test_demo_csv_has_synthetic_marker(tmp_path):
    assert valuation_alignment.main(["--demo", "--csv", "--output-dir", str(tmp_path)]) == 0
    exported = pd.read_csv(tmp_path / "demo_valuation_alignment.csv")
    assert exported["data_source"].eq("synthetic-demo").all()
    assert exported["pe"].isna().sum() == 2
    assert exported["pe"].lt(0).sum() == 1


@pytest.mark.parametrize("value", [
    "", "http://gateway.invalid", "https://user:secret@gateway.invalid", "https://gateway.invalid?token=secret",
    "https://gateway.invalid#secret", "https://gateway.invalid?", "https://gateway.invalid#",
    "https://gateway.invalid\\secret", "https://gateway.invalid:bad", "https://gateway.invalid:99999",
])
def test_https_gateway_validation_does_not_echo_input(value):
    with pytest.raises(common.ExampleError) as error:
        common.validate_base_url(value)
    assert "secret" not in str(error.value)
    assert "gateway.invalid" not in str(error.value)


def test_https_gateway_base_preserves_administrator_path():
    assert common.validate_base_url("https://gateway.invalid/sdk/") == "https://gateway.invalid/sdk"


def test_live_requires_explicit_stock_and_dates(capsys):
    assert daily_history.main([]) == 2
    assert "--ts-code" in capsys.readouterr().err


def test_sdk_request_exception_does_not_leak_token_or_url(monkeypatch, capsys):
    secret = "token-that-must-never-appear"

    class FailedClient:
        def daily(self, **kwargs):
            raise RuntimeError("Bearer " + secret + " https://gateway.invalid/?token=" + secret)

    monkeypatch.setattr(common, "live_client", lambda: FailedClient())
    assert daily_history.main(["--ts-code", "000001.SZ", "--start-date", "20250102", "--end-date", "20250108"]) == 2
    captured = capsys.readouterr()
    assert "daily request failed" in captured.err
    assert secret not in captured.out + captured.err
    assert "gateway.invalid" not in captured.out + captured.err
