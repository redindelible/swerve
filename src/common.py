from __future__ import annotations

from enum import Enum
from textwrap import indent
from pathlib import Path
from contextlib import contextmanager

from typing import IO, Generic, TypeVar, NamedTuple
from collections.abc import MutableSequence, Iterable

__all__ = ['CompilerMessage', 'ErrorType', 'Source', 'Location', 'BuiltinLocation', 'SourceLocation', 'CommandLineLocation',
           'Path', 'ValueStack', 'NamedTuple', 'UniqueList']


T = TypeVar('T')


class ValueStack(Generic[T]):
    def __init__(self, initial: T = None):
        if initial is not None:
            self._stack: list[T] = [initial]
        else:
            self._stack: list[T] = []

    @contextmanager
    def using(self, value: T) -> T:
        self._stack.append(value)
        yield value
        self._stack.pop()

    def push(self, value: T):
        self._stack.append(value)

    def pop(self) -> T:
        return self._stack.pop()

    @property
    def recent(self) -> T:
        return self._stack[-1]

    @property
    def all(self) -> list[T]:
        return self._stack


class UniqueList(MutableSequence[T], Generic[T]):
    def __init__(self, items: Iterable[T]):
        self._items = list(items)
        self._remove_dups()

    def insert(self, index: int, value: T):
        if value not in self._items:
            self._items.insert(index, value)

    def __getitem__(self, item: int) -> T:
        return self._items[item]

    def __setitem__(self, key: int, value: T):
        if value in self._items:
            del self._items[key]
        else:
            self._items[key] = value

    def __delitem__(self, key: int):
        del self._items[key]

    def __len__(self):
        return len(self._items)

    def _remove_dups(self):
        items = []
        for item in self._items:
            if item not in items:
                items.append(item)
        self._items = items


class ErrorType(Enum):
    PARSE = "Parsing Error"
    COMPILATION = "Compilation Error"
    NOTE = "Note"


class CompilerMessage(Exception):
    def __init__(self, error_type: ErrorType, message: str, location: Location | None = None, notes: list[CompilerMessage] = None):
        self.error_type: ErrorType = error_type
        self.message: str = message
        self.location: Location | None = location
        self.notes: list[CompilerMessage] = [] if notes is None else notes

    def display(self, stream: IO):
        print(str(self), file=stream)

    def __str__(self) -> str:
        s = f"{self.error_type.value}: {self.message}"
        if self.location is not None:
            s += "\n"
            s += self.location.in_context()
        for note in self.notes:
            s += "\n"
            s += indent(str(note), ' | ')
        return s


class Source:
    def __init__(self, path: Path, text: str):
        self.path = path
        self.text = text
        self.size = len(self.text)
        self.lines: dict[int, str] = {0: ""}
        recent = 0
        for index, char in enumerate(self.text):
            if char == "\n":
                self.lines[index+1] = ""
                recent = index+1
            else:
                self.lines[recent] += char

    def get_index_line(self, index: int) -> tuple[int, int, str]:
        for line_no, (start, line) in enumerate(self.lines.items()):
            if start <= index <= start + len(line):
                return line_no+1, start, line
        else:
            raise ValueError()


class Location:
    def in_context(self) -> str:
        raise NotImplementedError()

    def short_context(self) -> str:
        raise NotImplementedError()


class BuiltinLocation(Location):
    def in_context(self) -> str:
        return "(builtin definition)"

    def short_context(self) -> str:
        return "as a builtin"


class CommandLineLocation(Location):
    def in_context(self) -> str:
        return "(in command line invocation)"

    def short_context(self) -> str:
        return "from the command line"


class SourceLocation(Location):
    def __init__(self, index: int, length: int, source: Source):
        self.index = index
        self.length = length
        self.source = source

    def combine(self, other: Location) -> SourceLocation:
        if not isinstance(other, SourceLocation):
            raise ValueError()
        if self.source == other.source:
            this_end = self.index + self.length
            other_end = other.index + other.length
            start = min(self.index, other.index)
            length = max(this_end, other_end) - start
            return SourceLocation(start, length, self.source)
        else:
            raise ValueError()

    def in_context(self) -> str:
        line_no, line_start, line = self.source.get_index_line(self.index)
        line_pos = self.index - line_start
        ctxt = f"{line_no:> 4}"
        line_no_size = len(ctxt)
        ctxt += f" | {line}\n"
        caret_len = max(min(self.length, len(line)-line_pos), 1)
        ctxt += f"{' '*line_no_size}   {' '*line_pos}{'^'*caret_len}"
        if caret_len < self.length:
            ctxt += ">"
        return ctxt

    def short_context(self) -> str:
        line_no, line_start, line = self.source.get_index_line(self.index)
        return f"on line {line_no} of {self.source.path.name}"