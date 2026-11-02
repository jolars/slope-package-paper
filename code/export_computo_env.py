"""Expose the pinned render tools to Computo's subsequent workflow steps."""

import os
import shutil
from pathlib import Path


def executable(name: str) -> Path:
    """Keep wrapper paths intact so R and Python retain their Nix libraries."""
    path = shutil.which(name)
    if path is None:
        raise RuntimeError(f"The render environment is missing {name}.")
    return Path(path).absolute()


def single_line(value: str) -> str:
    if "\n" in value or "\r" in value:
        raise ValueError("GitHub environment values must occupy one line.")
    return value


def main() -> None:
    environment_file = Path(os.environ["GITHUB_ENV"])
    path_file = Path(os.environ["GITHUB_PATH"])

    tools = {
        name: executable(name)
        for name in (
            "Rscript",
            "python",
            "slope-example",
            "cmake",
            "latex",
            "latexmk",
            "lualatex",
            "xelatex",
            "dvipng",
            "pdfcrop",
            "gs",
            "pdftocairo",
            "pdftoppm",
            "rsvg-convert",
        )
    }
    julia = os.environ.get("QUARTO_JULIA") or str(executable("julia"))
    if not Path(julia).is_absolute() or not os.access(julia, os.X_OK):
        raise RuntimeError("QUARTO_JULIA must name an executable absolute path.")

    environment = {
        "QUARTO_R": str(tools["Rscript"].parent),
        "QUARTO_PYTHON": str(tools["python"]),
        "QUARTO_JULIA": julia,
        "SLOPE_CPP_EXAMPLE": str(tools["slope-example"]),
        "PYTHONHASHSEED": "0",
        "MPLBACKEND": "Agg",
        "GKSwstype": "100",
    }
    lines = [f"{key}={single_line(value)}\n" for key, value in environment.items()]
    paths = list(
        dict.fromkeys(single_line(str(tool.parent)) for tool in tools.values())
    )

    # Exporting only these tools leaves Computo's Quarto and Julia in control.
    with environment_file.open("a", encoding="utf-8") as stream:
        stream.writelines(lines)
    with path_file.open("a", encoding="utf-8") as stream:
        stream.writelines(f"{path}\n" for path in paths)


if __name__ == "__main__":
    main()
