import os
import subprocess
import time

import typer

from .utils import color_for_name


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
