"""Query and validate one stock's daily history, or run a synthetic offline demo."""

import sys
from typing import Optional, Sequence

try:
    from .common import ExampleError, build_parser, describe_table, fetch_tables, query_from_args, save_csv, show_source, validate_table
except ImportError:
    from common import ExampleError, build_parser, describe_table, fetch_tables, query_from_args, save_csv, show_source, validate_table


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser("Read and validate one stock's daily data. --demo is entirely synthetic and offline.").parse_args(argv)
    try:
        query = query_from_args(args)
        raw = fetch_tables(query, include_basic=False, demo=args.demo)["daily"]
        checked = validate_table(raw, query, "daily", ["close"])
        show_source(args.demo, query)
        describe_table("daily", raw, checked)
        print(checked.head(5).to_string(index=False))
        print("Prices are returned service values. This example does not compute adjusted prices or infer missing trading days.")
        if args.csv:
            print("CSV: " + str(save_csv(checked, args.output_dir, "daily_history", args.demo)))
        return 0
    except ExampleError as error:
        print("Error: " + str(error), file=sys.stderr)
        return 2
    except Exception:
        print("Error: the local example could not finish. Check dependencies and configuration; raw error details are hidden to protect credentials.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
