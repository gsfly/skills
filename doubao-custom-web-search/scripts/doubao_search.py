#!/usr/bin/env python3
"""Call the Doubao Custom web/image search API using an API key."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any
from urllib import error, request


DEFAULT_ENDPOINT = "https://open.feedcoopapi.com/search_api/web_search"
API_KEY_ENV = "DOUBAO_SEARCH_API_KEY"


class SearchError(RuntimeError):
    """Raised for local validation, transport, or API-level failures."""


def _put_if_set(target: dict[str, Any], key: str, value: Any) -> None:
    if value is not None:
        target[key] = value


def build_payload(
    query: str,
    search_type: str,
    count: int | None = None,
    *,
    need_content: bool = False,
    need_url: bool = False,
    sites: str | None = None,
    block_hosts: str | None = None,
    auth_info_level: int | None = None,
    time_range: str | None = None,
    content_formats: str | None = None,
    industry: str | None = None,
    query_rewrite: bool = False,
    image_width_min: int | None = None,
    image_height_min: int | None = None,
    image_width_max: int | None = None,
    image_height_max: int | None = None,
    image_shapes: list[str] | None = None,
) -> dict[str, Any]:
    query = query.strip()
    if not 1 <= len(query) <= 100:
        raise SearchError("Query must contain 1-100 characters")
    if search_type not in {"web", "image"}:
        raise SearchError("SearchType must be web or image")
    max_count = 50 if search_type == "web" else 5
    if count is not None and not 1 <= count <= max_count:
        raise SearchError(f"Count must be between 1 and {max_count} for {search_type} search")

    payload: dict[str, Any] = {"Query": query, "SearchType": search_type}
    _put_if_set(payload, "Count", count)
    filters: dict[str, Any] = {}
    if search_type == "web":
        if need_content:
            filters["NeedContent"] = True
        if need_url:
            filters["NeedUrl"] = True
        _put_if_set(filters, "Sites", sites)
        _put_if_set(filters, "BlockHosts", block_hosts)
        _put_if_set(filters, "AuthInfoLevel", auth_info_level)
        _put_if_set(payload, "TimeRange", time_range)
        _put_if_set(payload, "ContentFormats", content_formats)
        _put_if_set(payload, "Industry", industry)
    else:
        for key, value in (
            ("ImageWidthMin", image_width_min),
            ("ImageHeightMin", image_height_min),
            ("ImageWidthMax", image_width_max),
            ("ImageHeightMax", image_height_max),
            ("ImageShapes", image_shapes),
        ):
            _put_if_set(filters, key, value)
    if filters:
        payload["Filter"] = filters
    if query_rewrite:
        payload["QueryControl"] = {"QueryRewrite": True}
    return payload


def search(
    query: str,
    search_type: str,
    count: int | None = None,
    **options: Any,
) -> dict[str, Any]:
    api_key = os.environ.get(API_KEY_ENV, "").strip()
    if not api_key:
        raise SearchError(f"Set {API_KEY_ENV} before searching")
    endpoint = options.pop("endpoint", DEFAULT_ENDPOINT)
    timeout = options.pop("timeout", 30)
    payload = build_payload(query, search_type, count, **options)
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        endpoint,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=timeout) as response:
            response_body = response.read().decode("utf-8")
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SearchError(f"HTTP {exc.code}: {detail}") from exc
    except error.URLError as exc:
        raise SearchError(f"Request failed: {exc.reason}") from exc

    try:
        result = json.loads(response_body)
    except json.JSONDecodeError as exc:
        raise SearchError("API returned invalid JSON") from exc
    metadata = result.get("ResponseMetadata") or {}
    api_error = metadata.get("Error")
    if api_error:
        code = api_error.get("Code", "unknown")
        message = api_error.get("Message", "API request failed")
        raise SearchError(f"API error {code}: {message}")
    if result.get("Result") is None:
        raise SearchError("API returned no Result")
    return result


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Search with Doubao Custom API")
    parser.add_argument("query", help="1-100 character search query")
    parser.add_argument("--type", dest="search_type", choices=("web", "image"), default="web")
    parser.add_argument("--count", type=int)
    parser.add_argument("--need-content", action="store_true")
    parser.add_argument("--need-url", action="store_true")
    parser.add_argument("--sites")
    parser.add_argument("--block-hosts")
    parser.add_argument("--auth-info-level", type=int, choices=(0, 1))
    parser.add_argument("--time-range")
    parser.add_argument("--content-formats", choices=("text", "markdown"))
    parser.add_argument("--industry", choices=("finance", "game", "gov"))
    parser.add_argument("--query-rewrite", action="store_true")
    parser.add_argument("--image-width-min", type=int)
    parser.add_argument("--image-height-min", type=int)
    parser.add_argument("--image-width-max", type=int)
    parser.add_argument("--image-height-max", type=int)
    parser.add_argument("--image-shapes", nargs="+", choices=("横长方形", "竖长方形", "方形"))
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--timeout", type=float, default=30)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = vars(_parser().parse_args(argv))
    query = args.pop("query")
    search_type = args.pop("search_type")
    count = args.pop("count")
    try:
        result = search(query, search_type, count, **args)
    except SearchError as exc:
        print(f"doubao-search: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
