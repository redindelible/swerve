from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from sys import stderr

from common import CompilerMessage
from parser import parse_program
from names import resolve_names
from infer import infer_types
from llvmgen import generate_llvm


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
    # program.pretty_print()

    try:
        program = resolve_names(program)
    except CompilerMessage as msg:
        msg.display(stderr)
        return

    try:
        infer_types(program)
    except CompilerMessage as msg:
        msg.display(stderr)
        return

    try:
        module = generate_llvm(program)
    except CompilerMessage as msg:
        msg.display(stderr)
        return

    print(module)

main()