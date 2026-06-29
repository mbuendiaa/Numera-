from pathlib import Path
import typer


def find_project_root() -> Path:
    current = Path.cwd()
    for candidate in [current, *current.parents]:
        if (candidate / "docs").exists():
            return candidate
    raise typer.BadParameter("Could not find project root. Run inside the Numera repository.")


def docs_dir() -> Path:
    return find_project_root() / "docs"
