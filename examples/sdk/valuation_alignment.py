"""Strictly align one stock's daily and daily_basic observations by date."""

import sys
from typing import Optional, Sequence

try:
    from .common import ExampleError, align_tables, build_parser, describe_table, fetch_tables, query_from_args, save_csv, save_plot, show_source, validate_table
except ImportError:
    from common import ExampleError, align_tables, build_parser, describe_table, fetch_tables, query_from_args, save_csv, save_plot, show_source, validate_table


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser("Align daily and daily_basic with a one-to-one outer merge. No fill or adjusted-price calculation.", with_plot=True).parse_args(argv)
    try:
        query = query_from_args(args)
        raw = fetch_tables(query, include_basic=True, demo=args.demo)
        daily = validate_table(raw["daily"], query, "daily", ["close"])
        basic = validate_table(raw["daily_basic"], query, "daily_basic", ["pe", "pb"])
        merged = align_tables(daily, basic, query)
        show_source(args.demo, query)
        describe_table("daily", raw["daily"], daily)
        describe_table("daily_basic", raw["daily_basic"], basic)
        print("Alignment (left_only = daily only; right_only = daily_basic only):")
        print(merged["alignment"].value_counts().to_string())
        print("Missing PE: {}; missing PB: {}; negative PE: {}".format(merged["pe"].isna().sum(), merged["pb"].isna().sum(), merged["pe"].lt(0).sum()))
        print(merged.head(5).to_string(index=False))
        print("All returned dates are kept. Missing values and negative PE remain unchanged; no forward fill, calendar expansion or price adjustment.")
        if args.csv:
            print("CSV: " + str(save_csv(merged, args.output_dir, "valuation_alignment", args.demo)))
        if args.plot:
            print("PNG: " + str(save_plot(merged, args.output_dir, args.demo)))
        return 0
    except ExampleError as error:
        print("Error: " + str(error), file=sys.stderr)
        return 2
    except Exception:
        print("Error: the local example could not finish. Check dependencies and configuration; raw error details are hidden to protect credentials.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
