from __future__ import annotations

from sys import stderr


__all__ = ['CompilerMessage', 'ParseError', 'Source', 'SourceLocation']


class CompilerMessage(Exception):
    def display(self):
        raise NotImplementedError()


class ParseError(CompilerMessage):
    def __init__(self, message: str, location: SourceLocation):
        self.message = message
        self.location = location

    def display(self):
        print(self.message, file=stderr)
        print(self.location.in_context(), file=stderr)

    def __str__(self):
        return self.message + "\n" + self.location.in_context()


class Source:
    def __init__(self, text: str):
        self.text = text
        self.size = len(self.text)
        self.lines: dict[int, str] = {0: ""}
        recent = 0
        for index, char in enumerate(self.text):
            if char == "\n":
                self.lines[index] = ""
                recent = index
            else:
                self.lines[recent] += char

    def get_index_line(self, index: int) -> tuple[int, int, str]:
        for line_no, (start, line) in enumerate(self.lines.items()):
            if start <= index < start + len(line):
                return line_no+1, start, line
        else:
            raise ValueError()


class SourceLocation:
    def __init__(self, index: int, length: int, source: Source):
        self.index = index
        self.length = length
        self.source = source

    def combine(self, other: SourceLocation) -> SourceLocation:
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
        caret_len = min(self.length, len(line)-line_start)
        ctxt += f"{' '*line_no_size}   {' '*line_start}{'^'*caret_len}"
        if caret_len < self.length:
            ctxt += ">"
        ctxt += "\n"
        return ctxt