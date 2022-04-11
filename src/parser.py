from __future__ import annotations

from typing import Iterator

from src.common import ParseError, SourceLocation
from src.token import Token, TokenStream, TokenType


class ASTNode:
    def __init__(self, loc: SourceLocation):
        self.location = loc


class ASTProgram:
    def __init__(self, files: list[ASTFile]):
        self.files = files


class ASTFile:
    def __init__(self, top_levels: list[ASTTopLevel]):
        self.top_levels = top_levels


class ASTTopLevel(ASTNode):
    pass


class ASTFunction(ASTTopLevel):
    def __init__(self, def_token: Token, name: Token, parameters: list[ASTParameter], return_type: ASTType, body: ASTBlockExpr):
        super().__init__(def_token.location)
        self.name: str = name.text
        self.parameters = parameters
        self.return_type = return_type
        self.body = body


class ASTParameter(ASTNode):
    def __init__(self, name: Token, type: ASTType):
        super().__init__(name.location.combine(type.location))
        self.name: str = name.text
        self.type = type


class ASTStmt(ASTNode):
    pass


class ASTLetStmt(ASTStmt):
    def __init__(self, let_token: Token, name: Token, type: ASTType | None, init: ASTExpr):
        super().__init__(let_token.location.combine(init.location))
        self.name: str = name.text
        self.type = type
        self.init = init


class ASTVarStmt(ASTStmt):
    def __init__(self, var_token: Token, name: Token, type: ASTType | None, init: ASTExpr):
        super().__init__(var_token.location.combine(init.location))
        self.name: str = name.text
        self.type: ASTType = type
        self.init: ASTExpr = init


class ASTExprStmt(ASTStmt):
    def __init__(self, expr: ASTExpr):
        super().__init__(expr.location)
        self.expr: ASTExpr = expr


class ASTExpr(ASTNode):
    pass


class ASTBlockExpr(ASTExpr):
    def __init__(self, start_token: Token, end_token: Token, body: list[ASTStmt]):
        super().__init__(start_token.location.combine(end_token.location))
        self.body = body


class ASTReturnExpr(ASTExpr):
    def __init__(self, return_token: Token, expr: ASTExpr):
        super().__init__(return_token.location)
        self.expr = expr


class ASTAssign(ASTExpr):
    def __init__(self, name: ASTIdentExpr, value: ASTExpr):
        super().__init__(name.location.combine(value.location))
        self.name: str = name.ident
        self.value = value


class ASTAddExpr(ASTExpr):
    def __init__(self, left: ASTExpr, right: ASTExpr):
        super().__init__(left.location.combine(right.location))
        self.left: ASTExpr = left
        self.right: ASTExpr = right


class ASTSubExpr(ASTExpr):
    def __init__(self, left: ASTExpr, right: ASTExpr):
        super().__init__(left.location.combine(right.location))
        self.left: ASTExpr = left
        self.right: ASTExpr = right


class ASTMulExpr(ASTExpr):
    def __init__(self, left: ASTExpr, right: ASTExpr):
        super().__init__(left.location.combine(right.location))
        self.left: ASTExpr = left
        self.right: ASTExpr = right


class ASTDivExpr(ASTExpr):
    def __init__(self, left: ASTExpr, right: ASTExpr):
        super().__init__(left.location.combine(right.location))
        self.left: ASTExpr = left
        self.right: ASTExpr = right


class ASTPowExpr(ASTExpr):
    def __init__(self, left: ASTExpr, right: ASTExpr):
        super().__init__(left.location.combine(right.location))
        self.left: ASTExpr = left
        self.right: ASTExpr = right


class ASTOrExpr(ASTExpr):
    def __init__(self, left: ASTExpr, right: ASTExpr):
        super().__init__(left.location.combine(right.location))
        self.left: ASTExpr = left
        self.right: ASTExpr = right


