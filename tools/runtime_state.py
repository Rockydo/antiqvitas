#!/usr/bin/env python3
"""Resolve disposable test-driver state onto the configured work drive."""

from __future__ import annotations

import json
from pathlib import Path


def directory(root: Path) -> Path:
    config = json.loads((root / "config/local_paths.json").read_text(encoding="utf-8-sig"))
    configured = config.get("runtime_state_dir")
    if configured:
        return Path(str(configured))
    return Path(str(config["work_drive"])) / "antiqvitas_runtime" / "state"
