from __future__ import annotations

from typing import Iterator
from pathlib import Path

from .swc_ast import *
from .common import CompilerMessage, ErrorType, SourceLocation, Source, CommandLineLocation, Location
from .tokens import Token, TokenStream, TokenType


def parse_program(start: Path, import_dirs: list[Path]) -> ASTProgram:
    to_visit: list[tuple[Path, Location]] = [(start.resolve(), CommandLineLocation())]
    visited: set[Path] = set()
    files = []
    while to_visit:
        next_path, loc = to_visit.pop()
        if next_path in visited:
            continue
        try:
            text = next_path.read_text()
        except Exception as err:
            raise CompilerMessage(ErrorType.PARSE, f"Could not read from file '{next_path}'", loc)
        source = Source(next_path, text)
        file = ParseState(TokenStream(source), import_dirs).parse(True if len(visited) == 0 else False)
        files.append(file)
        for top_level in file.top_levels:
            if isinstance(top_level, ASTImport):
                path = top_level.path
                to_visit.append((path.resolve(), top_level.loc))
        visited.add(next_path)
    return ASTProgram(files)


def search_dirs(dirs: list[Path], name: str) -> Path | None:
    for dir in dirs:
        if (dir / name).exists() and (dir / name).is_file():
            return dir / name
    return None


