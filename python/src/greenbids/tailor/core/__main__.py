import os
import sys


def main():
    os.execlp("fastapi", "greenbids-tailor", *(sys.argv[1:] or ["dev"]), __file__)


if __name__ == "__main__":
    main()
else:
    from greenbids.tailor.core.app import app  # noqa: F401