class ASTAndExpr(ASTExpr):
    def __init__(self, left: ASTExpr, right: ASTExpr):
        super().__init__(left.location.combine(right.location))
        self.left: ASTExpr = left
        self.right: ASTExpr = right


class ASTNegExpr(ASTExpr):
    def __init__(self, token: Token, right: ASTExpr):
        super().__init__(token.location.combine(right.location))
        self.right = right


class ASTNotExpr(ASTExpr):
    def __init__(self, token: Token, right: ASTExpr):
        super().__init__(token.location.combine(right.location))
        self.right = right


class ASTCallExpr(ASTExpr):
    def __init__(self, callee: ASTExpr, arguments: list[ASTExpr], end: Token):
        super().__init__(callee.location.combine(end.location))
        self.callee = callee
        self.arguments = arguments


class ASTAttrExpr(ASTExpr):
    def __init__(self, object: ASTExpr, attr: Token):
        super().__init__(object.location.combine(attr.location))
        self.object = object
        self.attr: str = attr.text


class ASTIntegerExpr(ASTExpr):
    def __init__(self, number: Token):
        super().__init__(number.location)
        if number.type == TokenType.BINARY:
            self.number: int = int(number.text, 2)
        elif number.type == TokenType.HEX:
            self.number: int = int(number.text, 16)
        else:
            self.number: int = int(number.text, 10)


class ASTStringExpr(ASTExpr):
    def __init__(self, string: Token):
        super().__init__(string.location)
        self.string = string.text[1:-1]
        #TODO replace \ things


class ASTGroupExpr(ASTExpr):
    def __init__(self, start: Token, expr: ASTExpr, end: Token):
        super().__init__(start.location.combine(end.location))
        self.expr = expr


class ASTIdentExpr(ASTExpr):
    def __init__(self, ident: Token):
        super().__init__(ident.location)
        self.ident: str = ident.text


class ASTType(ASTNode):
    pass


class ASTTypeIdent(ASTType):
    def __init__(self, ident: Token):
        super().__init__(ident.location)
        self.ident = ident


