import pytest
from pathlib import Path

from src.parser import parse_program


class TestParser:
    @pytest.mark.parametrize("file_name", [
        "test_empty.sw",
        "test_all.sw",
    ])
    def test_succeed(self, file_name):
        file_path = Path(__file__).parent / file_name
        import_dirs = [Path(__file__).parent.parent.parent / "std"]
        parse_program(file_path, import_dirs)


