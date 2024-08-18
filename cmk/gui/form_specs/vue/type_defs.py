#!/usr/bin/env python3
# Copyright (C) 2023 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from enum import Enum


class RenderMode(Enum):
    EDIT = "edit"
    READONLY = "readonly"
    BOTH = "both"


class EmptyValue:
    pass


EMPTY_VALUE = EmptyValue()
