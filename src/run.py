from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from parser import parse_program
from common import CompilerMessage


def main():
    parser = ArgumentParser(
        prog="swc",
    )
    parser.add_argument("file", type=Path)

    arguments = parser.parse_args()

    try:
        program = parse_program(arguments.file)
    except CompilerMessage as msg:
        msg.display()
    else:
        program.pretty_print()


main()