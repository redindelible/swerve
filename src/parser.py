from __future__ import annotations

from typing import Iterator

from src.ast import *
from src.common import ParseError, SourceLocation
from src.token import Token, TokenStream, TokenType


class ParseState:
    def __init__(self, tokens: TokenStream):
        self.source = tokens.source
        self.tokens = tokens
        self.stream: Iterator[Token] = tokens.iter_tokens()

        self._curr_token = next(self.stream)
        self._last_token = self._curr_token
        self._next_token = next(self.stream)
        self._tried_match: list[TokenType] = []
        self._start_location: list[SourceLocation] = []

    @property
    def curr(self) -> Token:
        return self._curr_token

    @property
    def next(self) -> Token:
        return self._next_token

    def advance(self) -> Token:
        ret = self.curr
        self._last_token = self._curr_token
        self._curr_token = self._next_token
        self._next_token = next(self.stream)
        self._tried_match = []
        return ret

    def match(self, type: TokenType) -> bool:
        if self.curr.type == type:
            return True
        else:
            self._tried_match.append(type)
            return False

    def expect(self, type: TokenType) -> Token:
        if self.curr.type == type:
            return self.advance()
        else:
            self._tried_match.append(type)
            if len(self._tried_match) == 1:
                raise ParseError(f"Expected {self._tried_match[0].value}, got {self.curr.type}", self.curr.location)
            elif len(self._tried_match) == 2:
                raise ParseError(f"Expected {self._tried_match[0].value} or {self._tried_match[1].value}, got {self.curr.type}", self.curr.location)
            else:
                raise ParseError(f"Expected any of {', '.join(tried.value for tried in self._tried_match)}, got {self.curr.type}", self.curr.location)

    def push_loc(self):
        self._start_location.append(self._curr_token.location)

    def pop_loc(self) -> SourceLocation:
        return self._last_token.location.combine(self._start_location.pop())

    def parse(self) -> ASTFile:
        top_levels = []
        while not self.tokens.is_done():
            top_levels.append(self.parse_top_level())
        return ASTFile(self.source.name, top_levels)

    def parse_top_level(self) -> ASTTopLevel:
        if self.match(TokenType.DEF):
            return self.parse_function()
        elif self.match(TokenType.STRUCT):
            return self.parse_struct()
        else:
            raise ParseError(f"Expected a function or a struct, got {self.curr.type}", self.curr.location)

    def parse_function(self) -> ASTFunction:
        self.push_loc()
        def_token = self.expect(TokenType.DEF)
        name = self.expect(TokenType.IDENT)

        parameters: list[ASTParameter] = []
        self.expect(TokenType.LEFT_PAREN)
        while not self.match(TokenType.RIGHT_PAREN):
            self.push_loc()
            param_name = self.expect(TokenType.IDENT)
            self.expect(TokenType.COLON)
            param_type = self.parse_type()
            parameter = ASTParameter(param_name.text, param_type, self.pop_loc())
            parameters.append(parameter)
            if self.match(TokenType.COMMA):
                self.advance()
            else:
                break
        self.expect(TokenType.RIGHT_PAREN)

        self.expect(TokenType.ARROW)
        ret_type = self.parse_type()

        body = self.parse_block()
        return ASTFunction(def_token, name, parameters, ret_type, body, self.pop_loc())

    def parse_struct(self) -> ASTStruct:
        start = self.expect(TokenType.STRUCT)
        name = self.expect(TokenType.IDENT)

        type_variables = []
        if self.match(TokenType.LEFT_BRACKET):
            self.expect(TokenType.LEFT_BRACKET)
            while not self.match(TokenType.RIGHT_BRACKET):
                type_variables.append(self.parse_type_variable())
                if self.match(TokenType.COMMA):
                    self.advance()
                else:
                    break
            self.expect(TokenType.RIGHT_BRACKET)

        supertraits = []
        if self.match(TokenType.COLON):
            self.expect(TokenType.COLON)
            while not self.match(TokenType.LEFT_BRACE):
                supertraits.append(self.parse_type())
                if self.match(TokenType.COMMA):
                    self.advance()
                else:
                    break

        methods: list[ASTMethod] = []
        fields: list[ASTStructField] = []
        self.expect(TokenType.LEFT_BRACE)
        while not self.match(TokenType.RIGHT_BRACE):
            if self.match(TokenType.DEF):
                methods.append(self.parse_method())
            else:
                fields.append(self.parse_struct_field())
        end = self.expect(TokenType.RIGHT_BRACE)
        return ASTStruct(name, type_variables, supertraits, fields, methods, start.location.combine(end.location))

    def parse_struct_field(self) -> ASTStructField:
        self.push_loc()
        name = self.expect(TokenType.IDENT)
        self.expect(TokenType.COLON)
        type = self.parse_type()
        return ASTStructField(name, type, self.pop_loc())

    def parse_method(self) -> ASTMethod:
        self.push_loc()
        start = self.expect(TokenType.DEF)

        if self.match(TokenType.COLON_COLON):
            self.expect(TokenType.COLON_COLON)
            is_static = True
        else:
            is_static = False

        name = self.expect(TokenType.IDENT)

        parameters: list[ASTParameter] = []
        self_name: Token | None = None
        self.expect(TokenType.LEFT_PAREN)
        while not self.match(TokenType.RIGHT_PAREN):
            self.push_loc()
            param_name = self.expect(TokenType.IDENT)
            if not self.match(TokenType.COLON) and len(parameters) == 0:
                self_name = param_name
                self.pop_loc()
            else:
                self.expect(TokenType.COLON)
                param_type = self.parse_type()
                parameter = ASTParameter(param_name.text, param_type, self.pop_loc())
                parameters.append(parameter)
            if self.match(TokenType.COMMA):
                self.advance()
            else:
                break
        self.expect(TokenType.RIGHT_PAREN)

        self.expect(TokenType.ARROW)
        ret_type = self.parse_type()

        body = self.parse_block()
        return ASTMethod(start, name, parameters, is_static, self_name, ret_type, body, self.pop_loc())

    def parse_type_variable(self) -> ASTTypeVariable:
        self.push_loc()
        name = self.expect(TokenType.IDENT)
        if self.match(TokenType.COLON):
            self.expect(TokenType.COLON)
            bound = self.parse_type()
        else:
            bound = None
        return ASTTypeVariable(name.text, bound, self.pop_loc())

    def parse_stmt(self) -> ASTStmt:
        if self.match(TokenType.VAR) or self.match(TokenType.LET):
            stmt = self.parse_decl_stmt()
        else:
            stmt = ASTExprStmt(self.parse_expr())
        return stmt

    def parse_decl_stmt(self) -> ASTStmt:
        self.push_loc()
        if self.match(TokenType.VAR):
            is_var = True
            token = self.expect(TokenType.VAR)
        else:
            is_var = False
            token = self.expect(TokenType.LET)
        name = self.expect(TokenType.IDENT)
        self.expect(TokenType.COLON)
        if not self.match(TokenType.EQUAL):
            type = self.parse_type()
        else:
            type = None
        self.expect(TokenType.EQUAL)
        init = self.parse_expr()
        if is_var:
            return ASTVarStmt(token, name, type, init, self.pop_loc())
        else:
            return ASTLetStmt(token, name, type, init, self.pop_loc())

    def parse_expr(self) -> ASTExpr:
        return self.parse_precedence_1()

    def parse_precedence_1(self) -> ASTExpr:
        if self.match(TokenType.RETURN):
            self.push_loc()
            ret_token = self.expect(TokenType.RETURN)
            expr = self.parse_expr()
            return ASTReturnExpr(expr, self.pop_loc())
        elif self.match(TokenType.LEFT_BRACE):
            return self.parse_block()
        else:
            return self.parse_precedence_2()

    def parse_block(self) -> ASTBlockExpr:
        self.push_loc()
        self.expect(TokenType.LEFT_BRACE)
        stmts: list[ASTStmt] = []
        while not self.match(TokenType.RIGHT_BRACE):
            stmt = self.parse_stmt()
            stmts.append(stmt)
        self.expect(TokenType.RIGHT_BRACE)
        return ASTBlockExpr(stmts, self.pop_loc())

    def parse_precedence_2(self) -> ASTExpr:
        self.push_loc()
        left = self.parse_precedence_3()
        if self.match(TokenType.EQUAL):
            if isinstance(left, ASTIdentExpr):
                self.expect(TokenType.EQUAL)
                right = self.parse_precedence_2()
                return ASTAssign(left, right, self.pop_loc())
            else:
                raise ParseError("Can only assign to identifiers", left.location)
        else:
            return left

    def parse_precedence_3(self) -> ASTExpr:
        self.push_loc()
        left = self.parse_precedence_4()
        while self.match(TokenType.OR):
            self.expect(TokenType.OR)
            right = self.parse_precedence_4()
            left = ASTOrExpr(left, right, self.pop_loc())
        return left

    def parse_precedence_4(self) -> ASTExpr:
        self.push_loc()
        left = self.parse_precedence_5()
        while self.match(TokenType.AND):
            self.expect(TokenType.AND)
            right = self.parse_precedence_5()
            left = ASTAndExpr(left, right, self.pop_loc())
        return left

    def parse_precedence_5(self) -> ASTExpr:
        self.push_loc()
        left = self.parse_precedence_6()
        while True:
            if self.match(TokenType.PLUS):
                self.expect(TokenType.PLUS)
                right = self.parse_precedence_6()
                left = ASTAddExpr(left, right, self.pop_loc())
            elif self.match(TokenType.MINUS):
                self.expect(TokenType.MINUS)
                right = self.parse_precedence_6()
                left = ASTSubExpr(left, right, self.pop_loc())
            else:
                self.pop_loc()
                break
        return left

    def parse_precedence_6(self) -> ASTExpr:
        self.push_loc()
        left = self.parse_precedence_7()
        while True:
            if self.match(TokenType.STAR):
                self.expect(TokenType.STAR)
                right = self.parse_precedence_7()
                left = ASTMulExpr(left, right, self.pop_loc())
            elif self.match(TokenType.SLASH):
                self.expect(TokenType.SLASH)
                right = self.parse_precedence_7()
                left = ASTDivExpr(left, right, self.pop_loc())
            else:
                self.pop_loc()
                break
        return left

    def parse_precedence_7(self) -> ASTExpr:
        self.push_loc()
        left = self.parse_precedence_8()
        if self.match(TokenType.STAR_STAR):
            self.expect(TokenType.STAR_STAR)
            right = self.parse_precedence_7()
            return ASTPowExpr(left, right, self.pop_loc())
        else:
            self.pop_loc()
            return left

    def parse_precedence_8(self) -> ASTExpr:
        self.push_loc()
        if self.match(TokenType.MINUS):
            token = self.expect(TokenType.MINUS)
            right = self.parse_precedence_8()
            return ASTNegExpr(token, right, self.pop_loc())
        elif self.match(TokenType.NOT):
            token = self.expect(TokenType.NOT)
            right = self.parse_precedence_8()
            return ASTNotExpr(token, right, self.pop_loc())
        else:
            self.pop_loc()
            return self.parse_precedence_9()

    def parse_precedence_9(self) -> ASTExpr:
        self.push_loc()
        left = self.parse_precedence_10()
        while True:
            if self.match(TokenType.LEFT_PAREN):
                arguments: list[ASTExpr] = []
                self.expect(TokenType.LEFT_PAREN)
                while not self.match(TokenType.RIGHT_PAREN):
                    argument = self.parse_expr()
                    arguments.append(argument)
                    if self.match(TokenType.COMMA):
                        self.expect(TokenType.COMMA)
                    else:
                        break
                end = self.expect(TokenType.RIGHT_PAREN)
                left = ASTCallExpr(left, arguments, end, self.pop_loc())
            elif self.match(TokenType.DOT):
                self.expect(TokenType.DOT)
                attr = self.expect(TokenType.IDENT)
                left = ASTAttrExpr(left, attr, self.pop_loc())
            else:
                self.pop_loc()
                break
        return left

    def parse_precedence_10(self) -> ASTExpr:
        if self.match(TokenType.LEFT_PAREN):
            self.push_loc()
            self.expect(TokenType.LEFT_PAREN)
            expr = self.parse_expr()
            self.expect(TokenType.RIGHT_PAREN)
            return ASTGroupExpr(expr, self.pop_loc())
        elif self.match(TokenType.BINARY) or self.match(TokenType.HEX) or self.match(TokenType.INTEGER):
            number = self.advance()
            return ASTIntegerExpr(number)
        elif self.match(TokenType.STRING):
            return ASTStringExpr(self.expect(TokenType.STRING))
        else:
            return ASTIdentExpr(self.expect(TokenType.IDENT))

    def parse_type(self) -> ASTType:
        name = self.expect(TokenType.IDENT)
        return ASTTypeIdent(name)

