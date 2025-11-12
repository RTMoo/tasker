import os
import signal

from multiprocessing import Process

import typer

from constants import STATE_FILE
from utils import is_alive, load_state, load_yaml, run_command_loop, save_state

app = typer.Typer()


@app.command()
def up(config: str = "tasker.yaml"):
    """Запускает все задачи как отдельные процессы"""
    tasks = load_yaml(config)
    state = load_state()
    processes = []

    try:
        for task in tasks:
            p = Process(
                target=run_command_loop,
                args=(
                    task.get("name"),
                    task.get("command"),
                    task.get("interval", 0),
                    task.get("quantity"),
                ),
                daemon=False,
            )
            p.start()
            processes.append(p)

            state[task["name"]] = {
                "pid": p.pid,
                "command": task["command"],
                "status": "running",
            }

        save_state(state)
        typer.echo(f"Запущено {len(tasks)} задач.")

        for p in processes:
            p.join()

    except KeyboardInterrupt:
        for p in processes:
            if p.is_alive():
                p.kill()
        typer.echo("Все задачи остановлены.")


@app.command()
def ps():
    """Показывает список активных процессов"""
    state = load_state()
    if not state:
        typer.echo("Нет активных задач.")
        return

    typer.echo(f"{'NAME':15} {'PID':8} {'STATUS':10} COMMAND")
    typer.echo("-" * 60)

    for name, info in state.items():
        pid = info["pid"]
        status = {"running" if is_alive(pid) else "stopped": 10}
        typer.echo(f"{name:15} {pid:<8} {status} {info['command']}")


@app.command()
def stop(name: str):
    """Останавливает задачу по имени"""
    state = load_state()
    if name not in state:
        typer.echo(f"Нет задачи '{name}'")
        raise typer.Exit()

    pid = state[name]["pid"]
    try:
        os.kill(pid, signal.SIGTERM)
        state[name]["status"] = "stopped"
        save_state(state)
        typer.echo(f"Остановлена задача {name} (PID {pid})")
    except ProcessLookupError:
        typer.echo("Процесс уже завершён.")


@app.command()
def down():
    """Останавливает все процессы"""
    state = load_state()
    for name, info in state.items():
        try:
            os.kill(info["pid"], signal.SIGTERM)
            typer.echo(f"Остановлен {name} ({info['pid']})")
        except ProcessLookupError:
            typer.echo(f"{name} уже не активен.")
    STATE_FILE.unlink(missing_ok=True)
    typer.echo("Все процессы остановлены.")


if __name__ == "__main__":
    app()
