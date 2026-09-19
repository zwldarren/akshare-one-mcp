"""Automatic fallback across akshare-one's interchangeable data sources.

Every provider of a domain projects its frame onto that domain's declared
columns (see ``akshare_one.modules.schema``), so switching source cannot change
the shape or the column names of what a tool returns. That is what makes falling
back safe here: the sources of a domain are substitutes for each other rather
than different contracts.
"""

import logging
from collections.abc import Callable, Sequence
from typing import Literal

import pandas as pd

logger = logging.getLogger(__name__)

# A ``*Source`` alias is the domain's ``source`` parameter. The matching
# ``*SOURCES`` tuple is the fallback preference order: best source first, with
# the tool's default source at the head so an unchanged call still tries that
# source first. Every name in a tuple must come from its alias, which mypy
# checks; the names must match akshare-one's own ``Literal``s.
HistoricalSource = Literal["eastmoney", "eastmoney_direct", "sina"]
RealtimeSource = Literal["eastmoney_direct", "eastmoney", "xueqiu"]
FinancialSource = Literal["sina", "eastmoney_direct"]

HISTORICAL_SOURCES: tuple[HistoricalSource, ...] = (
    "eastmoney",
    "eastmoney_direct",
    "sina",
)
REALTIME_SOURCES: tuple[RealtimeSource, ...] = (
    "eastmoney_direct",
    "eastmoney",
    "xueqiu",
)
FINANCIAL_SOURCES: tuple[FinancialSource, ...] = ("sina", "eastmoney_direct")


def source_candidates[SourceT: str](
    source: SourceT,
    order: Sequence[SourceT],
    *,
    fallback: bool,
) -> list[SourceT]:
    """Sources to try for one call, in order.

    Args:
        source: The source the caller asked for; always tried first.
        order: The domain's preference order.
        fallback: Whether the other sources of the domain may be tried.

    Returns:
        ``[source]`` when fallback is off, otherwise ``source`` followed by the
        remaining sources in ``order``.
    """
    if not fallback:
        return [source]
    return [source, *(candidate for candidate in order if candidate != source)]


def fetch_with_fallback[SourceT: str](
    *,
    domain: str,
    candidates: Sequence[SourceT],
    fetch: Callable[[SourceT], pd.DataFrame],
) -> pd.DataFrame:
    """Return the first candidate's frame that has rows.

    A source counts as failed both when it raises and when it returns an empty
    frame, and either way the next candidate is tried.

    Args:
        domain: Domain name, used in log and error messages.
        candidates: Sources to try, in preference order.
        fetch: Called with a source name; returns that source's frame.

    Returns:
        The first frame with rows. When every candidate answered with an empty
        frame, that empty frame is returned: all sources agreeing there is no
        data is an answer, not a failure.

    Raises:
        RuntimeError: If at least one candidate raised and none returned rows,
            so that an outage is never passed off as "no data".
    """
    errors: list[str] = []
    empties: list[pd.DataFrame] = []

    for position, name in enumerate(candidates):
        try:
            df = fetch(name)
        except Exception as exc:  # noqa: BLE001 - any source failure falls through
            errors.append(f"{name}: {type(exc).__name__}: {exc}")
            logger.warning("%s: source %s failed with %s", domain, name, exc)
            continue

        if not df.empty:
            if position:
                logger.info("%s: served by fallback source %s", domain, name)
            return df

        empties.append(df)
        logger.info("%s: source %s returned no rows", domain, name)

    if errors:
        raise RuntimeError(f"{domain} data unavailable: " + "; ".join(errors))
    return empties[0] if empties else pd.DataFrame()
