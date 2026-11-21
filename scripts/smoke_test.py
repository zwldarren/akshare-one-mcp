"""Stands in for the test suite this project does not have.

Runs in CI (release.yml, prepare-release.yml and pr.yml). It answers one
question — does the locked set of third-party packages still provide everything
``server.py`` calls into? — because a dependency bump is the only change that can
break the server without touching our own code.

The scan covers every namespace the server reaches into: ``ako.*`` and
``indicators.*`` from akshare-one, and ``ak.*`` from akshare itself. The ``ak.*``
half is not optional: on 2026-11-21 the published 0.5.0 turned out to call
``ak.tool_trade_date_hist_sina``, which akshare 1.20.45 had renamed, so
``get_time_info`` failed for anyone who installed it. Nothing caught it, because
the original scan only looked at ``ako.`` and ``indicators.``.

The references are read from the module's AST rather than by regex, so names
that appear in comments or docstrings do not count as calls and prose about a
renamed function cannot fail the check.

Only names are checked, not behaviour: calling these functions needs live market
data and a network, which does not belong in CI.
"""

from __future__ import annotations

import ast
import asyncio
import pathlib

import akshare as ak
import akshare_one as ako
from akshare_one import indicators
from fastmcp import Client

from akshare_one_mcp.server import mcp

# get_time_info resolves the trading calendar through a ``getattr`` fallback so the
# server works on both sides of the akshare 1.20.45 rename. Each group therefore
# needs at least one member present, and no single member is required.
FALLBACK_GROUPS = {
    "ak": [
        ("calendar_trade_date_hist_sina", "tool_trade_date_hist_sina"),
    ],
}

# akshare-one has no fallbacks, so every reference must resolve.
MODULES = {
    "ako": ako,
    "indicators": indicators,
    "ak": ak,
}

EXPECTED_TOOLS = {
    "get_balance_sheet",
    "get_cash_flow",
    "get_financial_metrics",
    "get_hist_data",
    "get_income_statement",
    "get_inner_trade_data",
    "get_news_data",
    "get_realtime_data",
    "get_time_info",
    "get_valuation",
}


def referenced_names() -> dict[str, set[str]]:
    """Collect, per alias, the attribute names server.py actually dereferences."""
    tree = ast.parse(pathlib.Path("src/akshare_one_mcp/server.py").read_text())
    referenced: dict[str, set[str]] = {alias: set() for alias in MODULES}
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id in referenced
        ):
            referenced[node.value.id].add(node.attr)
    return referenced


def missing_references() -> list[str]:
    missing = []
    referenced = referenced_names()
    for alias, module in MODULES.items():
        groups = FALLBACK_GROUPS.get(alias, [])
        # A group that resolves to nothing is a break, however many names it lists.
        for group in groups:
            if not any(hasattr(module, name) for name in group):
                missing.append(f"{alias}.* (none of {'/'.join(group)})")
        # Names reachable only through a group are checked as a group, above.
        grouped = {name for group in groups for name in group}
        for name in sorted(referenced[alias] - grouped):
            if not hasattr(module, name):
                missing.append(f"{alias}.{name}")
    return missing


async def registered_tools() -> set[str]:
    async with Client(mcp) as client:
        tools = await client.list_tools()
    return {tool.name for tool in tools}


def main() -> None:
    missing = missing_references()
    if missing:
        raise SystemExit(f"API mismatch: {', '.join(missing)} missing upstream")

    tools = asyncio.run(registered_tools())
    if tools != EXPECTED_TOOLS:
        missing_tools = EXPECTED_TOOLS - tools
        extra_tools = tools - EXPECTED_TOOLS
        raise SystemExit(
            f"tool set changed (missing: {sorted(missing_tools)}, "
            f"unexpected: {sorted(extra_tools)}); "
            "update EXPECTED_TOOLS and both READMEs if this is intentional"
        )
    print(f"{len(tools)} tools registered: {sorted(tools)}")


if __name__ == "__main__":
    main()
