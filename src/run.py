from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from sys import stderr

from common import CompilerMessage
from parser import parse_program
from names import resolve_names


def main():
    parser = ArgumentParser(
        prog="swc",
    )
    parser.add_argument("file", type=Path)
    parser.add_argument("--import", "-I", type=Path, action="append", dest="imports", default=[])

    arguments = parser.parse_args()

    import_dirs = [Path(__file__).resolve().parent.parent / "std"] + arguments.imports

    try:
        program = parse_program(arguments.file, import_dirs)
    except CompilerMessage as msg:
        msg.display(stderr)
        return
    program.pretty_print()

    try:
        resolve_names(program)
    except CompilerMessage as msg:
        msg.display(stderr)
        # raise
        return


main()