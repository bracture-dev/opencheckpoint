#!/bin/sh
# SPDX-License-Identifier: Apache-2.0
# Prepare one task: reference run, interrupted source run, handoffs.
set -u
cd "$(dirname "$0")"
uv run --no-project python swe.py reference "$1" >> prep.log 2>&1
uv run --no-project python swe.py source "$1" >> prep.log 2>&1
uv run --no-project python swe.py handoffs "$1" >> prep.log 2>&1