class ParseState:
    def __init__(self, tokens: TokenStream):
        self.stream: Iterator[Token] = tokens.iter_tokens()

        self._curr_token = next(self.stream)
        self._next_token = next(self.stream)
        self._tried_match: list[TokenType] = []

    @property
    def curr(self) -> Token:
        return self._curr_token

    @property
    def next(self) -> Token:
        return self._next_token

    def advance(self) -> Token:
        ret = self.curr
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

    def parse(self):
        return self.parse_top_level()

    def parse_top_level(self):
        if self.match(TokenType.DEF):
            return self.parse_function()

    def parse_function(self) -> ASTFunction:
        def_token = self.expect(TokenType.DEF)
        name = self.expect(TokenType.IDENT)

        parameters: list[ASTParameter] = []
        self.expect(TokenType.LEFT_PAREN)
        while not self.match(TokenType.RIGHT_PAREN):
            param_name = self.expect(TokenType.IDENT)
            self.expect(TokenType.COLON)
            param_type = self.parse_type()
            parameter = ASTParameter(param_name, param_type)
            parameters.append(parameter)
            if self.match(TokenType.COMMA):
                self.advance()
            else:
                break
        self.expect(TokenType.RIGHT_PAREN)

        self.expect(TokenType.ARROW)
        ret_type = self.parse_type()

        body = self.parse_block()
        return ASTFunction(def_token, name, parameters, ret_type, body)

    def parse_stmt(self) -> ASTStmt:
        if self.match(TokenType.VAR) or self.match(TokenType.LET):
            stmt = self.parse_decl_stmt()
        else:
            stmt = ASTExprStmt(self.parse_expr())
        return stmt

    def parse_decl_stmt(self) -> ASTStmt:
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
            return ASTVarStmt(token, name, type, init)
        else:
            return ASTLetStmt(token, name, type, init)

    def parse_expr(self) -> ASTExpr:
        return self.parse_precedence_1()

    def parse_precedence_1(self) -> ASTExpr:
        if self.match(TokenType.RETURN):
            ret_token = self.expect(TokenType.RETURN)
            expr = self.parse_expr()
            return ASTReturnExpr(ret_token, expr)
        elif self.match(TokenType.LEFT_BRACE):
            return self.parse_block()
        else:
            return self.parse_precedence_2()

    def parse_block(self) -> ASTBlockExpr:
        start = self.expect(TokenType.LEFT_BRACE)
        stmts: list[ASTStmt] = []
        while not self.match(TokenType.RIGHT_BRACE):
            stmt = self.parse_stmt()
            stmts.append(stmt)
        end = self.expect(TokenType.RIGHT_BRACE)
        return ASTBlockExpr(start, end, stmts)

    def parse_precedence_2(self) -> ASTExpr:
        left = self.parse_precedence_3()
        if self.match(TokenType.EQUAL):
            if isinstance(left, ASTIdentExpr):
                self.expect(TokenType.EQUAL)
                right = self.parse_precedence_2()
                return ASTAssign(left, right)
            else:
                raise ParseError("Can only assign to identifiers", left.location)
        else:
            return left

    def parse_precedence_3(self) -> ASTExpr:
        left = self.parse_precedence_4()
        while self.match(TokenType.OR):
            self.expect(TokenType.OR)
            right = self.parse_precedence_4()
            left = ASTOrExpr(left, right)
        return left

    def parse_precedence_4(self) -> ASTExpr:
        left = self.parse_precedence_5()
        while self.match(TokenType.AND):
            self.expect(TokenType.AND)
            right = self.parse_precedence_5()
            left = ASTAndExpr(left, right)
        return left

    def parse_precedence_5(self) -> ASTExpr:
        left = self.parse_precedence_6()
        while True:
            if self.match(TokenType.PLUS):
                self.expect(TokenType.PLUS)
                right = self.parse_precedence_6()
                left = ASTAddExpr(left, right)
            elif self.match(TokenType.MINUS):
                self.expect(TokenType.MINUS)
                right = self.parse_precedence_6()
                left = ASTSubExpr(left, right)
            else:
                break
        return left

    def parse_precedence_6(self) -> ASTExpr:
        left = self.parse_precedence_7()
        while True:
            if self.match(TokenType.STAR):
                self.expect(TokenType.STAR)
                right = self.parse_precedence_7()
                left = ASTMulExpr(left, right)
            elif self.match(TokenType.SLASH):
                self.expect(TokenType.SLASH)
                right = self.parse_precedence_7()
                left = ASTDivExpr(left, right)
            else:
                break
        return left

    def parse_precedence_7(self) -> ASTExpr:
        left = self.parse_precedence_8()
        if self.match(TokenType.STAR_STAR):
            self.expect(TokenType.STAR_STAR)
            right = self.parse_precedence_7()
            return ASTPowExpr(left, right)
        else:
            return left

    def parse_precedence_8(self) -> ASTExpr:
        if self.match(TokenType.MINUS):
            token = self.expect(TokenType.MINUS)
            right = self.parse_precedence_8()
            return ASTNegExpr(token, right)
        elif self.match(TokenType.NOT):
            token = self.expect(TokenType.NOT)
            right = self.parse_precedence_8()
            return ASTNotExpr(token, right)
        else:
            return self.parse_precedence_9()

    def parse_precedence_9(self) -> ASTExpr:
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
                left = ASTCallExpr(left, arguments, end)
            elif self.match(TokenType.DOT):
                self.expect(TokenType.DOT)
                attr = self.expect(TokenType.IDENT)
                left = ASTAttrExpr(left, attr)
            else:
                break
        return left

    def parse_precedence_10(self) -> ASTExpr:
        if self.match(TokenType.LEFT_PAREN):
            start = self.expect(TokenType.LEFT_PAREN)
            expr = self.parse_expr()
            end = self.expect(TokenType.RIGHT_PAREN)
            return ASTGroupExpr(start, expr, end)
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

