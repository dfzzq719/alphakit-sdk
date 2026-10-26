"""Validation and safe I/O shared by the two single-stock SDK examples."""

import argparse
from dataclasses import dataclass
from datetime import datetime
import math
import os
from pathlib import Path
import re
from typing import Dict, Sequence, Tuple
from urllib.parse import urlsplit

import pandas as pd


class ExampleError(ValueError):
    """An error message controlled by this example; safe to show on the CLI."""


@dataclass(frozen=True)
class Query:
    ts_code: str
    start_date: str
    end_date: str


DEMO_QUERY = Query("000001.SZ", "20250102", "20250108")
KEYS = ["ts_code", "trade_date"]


def date_text(value: object) -> str:
    text = str(value)
    if not re.fullmatch(r"[0-9]{8}", text):
        raise ExampleError("Dates must use YYYYMMDD, for example 20250102.")
    try:
        datetime.strptime(text, "%Y%m%d")
    except ValueError:
        raise ExampleError("A date is not a valid calendar date.") from None
    return text


def validate_query(query: Query) -> Query:
    if not re.fullmatch(r"[0-9]{6}\.(SH|SZ|BJ)", query.ts_code):
        raise ExampleError("Supply one explicit stock code, for example 000001.SZ.")
    start = date_text(query.start_date)
    end = date_text(query.end_date)
    if start > end:
        raise ExampleError("start-date must be on or before end-date.")
    return Query(query.ts_code, start, end)


def build_parser(description: str, with_plot: bool = False) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--demo", action="store_true", help="Use fixed SYNTHETIC data; no Token or network.")
    parser.add_argument("--ts-code", help="One stock code, required for a live request.")
    parser.add_argument("--start-date", help="YYYYMMDD, inclusive; required for a live request.")
    parser.add_argument("--end-date", help="YYYYMMDD, inclusive; required for a live request.")
    parser.add_argument("--csv", action="store_true", help="Save the checked result to a CSV file.")
    parser.add_argument(
        "--output-dir", type=Path, default=Path.cwd() / "outputs" / "sdk-examples",
        help="Directory for requested CSV/PNG files (default: ./outputs/sdk-examples).",
    )
    if with_plot:
        parser.add_argument("--plot", action="store_true", help="Save a PNG; requires optional matplotlib.")
    return parser


def query_from_args(args: argparse.Namespace) -> Query:
    values = (args.ts_code, args.start_date, args.end_date)
    if args.demo:
        if any(value is not None for value in values):
            raise ExampleError("--demo uses a fixed synthetic sample; omit stock/date arguments.")
        return DEMO_QUERY
    if not all(values):
        raise ExampleError("Live mode requires --ts-code, --start-date and --end-date.")
    return validate_query(Query(*values))


def validate_base_url(value: str) -> str:
    # Never include the supplied URL in an error: it could contain a pasted secret.
    message = "ALPHAKIT_BASE_URL must be the administrator-provided HTTPS gateway base URL, without credentials, query or fragment."
    if not value or any(char.isspace() or ord(char) < 32 for char in value) or any(char in value for char in "\\?#"):
        raise ExampleError(message)
    try:
        parsed = urlsplit(value)
        valid = (
            parsed.scheme.lower() == "https"
            and bool(parsed.hostname)
            and parsed.username is None
            and parsed.password is None
            and not parsed.query
            and not parsed.fragment
            and "%" not in parsed.netloc
        )
        # Access also validates a malformed/non-numeric port.
        port = parsed.port
        valid = valid and (port is None or 1 <= port <= 65535)
    except ValueError:
        valid = False
    if not valid:
        raise ExampleError(message)
    return value.rstrip("/")


def live_client():
    token = os.environ.get("ALPHAKIT_TOKEN", "").strip()
    if not token:
        raise ExampleError("Set ALPHAKIT_TOKEN in your environment, or use --demo.")
    base_url = validate_base_url(os.environ.get("ALPHAKIT_BASE_URL", ""))
    try:
        from alphakit import AlphaKit

        return AlphaKit(token=token, base_url=base_url)
    except ImportError:
        raise ExampleError("Install alphakit-sdk first, using the requirements.txt included with these examples.") from None
    except Exception:
        raise ExampleError("Could not initialize the SDK. Check your local installation and gateway configuration.") from None


