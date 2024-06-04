#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
"""Check_MK base specific code of the crash reporting"""

import traceback
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Literal

import cmk.utils.debug
import cmk.utils.encoding
import cmk.utils.paths
from cmk.utils import crash_reporting
from cmk.utils.agentdatatype import AgentRawData
from cmk.utils.hostaddress import HostName
from cmk.utils.piggyback import get_source_hostnames
from cmk.utils.sectionname import SectionName
from cmk.utils.servicename import ServiceName

from cmk.snmplib import SNMPBackendEnum

from cmk.checkengine.checking import CheckPluginName

CrashReportStore = crash_reporting.CrashReportStore


def create_section_crash_dump(
    *,
    operation: str,
    section_name: SectionName,
    section_content: object,
    host_name: HostName,
    rtc_package: AgentRawData | None,
) -> str:
    """Create a crash dump from an exception raised in a parse or host label function"""

    text = f"{operation.title()} of section {section_name} failed"
    try:
        crash = SectionCrashReport.from_exception(
            details={
                "section_name": str(section_name),
                "section_content": section_content,
                "host_name": host_name,
            },
            type_specific_attributes={
                "snmp_info": _read_snmp_info(host_name),
                "agent_output": (
                    _read_agent_output(host_name) if rtc_package is None else rtc_package
                ),
            },
        )
        CrashReportStore().save(crash)
        return f"{text} - please submit a crash report! (Crash-ID: {crash.ident_to_text()})"
    except Exception:
        if cmk.utils.debug.enabled():
            raise
        return f"{text} - failed to create a crash report: {traceback.format_exc()}"


def create_check_crash_dump(
    host_name: HostName,
    service_name: ServiceName,
    *,
    plugin_name: str | CheckPluginName,
    plugin_kwargs: Mapping[str, Any],
    is_cluster: bool,
    is_enforced: bool,
    snmp_backend: SNMPBackendEnum,
    rtc_package: AgentRawData | None,
) -> str:
    """Create a crash dump from an exception occured during check execution

    The crash dump is put into a tarball, base64 encoded and appended to the long output
    of the check. The GUI (cmk.gui.crash_reporting) is able to parse it and send it to
    the Checkmk team.
    """
    text = "check failed - please submit a crash report!"
    try:
        crash = CheckCrashReport.from_exception(
            details={
                "check_output": text,
                "host": host_name,
                "is_cluster": is_cluster,
                "description": service_name,
                "check_type": str(plugin_name),
                "inline_snmp": snmp_backend is SNMPBackendEnum.INLINE,
                "enforced_service": is_enforced,
                **plugin_kwargs,
            },
            type_specific_attributes={
                "snmp_info": _read_snmp_info(host_name),
                "agent_output": (
                    _read_agent_output(host_name) if rtc_package is None else rtc_package
                ),
            },
        )
        CrashReportStore().save(crash)
        text += " (Crash-ID: %s)" % crash.ident_to_text()
        return text
    except Exception:
        if cmk.utils.debug.enabled():
            raise
        return "check failed - failed to create a crash report: %s" % traceback.format_exc()


class CrashReportWithAgentOutput(crash_reporting.ABCCrashReport):
    def __init__(
        self,
        crash_info: dict,
        snmp_info: bytes | None = None,
        agent_output: bytes | None = None,
    ) -> None:
        super().__init__(crash_info)
        self.snmp_info = snmp_info
        self.agent_output = agent_output

    def _serialize_attributes(self) -> dict:
        """Serialize object type specific attributes for transport"""
        attributes = super()._serialize_attributes()

        for key, val in [
            ("snmp_info", self.snmp_info),
            ("agent_output", self.agent_output),
        ]:
            if val is not None:
                attributes[key] = val

        return attributes


@crash_reporting.crash_report_registry.register
class SectionCrashReport(CrashReportWithAgentOutput):
    @staticmethod
    def type() -> Literal["section"]:
        return "section"


@crash_reporting.crash_report_registry.register
class CheckCrashReport(CrashReportWithAgentOutput):
    @staticmethod
    def type() -> Literal["check"]:
        return "check"


def _read_snmp_info(hostname: str) -> bytes | None:
    cache_path = Path(cmk.utils.paths.snmpwalks_dir, hostname)
    try:
        with cache_path.open(mode="rb") as f:
            return f.read()
    except OSError:
        pass
    return None


def _read_agent_output(hostname: HostName) -> AgentRawData | None:
    cache_path = Path(cmk.utils.paths.tcp_cache_dir, hostname)
    piggyback_cache_path = Path(cmk.utils.paths.piggyback_dir, hostname)
    cache_paths = [cache_path] + [
        piggyback_cache_path / source_hostname for source_hostname in get_source_hostnames(hostname)
    ]
    agent_outputs = []
    for cache_path in cache_paths:
        try:
            with cache_path.open(mode="rb") as f:
                agent_outputs.append(f.read())
        except OSError:
            pass

    if agent_outputs:
        return AgentRawData(b"\n".join(agent_outputs))
    return None
