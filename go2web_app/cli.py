import argparse
from typing import Optional

from .commands import run_search_mode, run_url_mode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="go2web",
        description="HTTP-over-sockets CLI fetcher and search tool",
    )

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("-u", "--url", help="Make an HTTP request to the specified URL")
    mode.add_argument(
        "-s",
        "--search",
        nargs=argparse.REMAINDER,
        help="Search the term using DuckDuckGo and print top 10 results",
    )

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.url:
        return run_url_mode(args.url)

    return run_search_mode(args.search or [])
