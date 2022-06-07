from __future__ import annotations

from common import BuiltinLocation, CompilerMessage, ErrorType, Location, Path
from llvmlite import ir
from llvmlite import binding as llvm

import subprocess
import tempfile


WINDOWS_PATH = Path(__file__).parent / "windows"
LINKER_PATH = WINDOWS_PATH / "lld-link.exe"


def emit_module(module: ir.Module, output: Path):
    target = llvm.Target.from_default_triple()
    machine = target.create_target_machine(codemodel="default")
    module.triple = target.triple
    object_code = machine.emit_object(llvm.parse_assembly(str(module)))

    lib_path = find_vs_lib_path("x64")
    if lib_path is None:
        raise CompilerMessage(ErrorType.COMPILATION, "Could not locate MSVC redistributable")
    sdk_paths = find_sdk_paths("x64")
    if sdk_paths is None:
        raise CompilerMessage(ErrorType.COMPILATION, "Could not locate Windows SDKs")
    um_path, ucrt_path = sdk_paths

    object_file = tempfile.NamedTemporaryFile(delete=False)
    object_file.write(object_code)

    result = subprocess.Popen([LINKER_PATH, object_file.name, f"/libpath:{lib_path}", f"/libpath:{um_path}", f"/libpath:{ucrt_path}", "/DEFAULTLIB:libcmt.lib", f"/out:{output}"], shell=False)


def find_vs_lib_path(platform: str) -> Path | None:
    current_path = Path(r"C:\Program Files (x86)\Microsoft Visual Studio")
    if not current_path.exists() or not current_path.is_dir():
        return None

    items = sorted((name for name in current_path.iterdir() if name.name.isnumeric()), key=lambda p: int(p.name))
    if len(items) == 0:
        return None
    current_path = items[-1] / "Community" / "VC"/ "Tools" / "MSVC"
    if not current_path.exists() or not current_path.is_dir():
        return None

    items = sorted(current_path.iterdir(), key=lambda p: tuple(p.name.split(".")))
    if len(items) == 0:
        return None
    current_path = items[-1] / "lib" / f"{platform}"
    if not current_path.exists() or not current_path.is_dir():
        return None
    return current_path


def find_sdk_paths(platform: str) -> tuple[Path, Path] | None:
    current_path = Path(r"C:\Program Files (x86)\Windows Kits\10\Lib")
    if not current_path.exists() or not current_path.is_dir():
        return None
    items = sorted(current_path.iterdir(), key=lambda p: tuple(p.name.split(".")))
    if len(items) == 0:
        return None
    current_path = items[-1] / "um" / f"{platform}"
    if not current_path.exists() or not current_path.is_dir():
        return None
    um_path = current_path
    current_path = items[-1] / "ucrt" / f"{platform}"
    if not current_path.exists() or not current_path.is_dir():
        return None
    ucrt_path = current_path
    return um_path, ucrt_path