class ParseState:
    def __init__(self, tokens: TokenStream, import_dirs: list[Path]):
        self.source = tokens.source
        self.tokens = tokens
        self.stream: Iterator[Token] = tokens.iter_tokens()

        self.import_dirs = import_dirs

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

    def match(self, *types: TokenType) -> bool:
        if self.curr.type in types:
            return True
        else:
            self._tried_match.extend(types)
            return False

    def expect(self, type: TokenType) -> Token:
        if self.curr.type == type:
            return self.advance()
        else:
            self._tried_match.append(type)
            self.error()

    def error(self):
        if len(self._tried_match) == 1:
            raise CompilerMessage(ErrorType.PARSE, f"Expected {self._tried_match[0].value}, but got {self.curr.type.value} instead", self.curr.location)
        elif len(self._tried_match) == 2:
            raise CompilerMessage(ErrorType.PARSE, f"Expected {self._tried_match[0].value} or {self._tried_match[1].value}, but got {self.curr.type.value} instead", self.curr.location)
        else:
            raise CompilerMessage(ErrorType.PARSE, f"Expected any of {', '.join(tried.value for tried in self._tried_match[:-1])}, or {self._tried_match[-1].value}, but got {self.curr.type.value} instead", self.curr.location)

    def push_loc(self):
        self._start_location.append(self._curr_token.location)

    def pop_loc(self) -> SourceLocation:
        return self._last_token.location.combine(self._start_location.pop())

    def parse(self, is_main: bool) -> ASTFile:
        top_levels = []
        while self.curr.type != TokenType.EOF:
            if self.match(TokenType.IMPORT):
                top_levels.extend(self.parse_import())
            elif self.match(TokenType.FN) or self.match(TokenType.EXTERN):
                top_levels.append(self.parse_function())
            elif self.match(TokenType.TRAIT):
                top_levels.append(self.parse_trait())
            else:
                top_levels.append(self.parse_struct())
        return ASTFile(self.source.path, top_levels, is_main)

    def parse_import(self) -> list[ASTImport]:
        self.expect(TokenType.IMPORT)
        self.push_loc()
        if self.match(TokenType.IDENT):
            token = self.expect(TokenType.IDENT)
            result = search_dirs(self.import_dirs, token.text + ".sw")
            if result is None:
                raise CompilerMessage(ErrorType.PARSE, f"Could not read from file '{token.text}.sw'", token.location)
            else:
                path = result
        else:
            path = Path(self.expect(TokenType.STRING).text[1:-1])
        imports = self.parse_import_specifier(path, [])
        return imports

    def parse_import_specifier(self, path: Path, names: list[str]) -> list[ASTImport]:
        if self.match(TokenType.COLON_COLON):
            self.expect(TokenType.COLON_COLON)
            if self.match(TokenType.LEFT_BRACE):
                self.pop_loc()
                imports = []
                self.expect(TokenType.LEFT_BRACE)
                while not self.match(TokenType.RIGHT_BRACE):
                    self.push_loc()
                    name = self.expect(TokenType.IDENT)
                    imports.extend(self.parse_import_specifier(path, names + [name.text]))
                    if self.match(TokenType.COMMA):
                        self.expect(TokenType.COMMA)
                    else:
                        break
                self.expect(TokenType.RIGHT_BRACE)
                return imports
            else:
                name = self.expect(TokenType.IDENT)
                return self.parse_import_specifier(path, names + [name.text])
        else:
            if self.match(TokenType.AS):
                self.expect(TokenType.AS)
                as_name = self.expect(TokenType.IDENT)
                return [ASTImport(path, names, as_name.text, self.pop_loc())]
            else:
                return [ASTImport(path, names, None, self.pop_loc())]

    def parse_function(self) -> ASTFunction:
        self.push_loc()
        if self.match(TokenType.EXTERN):
            is_extern = True
            self.advance()
        else:
            is_extern = False
        self.expect(TokenType.FN)
        name = self.expect(TokenType.IDENT)

        type_vars: list[ASTTypeVariable] = []
        if self.match(TokenType.LEFT_BRACKET):
            self.expect(TokenType.LEFT_BRACKET)
            while not self.match(TokenType.RIGHT_BRACKET):
                type_vars.append(self.parse_type_variable())
                if self.match(TokenType.COMMA):
                    self.advance()
                else:
                    break
            self.expect(TokenType.RIGHT_BRACKET)

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

        if is_extern:
            semicolon = self.expect(TokenType.SEMICOLON)
            body = ASTBlockExpr([], False, semicolon.location)
        else:
            body = self.parse_block()
        if len(type_vars) > 0:
            if is_extern:
                raise CompilerMessage(ErrorType.PARSE, "Generic functions cannot be marked 'extern'", self.pop_loc())
            return ASTGenericFunction(name.text, type_vars, parameters, ret_type, body, self.pop_loc())
        else:
            loc = self.pop_loc()
            return ASTFunction(name.text, is_extern, parameters, ret_type, body, loc)

    def parse_struct(self) -> ASTStruct:
        self.push_loc()
        self.expect(TokenType.STRUCT)
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
            if self.match(TokenType.FN):
                method = self.parse_method()
                if method.is_virtual:
                    raise CompilerMessage(ErrorType.PARSE, "Struct methods must have a body", method.loc)
                methods.append(method)
            else:
                fields.append(self.parse_struct_field())
        self.expect(TokenType.RIGHT_BRACE)
        return ASTStruct(name.text, type_variables, supertraits, fields, methods, self.pop_loc())

    def parse_struct_field(self) -> ASTStructField:
        self.push_loc()
        name = self.expect(TokenType.IDENT)
        self.expect(TokenType.COLON)
        type = self.parse_type()
        return ASTStructField(name, type, self.pop_loc())

    def parse_method(self) -> ASTMethod:
        self.push_loc()
        self.expect(TokenType.FN)

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

        if self.match(TokenType.SEMICOLON):
            loc = self.expect(TokenType.SEMICOLON).location
            if is_static:
                raise CompilerMessage(ErrorType.PARSE, "Static methods may not be virtual", loc)
            is_virtual = True
            body = ASTBlockExpr([], False, loc)
        else:
            is_virtual = False
            body = self.parse_block()
        return ASTMethod(name.text, parameters, ret_type, is_static, self_name, is_virtual, body, self.pop_loc())

    def parse_trait(self) -> ASTTrait:
        self.push_loc()
        self.expect(TokenType.TRAIT)
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
        self.expect(TokenType.LEFT_BRACE)
        while not self.match(TokenType.RIGHT_BRACE):
            methods.append(self.parse_method())
        self.expect(TokenType.RIGHT_BRACE)

        return ASTTrait(name.text, type_variables, supertraits, methods, self.pop_loc())

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
            return self.parse_decl_stmt()
        elif self.match(TokenType.RETURN):
            self.push_loc()
            ret_token = self.expect(TokenType.RETURN)
            expr = self.parse_expr()
            self.expect(TokenType.SEMICOLON)
            return ASTReturnStmt(expr, self.pop_loc())
        elif self.match(TokenType.WHILE):
            return self.parse_while()
        elif self.match(TokenType.FOR):
            return self.parse_for()
        else:
            self.push_loc()
            expr = self.parse_expr()
            has_semicolon = False
            if self.match(TokenType.SEMICOLON):
                self.expect(TokenType.SEMICOLON)
                has_semicolon = True
            return ASTExprStmt(expr, has_semicolon, self.pop_loc())

    def parse_while(self):
        self.push_loc()
        self.expect(TokenType.WHILE)
        cond = self.parse_expr()
        body = self.parse_expr()
        return ASTWhileStmt(cond, body, self.pop_loc())

    def parse_for(self):
        self.push_loc()
        self.expect(TokenType.FOR)
        iter_var = self.expect(TokenType.IDENT).text
        self.expect(TokenType.IN)
        iterator = self.parse_expr()
        body = self.parse_expr()
        return ASTForStmt(iter_var, iterator, body, self.pop_loc())

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
        self.expect(TokenType.SEMICOLON)
        if is_var:
            return ASTVarStmt(token, name, type, init, self.pop_loc())
        else:
            return ASTLetStmt(token, name, type, init, self.pop_loc())

    def parse_maybe_expr(self) -> ASTMaybeExpr:
        return self.parse_precedence_1()

    def parse_expr(self) -> ASTExpr:
        return self.parse_maybe_expr().as_expr()

    def parse_type(self) -> ASTType:
        return self.parse_maybe_expr().as_type()

    def parse_precedence_1(self) -> ASTMaybeExpr:
        if self.match(TokenType.IF):
            return self.parse_if()
        elif self.match(TokenType.LEFT_BRACE):
            return self.parse_block()
        else:
            return self.parse_precedence_2()

    def parse_if(self) -> ASTIfExpr:
        self.push_loc()
        self.expect(TokenType.IF)
        cond = self.parse_expr()
        then_do = self.parse_expr()
        if self.match(TokenType.ELSE):
            self.expect(TokenType.ELSE)
            else_do = self.parse_expr()
        else:
            else_do = None
        return ASTIfExpr(cond, then_do, else_do, self.pop_loc())

    def parse_block(self) -> ASTBlockExpr:
        self.push_loc()
        self.expect(TokenType.LEFT_BRACE)
        stmts: list[ASTStmt] = []
        while not self.match(TokenType.RIGHT_BRACE):
            stmt = self.parse_stmt()
            stmts.append(stmt)
            if isinstance(stmt, ASTExprStmt) and not stmt.trailing_semicolon and stmt.expr.requires_semicolon():
                if self.match(TokenType.RIGHT_BRACE):
                    break
                else:
                    # TODO better error message maybe?
                    self.expect(TokenType.SEMICOLON)
        if len(stmts) == 0:
            return_unit = True
        else:
            last_stmt = stmts[-1]
            if isinstance(last_stmt, ASTExprStmt):
                return_unit = last_stmt.trailing_semicolon
            else:
                return_unit = True

        self.expect(TokenType.RIGHT_BRACE)
        loc = self.pop_loc()
        return ASTBlockExpr(stmts, return_unit, loc)

    def parse_precedence_2(self) -> ASTMaybeExpr:
        left = self.parse_precedence_3()
        if self.match(TokenType.EQUAL, TokenType.PLUS_EQUAL, TokenType.MINUS_EQUAL, TokenType.STAR_EQUAL, TokenType.SLASH_EQUAL, TokenType.PERCENT_EQUAL):
            left_expr = left.as_expr()
            if not isinstance(left_expr, (ASTNameExpr, ASTAttrExpr)):
                return left
            self.push_loc()
            assign_type = self.advance()
            right = self.parse_precedence_2().as_expr()
            match assign_type.type:
                case TokenType.EQUAL:
                    op = "none"
                case TokenType.PLUS_EQUAL:
                    op = "Add"
                case TokenType.MINUS_EQUAL:
                    op = "Sub"
                case TokenType.STAR_EQUAL:
                    op = "Mul"
                case TokenType.SLASH_EQUAL:
                    op = "Div"
                case TokenType.PERCENT_EQUAL:
                    op = "Mod"
                case _:
                    raise ValueError()
            if isinstance(left_expr, ASTNameExpr):
                return ASTAssign(left_expr, op, right, self.pop_loc().combine(left.loc))
            elif isinstance(left_expr, ASTAttrExpr):
                return ASTAttrAssign(left_expr.object, left_expr.attr, op, right, self.pop_loc().combine(left.loc))
            else:
                raise CompilerMessage(ErrorType.PARSE, "Can only assign to identifiers or attributes", left.loc)
        else:
            return left

    def parse_precedence_3(self) -> ASTMaybeExpr:
        left = self.parse_precedence_4()
        while self.match(TokenType.OR):
            left_expr = left.as_expr()
            self.push_loc()
            self.expect(TokenType.OR)
            right = self.parse_precedence_4().as_expr()
            left = ASTOrExpr(left_expr, right, self.pop_loc().combine(left.loc))
        return left

    def parse_precedence_4(self) -> ASTMaybeExpr:
        left = self.parse_comparison()
        while self.match(TokenType.AND):
            left_expr = left.as_expr()
            self.push_loc()
            self.expect(TokenType.AND)
            right = self.parse_comparison().as_expr()
            left = ASTAndExpr(left_expr, right, self.pop_loc().combine(left.loc))
        return left

    def parse_comparison(self) -> ASTMaybeExpr:
        left = self.parse_precedence_5()
        while True:
            if self.match(TokenType.LESS):
                left_expr = left.as_expr()
                self.push_loc()
                self.expect(TokenType.LESS)
                right = self.parse_precedence_5().as_expr()
                left = ASTLessExpr(left_expr, right, self.pop_loc().combine(left.loc))
            elif self.match(TokenType.LESS_EQUAL):
                left_expr = left.as_expr()
                self.push_loc()
                self.expect(TokenType.LESS_EQUAL)
                right = self.parse_precedence_5().as_expr()
                left = ASTLessEqualExpr(left_expr, right, self.pop_loc().combine(left.loc))
            elif self.match(TokenType.GREATER):
                left_expr = left.as_expr()
                self.push_loc()
                self.expect(TokenType.GREATER)
                right = self.parse_precedence_5().as_expr()
                left = ASTGreaterExpr(left_expr, right, self.pop_loc().combine(left.loc))
            elif self.match(TokenType.GREATER_EQUAL):
                left_expr = left.as_expr()
                self.push_loc()
                self.expect(TokenType.GREATER_EQUAL)
                right = self.parse_precedence_5().as_expr()
                left = ASTGreaterEqualExpr(left_expr, right, self.pop_loc().combine(left.loc))
            elif self.match(TokenType.EQUAL_EQUAL):
                left_expr = left.as_expr()
                self.push_loc()
                self.expect(TokenType.EQUAL_EQUAL)
                right = self.parse_precedence_5().as_expr()
                left = ASTEqualExpr(left_expr, right, self.pop_loc().combine(left.loc))
            elif self.match(TokenType.NOT_EQUAL):
                left_expr = left.as_expr()
                self.push_loc()
                self.expect(TokenType.NOT_EQUAL)
                right = self.parse_precedence_5().as_expr()
                left = ASTNotEqualExpr(left_expr, right, self.pop_loc().combine(left.loc))
            else:
                break
        return left

    def parse_precedence_5(self) -> ASTMaybeExpr:
        left = self.parse_precedence_6()
        while True:
            if self.match(TokenType.PLUS):
                left_expr = left.as_expr()
                self.push_loc()
                self.expect(TokenType.PLUS)
                right = self.parse_precedence_6().as_expr()
                left = ASTAddExpr(left_expr, right, self.pop_loc().combine(left.loc))
            elif self.match(TokenType.MINUS):
                left_expr = left.as_expr()
                self.push_loc()
                self.expect(TokenType.MINUS)
                right = self.parse_precedence_6().as_expr()
                left = ASTSubExpr(left_expr, right, self.pop_loc().combine(left.loc))
            else:
                break
        return left

    def parse_precedence_6(self) -> ASTMaybeExpr:
        left = self.parse_precedence_7()
        while True:
            if self.match(TokenType.STAR):
                left_expr = left.as_expr()
                self.push_loc()
                self.expect(TokenType.STAR)
                right = self.parse_precedence_7().as_expr()
                left = ASTMulExpr(left_expr, right, self.pop_loc().combine(left.loc))
            elif self.match(TokenType.SLASH):
                left_expr = left.as_expr()
                self.push_loc()
                self.expect(TokenType.SLASH)
                right = self.parse_precedence_7().as_expr()
                left = ASTDivExpr(left_expr, right, self.pop_loc().combine(left.loc))
            elif self.match(TokenType.PERCENT):
                left_expr = left.as_expr()
                self.push_loc()
                self.expect(TokenType.PERCENT)
                right = self.parse_precedence_7().as_expr()
                left = ASTModExpr(left_expr, right, self.pop_loc().combine(left.loc))
            else:
                break
        return left

    def parse_precedence_7(self) -> ASTMaybeExpr:
        # self.push_loc()
        # left = self.parse_precedence_8()
        # if self.match(TokenType.STAR_STAR):
        #     self.expect(TokenType.STAR_STAR)
        #     right = self.parse_precedence_7()
        #     return ASTPowExpr(left, right, self.pop_loc())
        # else:
        #     self.pop_loc()
        #     return left
        return self.parse_precedence_8()

    def parse_precedence_8(self) -> ASTMaybeExpr:
        self.push_loc()
        if self.match(TokenType.MINUS):
            token = self.expect(TokenType.MINUS)
            right = self.parse_precedence_8().as_expr()
            return ASTNegExpr(token, right, self.pop_loc())
        elif self.match(TokenType.NOT):
            token = self.expect(TokenType.NOT)
            right = self.parse_precedence_8().as_expr()
            return ASTNotExpr(token, right, self.pop_loc())
        else:
            self.pop_loc()
            return self.parse_precedence_9()

    def parse_precedence_9(self) -> ASTMaybeExpr:
        left: ASTMaybeExpr = self.parse_precedence_10()
        while True:
            if self.match(TokenType.LEFT_PAREN):
                left_expr = left.as_expr()
                self.push_loc()
                arguments: list[ASTExpr] = []
                self.expect(TokenType.LEFT_PAREN)
                while not self.match(TokenType.RIGHT_PAREN):
                    argument = self.parse_expr()
                    arguments.append(argument)
                    if self.match(TokenType.COMMA):
                        self.expect(TokenType.COMMA)
                    else:
                        break
                self.expect(TokenType.RIGHT_PAREN)
                left = ASTCallExpr(left_expr, arguments, self.pop_loc().combine(left.loc))
            elif self.match(TokenType.LEFT_BRACKET):
                self.push_loc()
                arguments: list[ASTMaybeExpr] = []
                self.expect(TokenType.LEFT_BRACKET)
                while not self.match(TokenType.RIGHT_BRACKET):
                    argument = self.parse_maybe_expr()
                    arguments.append(argument)
                    if self.match(TokenType.COMMA):
                        self.expect(TokenType.COMMA)
                    else:
                        break
                end = self.expect(TokenType.RIGHT_BRACKET)
                left = ASTMaybeGeneric(left, arguments, self.pop_loc().combine(left.loc))
            elif self.match(TokenType.COLON_COLON):
                if isinstance(left, ASTMaybeGeneric):
                    left_type = left.as_type()
                    self.push_loc()
                    self.expect(TokenType.COLON_COLON)
                    name = self.expect(TokenType.IDENT).text
                    left = ASTGenericAttrExpr(left_type, name, self.pop_loc())
                else:
                    left_ns = left.as_namespace()
                    self.push_loc()
                    self.expect(TokenType.COLON_COLON)
                    name = self.expect(TokenType.IDENT).text
                    left = ASTMaybeName(name, left_ns, self.pop_loc().combine(left_ns.loc))
            elif self.match(TokenType.DOT):
                left_expr = left.as_expr()
                self.push_loc()
                self.expect(TokenType.DOT)
                attr = self.expect(TokenType.IDENT)
                left = ASTAttrExpr(left.as_expr(), attr, self.pop_loc().combine(left.loc))
            else:
                break
        return left

    def parse_precedence_10(self) -> ASTMaybeExpr:
        if self.match(TokenType.LEFT_PAREN):
            self.push_loc()
            items: list[ASTMaybeExpr] = []
            had_comma = False
            self.expect(TokenType.LEFT_PAREN)
            while not self.match(TokenType.RIGHT_PAREN):
                item = self.parse_maybe_expr()
                items.append(item)
                if self.match(TokenType.COMMA):
                    self.expect(TokenType.COMMA)
                    had_comma = True
                else:
                    break
            self.expect(TokenType.RIGHT_PAREN)

            if self.match(TokenType.ARROW):
                parameters: list[ASTType] = [item.as_type() for item in items]
                self.expect(TokenType.ARROW)
                ret_type = self.parse_type()
                return ASTFunctionType(parameters, ret_type, self.pop_loc())
            elif len(items) == 0:
                return ASTMaybeUnit(self.pop_loc())
            elif len(items) == 1 and not had_comma:
                self.pop_loc()
                return items[0]
            else:
                self.pop_loc()
                self.expect(TokenType.ARROW)
        elif self.match(TokenType.BAR):
            self.push_loc()
            parameters: list[ASTParameter] = []
            self.expect(TokenType.BAR)
            while not self.match(TokenType.BAR):
                self.push_loc()
                name = self.expect(TokenType.IDENT)
                if self.match(TokenType.COLON):
                    self.expect(TokenType.COLON)
                    parameter = self.parse_type()
                else:
                    parameter = None
                parameters.append(ASTParameter(name.text, parameter, self.pop_loc()))
                if self.match(TokenType.COMMA):
                    self.expect(TokenType.COMMA)
                else:
                    break
            self.expect(TokenType.BAR)
            if self.match(TokenType.ARROW):
                self.expect(TokenType.ARROW)
                ret_type = self.parse_type()
            else:
                ret_type = None
            expr = self.parse_expr()
            return ASTLambda(parameters, ret_type, expr, self.pop_loc())
        elif self.match(TokenType.BINARY) or self.match(TokenType.HEX) or self.match(TokenType.INTEGER):
            number = self.advance()
            return ASTIntegerExpr(number)
        else:
            tok = self.expect(TokenType.IDENT)
            return ASTMaybeName(tok.text, None, tok.location)
