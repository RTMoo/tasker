import typer

from .manager import down_all, restart_task, show_all, stop_task, up_all

app = typer.Typer()


@app.command()
def up(f: str = "tasker.yaml", log: bool = False):
    up_all(f, log)


@app.command()
def show():
    show_all()


@app.command()
def stop(name: str):
    stop_task(name)


@app.command()
def down():
    down_all()


@app.command()
def restart(name: str):
    restart_task(name)


if __name__ == "__main__":
    app()