def fetch_tables(query: Query, include_basic: bool, demo: bool) -> Dict[str, pd.DataFrame]:
    if demo:
        daily, basic = synthetic_tables()
        return {"daily": daily, **({"daily_basic": basic} if include_basic else {})}
    client = live_client()
    tables = {}
    for name in (["daily", "daily_basic"] if include_basic else ["daily"]):
        try:
            tables[name] = getattr(client, name)(
                ts_code=query.ts_code, start_date=query.start_date, end_date=query.end_date,
            )
        except Exception:
            # SDK/requests exceptions can contain URLs or a server response. Do not
            # display them, chain a traceback, or write them to a log.
            raise ExampleError(
                name + " request failed. Check gateway availability, dates, Token permissions and quota with the administrator."
            ) from None
    return tables


def validate_table(frame: pd.DataFrame, query: Query, name: str, numeric: Sequence[str]) -> pd.DataFrame:
    """Reject mixed stocks, invalid/out-of-range dates and duplicate observation keys."""
    query = validate_query(query)
    if not isinstance(frame, pd.DataFrame):
        raise ExampleError(name + " did not return a pandas DataFrame.")
    if frame.columns.duplicated().any():
        raise ExampleError(name + " contains duplicate field names.")
    required = KEYS + list(numeric)
    if frame.empty:
        # The SDK returns a completely column-less DataFrame for an empty response.
        return pd.DataFrame(columns=list(dict.fromkeys(required + list(frame.columns))))
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise ExampleError(name + " is missing required fields: " + ", ".join(missing) + ".")
    checked = frame.copy()
    if checked["ts_code"].isna().any() or not checked["ts_code"].eq(query.ts_code).all():
        raise ExampleError(name + " returned a different stock or an empty stock code; refusing the result.")
    try:
        checked["trade_date"] = checked["trade_date"].map(date_text)
    except ExampleError:
        raise ExampleError(name + " contains a missing or invalid YYYYMMDD trade_date.") from None
    if not checked["trade_date"].between(query.start_date, query.end_date).all():
        raise ExampleError(name + " returned a date outside the requested range; refusing the result.")
    if checked.duplicated(KEYS).any():
        raise ExampleError(name + " contains duplicate (ts_code, trade_date) keys; one-to-one alignment is unsafe.")
    for column in numeric:
        try:
            checked[column] = pd.to_numeric(checked[column], errors="raise")
            finite = checked[column].dropna().map(lambda value: math.isfinite(float(value))).all()
        except (ValueError, TypeError, OverflowError):
            finite = False
        if not finite:
            raise ExampleError(name + " contains a non-numeric or infinite value in " + column + ".")
        if name == "daily" and column == "close" and (checked[column].isna().any() or checked[column].le(0).any()):
            raise ExampleError("daily close must be present and strictly positive for every returned observation.")
    return checked.sort_values(KEYS, kind="mergesort").reset_index(drop=True)


def align_tables(daily: pd.DataFrame, basic: pd.DataFrame, query: Query) -> pd.DataFrame:
    left = validate_table(daily, query, "daily", ["close"])
    right = validate_table(basic, query, "daily_basic", ["pe", "pb"])
    if "alignment" in left.columns or "alignment" in right.columns:
        raise ExampleError("Returned fields collide with the example's alignment marker.")
    # daily_basic may also contain close. Keep the daily close for plotting and
    # retain the other table's close under close_basic, rather than overwriting it.
    if "pe" in left.columns or "pb" in left.columns:
        raise ExampleError("daily unexpectedly contains valuation fields; check the response schema before merging.")
    try:
        merged = left.merge(
            right, on=KEYS, how="outer", validate="one_to_one",
            suffixes=("", "_basic"), indicator="alignment",
        )
    except (pd.errors.MergeError, ValueError):
        raise ExampleError("The tables could not be aligned one-to-one; check their field names and keys.") from None
    return merged.sort_values(KEYS, kind="mergesort").reset_index(drop=True)


