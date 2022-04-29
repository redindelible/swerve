from __future__ import annotations

from enum import Enum
from typing import Iterator

from src.common import ParseError, Source, SourceLocation


__all__ = ['TokenType', 'Token', 'TokenStream']


class TokenType(Enum):
    PLUS = "`+`"
    MINUS = "`-`"
    STAR = "`*`"
    STAR_STAR = "`**`"
    SLASH = "`/`"
    SLASH_SLASH = "`//`"
    PLUS_EQUAL = "`+=`"
    MINUS_EQUAL = "`-=`"
    STAR_EQUAL = "`*=`"
    STAR_STAR_EQUAL = "`**=`"
    SLASH_EQUAL = "`/=`"
    SLASH_SLASH_EQUAL = "`//=`"
    LEFT_PAREN = "`(`"
    RIGHT_PAREN = "`)`"
    LEFT_BRACE = "`{`"
    RIGHT_BRACE = "`}`"
    LEFT_BRACKET = "`[`"
    RIGHT_BRACKET = "`]`"
    DOT = "`.`"
    ARROW = "`->`"
    COLON = "`:`"
    COLON_COLON = "`::`"
    EQUAL = "`=`"
    EQUAL_EQUAL = "`==`"
    SEMICOLON = "`;`"
    COMMA = "`,`"
    DEF = "`def`"
    RETURN = "`return`"
    LET = "`let`"
    VAR = "`var`"
    OR = "`or`"
    AND = "`and`"
    NOT = "`not`"
    STRUCT = "`struct`"
    IMPORT = "`import`"
    AS = "`as`"
    IDENT = "an identifier"
    BINARY = "a binary literal"
    HEX = "a hexadecimal literal"
    INTEGER = "an integer literal"
    FLOAT = "a float literal"
    STRING = "a string literal"
    EOF = "<eof>"
    ERROR = "<error>"


SIMPLE_TOKENS = {
    "(": TokenType.LEFT_PAREN,
    ")": TokenType.RIGHT_PAREN,
    "{": TokenType.LEFT_BRACE,
    "}": TokenType.RIGHT_BRACE,
    "[": TokenType.LEFT_BRACKET,
    "]": TokenType.RIGHT_BRACKET,
    ";": TokenType.SEMICOLON,
    ",": TokenType.COMMA,
    ".": TokenType.DOT,
}


KEYWORDS = {
    "def": TokenType.DEF,
    "return": TokenType.RETURN,
    "let": TokenType.LET,
    "var": TokenType.VAR,
    "or": TokenType.OR,
    "and": TokenType.AND,
    "not": TokenType.NOT,
    "struct": TokenType.STRUCT,
    "import": TokenType.IMPORT,
    "as": TokenType.AS,
}


class Token:
    def __init__(self, type: TokenType, text: str, location: SourceLocation):
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

    def is_done(self):
        return self._index >= self.source.size

    def _new_token(self):
        self._token_start = self._index
        self._token_text = ""

    def _get_token(self, type: TokenType) -> Token:
        return Token(type, self._token_text, SourceLocation(self._token_start, len(self._token_text), self.source))

    def iter_tokens(self) -> Iterator[Token]:
        while not self.is_done():
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
                elif self._next == ">":
                    self._advance(steps=2)
                    yield self._get_token(TokenType.ARROW)
                else:
                    self._advance()
                    yield self._get_token(TokenType.MINUS)
            elif self._curr == "*":
                self._new_token()
                self._advance()
                if self._curr == "=":
                    self._advance()
                    yield self._get_token(TokenType.STAR_EQUAL)
                elif self._next == "*":
                    self._advance()
                    if self._curr == "=":
                        self._advance()
                        yield self._get_token(TokenType.STAR_STAR_EQUAL)
                    else:
                        yield self._get_token(TokenType.STAR_STAR)
                else:
                    yield self._get_token(TokenType.STAR)
            elif self._curr == "/":
                self._new_token()
                self._advance()
                if self._curr == "=":
                    self._advance()
                    yield self._get_token(TokenType.SLASH_EQUAL)
                elif self._next == "/":
                    self._advance()
                    if self._curr == "=":
                        self._advance()
                        yield self._get_token(TokenType.SLASH_SLASH_EQUAL)
                    else:
                        yield self._get_token(TokenType.SLASH_SLASH)
                else:
                    yield self._get_token(TokenType.SLASH)
            elif self._curr == "=":
                self._new_token()
                if self._next == "=":
                    self._advance(steps=2)
                    yield self._get_token(TokenType.EQUAL_EQUAL)
                else:
                    self._advance()
                    yield self._get_token(TokenType.EQUAL)
            elif self._curr == ":":
                self._new_token()
                if self._next == ":":
                    self._advance(steps=2)
                    yield self._get_token(TokenType.COLON_COLON)
                else:
                    self._advance()
                    yield self._get_token(TokenType.COLON)
            elif self._curr in SIMPLE_TOKENS.keys():
                type = SIMPLE_TOKENS[self._curr]
                self._new_token()
                self._advance()
                yield self._get_token(type)
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
                tok = self._get_token(TokenType.IDENT)
                if tok.text in KEYWORDS:
                    yield Token(KEYWORDS[tok.text], tok.text, tok.location)
                else:
                    yield tok
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
        self._new_token()
        while True:
            yield self._get_token(TokenType.EOF)
