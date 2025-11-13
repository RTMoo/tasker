import json

from typing import Any

import psutil
import yaml

from .constants import COLORS, STATE_FILE


def load_yaml(file="tasker.yaml"):
    with open(file, "r") as f:
        return yaml.safe_load(f)["tasks"]


def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}


def save_state(state: dict[str, Any]):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def is_alive(pid: int) -> bool:
    return psutil.pid_exists(pid)


def color_for_name(name: str) -> str:
    return COLORS[hash(name) % len(COLORS)]


def kill_process(pid: int):
    try:
        proc = psutil.Process(pid)
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except psutil.TimeoutExpired:
            proc.kill()
    except psutil.NoSuchProcess:
        pass