def synthetic_tables() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Invented numbers, not a historical observation of the displayed stock."""
    daily = pd.DataFrame([
        {"ts_code": DEMO_QUERY.ts_code, "trade_date": "20250106", "open": 10.2, "close": 10.4},
        {"ts_code": DEMO_QUERY.ts_code, "trade_date": "20250102", "open": 10.0, "close": 10.1},
        {"ts_code": DEMO_QUERY.ts_code, "trade_date": "20250107", "open": 10.4, "close": 10.3},
        {"ts_code": DEMO_QUERY.ts_code, "trade_date": "20250103", "open": 10.1, "close": 10.2},
    ])
    basic = pd.DataFrame([
        {"ts_code": DEMO_QUERY.ts_code, "trade_date": "20250108", "pe": 9.0, "pb": 0.90},
        {"ts_code": DEMO_QUERY.ts_code, "trade_date": "20250106", "pe": -5.0, "pb": 0.95},
        {"ts_code": DEMO_QUERY.ts_code, "trade_date": "20250102", "pe": 8.0, "pb": 0.92},
        {"ts_code": DEMO_QUERY.ts_code, "trade_date": "20250107", "pe": None, "pb": None},
    ])
    return daily, basic


def show_source(demo: bool, query: Query) -> None:
    if demo:
        print("SYNTHETIC DEMO: invented sample values, NOT real market data. No network request was made.")
    else:
        print("LIVE SDK RESPONSE: one explicit stock, subject to the account's service permissions.")
    print("Query: {} | {} to {}".format(query.ts_code, query.start_date, query.end_date))


def describe_table(name: str, raw: pd.DataFrame, checked: pd.DataFrame) -> None:
    print(name + " returned fields: " + ", ".join(str(column) for column in raw.columns))
    print("{} checked rows: {} (sorted ascending; duplicate keys rejected)".format(name, len(checked)))
    if checked.empty:
        print(name + " is empty. Check permissions, coverage, the requested period and non-trading days; no values were invented.")


def save_csv(frame: pd.DataFrame, output_dir: Path, stem: str, demo: bool) -> Path:
    exported = frame.copy()
    if "data_source" in exported.columns:
        raise ExampleError("Returned fields collide with the example's data_source marker.")
    exported.insert(0, "data_source", "synthetic-demo" if demo else "live-sdk-response")
    destination = output_dir / (("demo_" if demo else "") + stem + ".csv")
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        exported.to_csv(destination, index=False, encoding="utf-8-sig")
    except (OSError, ValueError):
        raise ExampleError("Could not write the CSV. Check --output-dir and filesystem permissions.") from None
    return destination


def save_plot(frame: pd.DataFrame, output_dir: Path, demo: bool) -> Path:
    if frame.empty:
        raise ExampleError("There are no returned dates to plot.")
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        raise ExampleError("--plot requires the optional dependency: python -m pip install matplotlib") from None
    dates = pd.to_datetime(frame["trade_date"], format="%Y%m%d")
    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    destination = output_dir / (("demo_" if demo else "") + "valuation_alignment.png")
    try:
        for axis, column, label in zip(axes, ["close", "pe", "pb"], ["Daily close: service value, no adjustment", "PE: negative and empty values retained", "PB: empty values retained"]):
            axis.plot(dates, frame[column], marker="o")
            axis.set_ylabel(column.upper())
            axis.set_title(label, loc="left", fontsize=9)
            axis.grid(alpha=0.2)
        fig.suptitle("SYNTHETIC DEMO - NOT MARKET DATA" if demo else "Single-stock daily data and valuation alignment")
        fig.autofmt_xdate()
        fig.tight_layout(rect=(0, 0, 1, 0.97))
        output_dir.mkdir(parents=True, exist_ok=True)
        fig.savefig(destination, dpi=150)
    except (OSError, ValueError):
        raise ExampleError("Could not save the chart. Check the local matplotlib installation and --output-dir.") from None
    finally:
        plt.close(fig)
    return destination
