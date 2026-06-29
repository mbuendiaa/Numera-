import typer
from forge.commands.docs import app as docs_app

app = typer.Typer(name="forge", help="Numera Forge - internal development assistant.")
app.add_typer(docs_app, name="docs", help="Documentation commands.")

if __name__ == "__main__":
    app()
