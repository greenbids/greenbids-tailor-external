import os
import pathlib
import fastapi_cli.cli
from greenbids.tailor.core.app import app

__all__ = ["app"]


def run():
    os.execlp("fastapi", "greenbids-tailor", "run", __file__)


if __name__ == "__main__":
    fastapi_cli.cli.dev(pathlib.Path(__file__))
