#!/usr/bin/env python3
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
"""This package contains the business logic for the checkers.

The typical sequence of events is

.. uml::

    actor User
    participant Fetcher
    participant Parser
    participant Summarizer

    User -> Fetcher : fetch()
    Fetcher --> Fetcher : I/O
    Fetcher -> Parser : parse(RawData)
    Parser --> Parser : parse data
    Parser --> Parser : cache data
    Parser -> Summarizer : summarize(HostSections)
    Summarizer --> User : ServiceCheckResult

See Also:
    cmk.fetchers for the fetchers.
    cmk.base.sources: The entry point into the core helpers from base.

"""

from . import checking, inventory
from ._api import (
    DiscoveryPlugin,
    FetcherFunction,
    HostLabel,
    HostLabelDiscoveryPlugin,
    InventoryPlugin,
    Parameters,
    parse_raw_data,
    ParserFunction,
    PCheckPlugin,
    PInventoryResult,
    PluginSuppliedLabel,
    PSectionPlugin,
    Source,
    SummarizerFunction,
)
from ._markers import PiggybackMarker, SectionMarker
from ._parser import Parser
from ._parseragent import AgentParser
from ._parsersnmp import SNMPParser
from ._typedefs import HostKey, SourceInfo, SourceType
from .summarize import summarize

__all__ = [
    "AgentParser",
    "checking",
    "FetcherFunction",
    "HostKey",
    "HostLabel",
    "inventory",
    "Parameters",
    "parse_raw_data",
    "Parser",
    "ParserFunction",
    "PCheckPlugin",
    "DiscoveryPlugin",
    "HostLabelDiscoveryPlugin",
    "PiggybackMarker",
    "InventoryPlugin",
    "PInventoryResult",
    "PluginSuppliedLabel",
    "PSectionPlugin",
    "SectionMarker",
    "SNMPParser",
    "SourceInfo",
    "SourceType",
    "summarize",
    "SummarizerFunction",
]
