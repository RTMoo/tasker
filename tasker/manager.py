from multiprocessing import Process

import typer

from .constants import STATE_FILE
from .utils import (
    is_alive,
    kill_process,
    load_state,
    load_yaml,
    save_state,
)
from .runners import run_command_loop


def up_all(f: str = "tasker.yaml", log: bool = False):
    """Запускает все задачи как отдельные процессы"""
    tasks = load_yaml(f)
    state = load_state()
    processes = []

    for task in tasks:
        task = state.get(task["name"])
        if task and task["status"] == "running":
            kill_process(task["pid"])
    try:
        for task in tasks:
            proc = Process(
                target=run_command_loop,
                args=(
                    task.get("name"),
                    task.get("command"),
                    task.get("interval", 0),
                    task.get("quantity", 0),
                    log,
                ),
                daemon=False,
            )
            proc.start()
            processes.append(proc)

            state[task["name"]] = {
                "pid": proc.pid,
                "command": task["command"],
                "status": "running",
            }

        save_state(state)
        typer.echo(f"Запущено {len(tasks)} задач.")

        for proc in processes:
            proc.join()

    except KeyboardInterrupt:
        for proc in processes:
            kill_process(proc.pid)
        typer.echo("Все задачи остановлены.")


def show_all():
    """Показывает список активных процессов"""
    state = load_state()
    if not state:
        typer.echo("Нет активных задач.")
        return

    typer.echo(f"{'NAME':15} {'PID':8} {'STATUS':10} COMMAND")
    typer.echo("-" * 60)

    for name, info in state.items():
        pid = info["pid"]
        status = "running" if is_alive(pid) else "stopped"
        typer.echo(f"{name:15} {pid:<8} {status:10} {info['command']}")


def stop_task(name: str):
    """Останавливает задачу по имени"""
    state = load_state()
    if name not in state:
        typer.echo(f"Нет задачи '{name}'")
        raise typer.Exit()

    pid = state[name]["pid"]
    try:
        kill_process(pid)
        state[name]["status"] = "stopped"
        save_state(state)
        typer.echo(f"Остановлена задача {name} (PID {pid})")
    except ProcessLookupError:
        typer.echo("Процесс уже завершён.")


def down_all():
    """Останавливает все процессы"""
    state = load_state()
    for name, task in state.items():
        try:
            kill_process(task["pid"])
            typer.echo(f"Остановлен {name} ({task['pid']})")
        except ProcessLookupError:
            typer.echo(f"{name} уже не активен.")
    STATE_FILE.unlink(missing_ok=True)
    typer.echo("Все процессы остановлены.")
