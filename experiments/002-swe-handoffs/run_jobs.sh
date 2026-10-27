#!/bin/sh
# SPDX-License-Identifier: Apache-2.0
# One destination run: AGENT INSTANCE CONDITION.
cd "$(dirname "$0")"
uv run --no-project python swe.py run "$1" "$2" "$3" >> runs.log 2>&1
