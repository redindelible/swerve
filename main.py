from __future__ import annotations

from enum import Enum
from typing import Iterator
from sys import stderr


class CompilerMessage(Exception):
    def display(self):
        raise NotImplementedError()


class ParseError(CompilerMessage):
    def __init__(self, message: str, location: Location):
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


class Location:
    def __init__(self, index: int, length: int, source: Source):
        self.index = index
        self.length = length
        self.source = source

    def in_context(self) -> str:
        line_no, line_start, line = self.source.get_index_line(self.index)
        line_pos = self.index - line_start
        ctxt = f"{line_no:> 4}"
        line_no_size = len(ctxt)
        ctxt += " | {line}\n"
        ctxt += f"{' '*line_no_size}   {' '*line_start}{'^'*self.length}\n"
        return ctxt


class TokenType(Enum):
    PLUS = "`+`"
    MINUS = "`-`"
    PLUS_EQUAL = "`+=`"
    MINUS_EQUAL = "`-=`"
    IDENT = "an identifier"
    DEF = "`def`"
    RETURN = "`return`"
    BINARY = "a binary literal"
    HEX = "a hexadecimal literal"
    INTEGER = "an integer literal"
    FLOAT = "a float literal"
    STRING = "a string literal"
    ERROR = "<error>"


class Token:
    def __init__(self, type: TokenType, text: str, location: Location):
        self.type = type
        self.text = text
        self.location = location


class TokenStream:
    def __init__(self, source: Source):
        self.source = source
        self._index = 0

        self._token_start = 0
        self._token_text = ""

    @property
    def _curr(self) -> str:
        if self._index >= self.source.size:
            return '\0'
        else:
            return self.source.text[self._index]

    @property
    def _next(self) -> str:
        if self._index+1 >= self.source.size:
            return '\0'
        else:
            return self.source.text[self._index+1]

    @property
    def _last(self) -> str:
        if self._index-1 < 0:
            return '\0'
        else:
            return self.source.text[self._index-1]

    def _advance(self, steps: int = 1):
        for _ in range(steps):
            self._token_text += self._curr
            self._index += 1

    def _is_done(self):
        return self._index >= self.source.size

    def _new_token(self):
        self._token_start = self._index
        self._token_text = ""

    def _get_token(self, type: TokenType) -> Token:
        return Token(type, self._token_text, Location(self._token_start, len(self._token_text), self.source))

    def iter_tokens(self) -> Iterator[Token]:
        while not self._is_done():
            if self._curr == "\n":
                self._advance()
            elif self._curr in " \t\r":
                self._advance()
            elif self._curr == "+":
                self._new_token()
                if self._next == "=":
                    self._advance(steps=2)
                    yield self._get_token(TokenType.PLUS_EQUAL)
                else:
                    self._advance()
                    yield self._get_token(TokenType.PLUS)
            elif self._curr == "-":
                self._new_token()
                if self._next == "=":
                    self._advance(steps=2)
                    yield self._get_token(TokenType.MINUS_EQUAL)
                else:
                    self._advance()
                    yield self._get_token(TokenType.MINUS)
            elif self._curr == "\"":
                self._new_token()
                self._advance()
                while self._curr != "\"":
                    if self._curr == "\n":
                        raise ParseError("A string literal cannot span multiple lines", self._get_token(TokenType.ERROR).location)
                    if self._curr == "\\":
                        if self._next == "\n":
                            raise ParseError("A string literal cannot span multiple lines", self._get_token(TokenType.ERROR).location)
                        self._advance()
                    self._advance()
                self._advance()
                yield self._get_token(TokenType.STRING)
            elif self._curr.isalpha() or self._curr == "_":
                self._new_token()
                while self._curr.isalpha() or self._curr.isnumeric() or self._curr == "_":
                    self._advance()
                yield self._get_token(TokenType.IDENT)
            elif self._curr.isnumeric():
                self._new_token()
                if self._curr == "0" and self._next in "bxBX":
                    self._advance(steps=2)
                    if self._last in "bB":
                        while self._curr.isnumeric():
                            if self._curr not in "01":
                                self._advance()
                                raise ParseError("Digits other than 0 and 1 are not allowed in a binary literal.",
                                                 self._get_token(TokenType.ERROR).location)
                            else:
                                self._advance()
                        yield self._get_token(TokenType.BINARY)
                    else:  # self.last in "xX"
                        while self._curr.isnumeric() or self._curr in "abcdefABCDEF":
                            self._advance()
                        yield self._get_token(TokenType.HEX)
                else:
                    self._new_token()
                    while self._curr.isnumeric():
                        self._advance()
                    if self._curr == "." and self._next.isnumeric():
                        self._advance()
                        while self._curr.isnumeric():
                            self._advance()
                        yield self._get_token(TokenType.FLOAT)
                    else:
                        yield self._get_token(TokenType.INTEGER)
            else:
                self._new_token()
                self._advance()
                raise ParseError(f"Unexpected character `{self._curr}`.", self._get_token(TokenType.ERROR).location)

