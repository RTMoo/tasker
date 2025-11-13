import json
import os
import subprocess
import time

import psutil
import typer
import yaml

from constants import STATE_FILE, COLORS


def load_yaml(file="tasker.yaml"):
    with open(file, "r") as f:
        return yaml.safe_load(f)["tasks"]


def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}


def save_state(state: dict):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def is_alive(pid: int) -> bool:
    return psutil.pid_exists(pid)


def color_for_name(name: str) -> str:
    return COLORS[hash(name) % len(COLORS)]


def run_command_loop(
    name: str,
    command: str,
    interval: float,
    quantity: int = 0,
    log=False,
):
    color = color_for_name(name)
    typer.secho(f"[{name}] started with PID {os.getpid()}", fg=color, bold=True)
    if quantity > 0:
        for i in range(quantity):
            proc = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, stderr = proc.communicate()
            if log:
                if stdout:
                    typer.secho(f"[{name}] {stdout.decode().strip()}", fg=color)
                else:
                    typer.secho(f"[{name}] {stderr.decode().strip()}", fg=color)
            if i < quantity - 1:
                time.sleep(interval)
    else:
        while True:
            proc = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, stderr = proc.communicate()
            if log:
                if stdout:
                    typer.secho(f"[{name}] {stdout.decode().strip()}", fg=color)
                else:
                    typer.secho(f"[{name}] {stderr.decode().strip()}", fg=color)
            time.sleep(interval)
