from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from parser import parse_program


def main():
    parser = ArgumentParser(
        prog="swc",
    )
    parser.add_argument("file", type=Path)

    arguments = parser.parse_args()

    parse_program(arguments.file)


main()