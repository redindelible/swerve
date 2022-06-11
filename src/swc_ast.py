from __future__ import annotations

from pathlib import Path
from contextlib import contextmanager

from common import Location, SourceLocation
from tokens import Token, TokenType


__all__ = ["ASTFunction", "ASTParameter", "ASTStmt", "ASTLetStmt", "ASTVarStmt", "ASTExprStmt", "ASTExpr", "ASTBlockExpr",
    "ASTReturnStmt", "ASTAssign", "ASTAddExpr", "ASTSubExpr", "ASTMulExpr", "ASTDivExpr", "ASTPowExpr", "ASTOrExpr", "ASTAndExpr",
    "ASTNegExpr", "ASTNotExpr", "ASTCallExpr", "ASTAttrExpr", "ASTIntegerExpr", "ASTStringExpr", "ASTGroupExpr", "ASTIdentExpr",
    "ASTType", "ASTTypeIdent", "ASTFile", "ASTNode", "ASTProgram", "ASTTopLevel", "ASTStruct", "ASTTypeVariable", "ASTMethod",
    "ASTStructField", "ASTImport", "ASTBinaryExpr", "ASTForStmt", "ASTIfExpr", "ASTWhileStmt", "ASTTypeGeneric", "ASTGenericExpr",
    "ASTLessExpr", "ASTLessEqualExpr", "ASTGreaterExpr", "ASTGreaterEqualExpr", "ASTAttrAssign", "ASTTypeUnit", "ASTTypeFunction",
    "ASTLambda", "ASTEqualExpr", "ASTNotEqualExpr", "ASTModExpr", "ASTGenericFunction"]


class Printer:
    def __init__(self):
        self.level = 0

    @contextmanager
    def indent(self):
        self.level += 1
        yield
        self.level -= 1

    def print(self, s: str):
        print('  '*self.level + s)


class ASTNode:
    def __init__(self, loc: Location):
        self.loc = loc

    def pretty_print(self, printer: Printer):
        raise NotImplementedError()


class ASTProgram:
    def __init__(self, files: list[ASTFile]):
        self.files = files

    def pretty_print(self):
        print("Program:")
        for file in self.files:
            file.pretty_print(Printer())


class ASTFile:
    def __init__(self, path: Path, top_levels: list[ASTTopLevel], is_main: bool):
        self.path = path
        self.top_levels = top_levels
        self.is_main = is_main

    def pretty_print(self, printer: Printer):
        printer.print(f"File:")
        with printer.indent():
            printer.print(f"Path={self.path}")
            printer.print(f"Top Levels:")
            with printer.indent():
                for top_level in self.top_levels:
                    top_level.pretty_print(printer)


class ASTTopLevel(ASTNode):
    def pretty_print(self, printer: Printer):
        raise NotImplementedError()


class ASTImport(ASTTopLevel):
    def __init__(self, path: Path, names: list[str], as_name: str | None, location: Location):
        super().__init__(location)
        self.path = path
        self.names = names
        if as_name is not None:
            self.as_name = as_name
        elif len(names) == 0:
            self.as_name = path.stem
        else:
            self.as_name = names[-1]

    def pretty_print(self, printer: Printer):
        printer.print("Import:")
        with printer.indent():
            printer.print(f"Path={self.path}")
            printer.print(f"Names={self.names}")
            printer.print(f"As={self.as_name}")


class ASTFunction(ASTTopLevel):
    def __init__(self, name: str, parameters: list[ASTParameter], return_type: ASTType, body: ASTBlockExpr, location: Location):
        super().__init__(location)
        self.name = name
        self.parameters = parameters
        self.return_type = return_type
        self.body = body

    def pretty_print(self, printer: Printer):
        printer.print("Function:")
        with printer.indent():
            printer.print(f"Name={self.name}")
            printer.print(f"Parameters:")
            with printer.indent():
                for param in self.parameters:
                    param.pretty_print(printer)
            printer.print(f"Return Type:")
            with printer.indent():
                self.return_type.pretty_print(printer)
            printer.print(f"Body:")
            with printer.indent():
                for stmt in self.body.stmts:
                    stmt.pretty_print(printer)


class ASTGenericFunction(ASTFunction):
    def __init__(self, name: str, type_vars: list[ASTTypeVariable], parameters: list[ASTParameter], return_type: ASTType, body: ASTBlockExpr, location: Location):
        super().__init__(name, parameters, return_type, body, location)
        self.type_vars = type_vars

    def pretty_print(self, printer: Printer):
        printer.print("Function:")
        with printer.indent():
            printer.print(f"Name={self.name}")
            printer.print(f"Parameters:")
            with printer.indent():
                for param in self.parameters:
                    param.pretty_print(printer)
            printer.print(f"Return Type:")
            with printer.indent():
                self.return_type.pretty_print(printer)
            printer.print(f"Body:")
            with printer.indent():
                for stmt in self.body.stmts:
                    stmt.pretty_print(printer)


class ASTParameter(ASTNode):
    def __init__(self, name: str, type: ASTType | None, location: Location):
        super().__init__(location)
        self.name = name
        self.type = type

    def pretty_print(self, printer: Printer):
        printer.print("Parameter:")
        with printer.indent():
            printer.print(f"Name={self.name}")
            printer.print(f"Type:")
            with printer.indent():
                self.type.pretty_print(printer)


class ASTStruct(ASTTopLevel):
    def __init__(self, name: Token, type_variables: list[ASTTypeVariable], supertraits: list[ASTType],
                 fields: list[ASTStructField], methods: list[ASTMethod], location: SourceLocation):
        super().__init__(location)
        self.name: str = name.text
        self.type_variables = type_variables
        self.supertraits = supertraits
        self.fields = fields
        self.methods = methods

    def pretty_print(self, printer: Printer):
        printer.print("Struct:")
        with printer.indent():
            printer.print(f"Name={self.name}")
            printer.print(f"Type Variables:")
            with printer.indent():
                for type_var in self.type_variables:
                    type_var.pretty_print(printer)
            printer.print(f"Super Traits:")
            with printer.indent():
                for trait in self.supertraits:
                    trait.pretty_print(printer)
            printer.print(f"Fields:")
            with printer.indent():
                for field in self.fields:
                    field.pretty_print(printer)
            printer.print(f"Methods:")
            with printer.indent():
                for method in self.methods:
                    method.pretty_print(printer)


class ASTStructField(ASTNode):
    def __init__(self, name: Token, type: ASTType, location: Location):
        super().__init__(location)
        self.name: str = name.text
        self.type = type

    def pretty_print(self, printer: Printer):
        printer.print("Struct Field:")
        with printer.indent():
            printer.print(f"Name={self.name}")
            printer.print(f"Type:")
            with printer.indent():
                self.type.pretty_print(printer)


class ASTMethod(ASTNode):
    def __init__(self, start: Token, name: Token, parameters: list[ASTParameter], is_static: bool, self_name: Token | None, return_type: ASTType, body: ASTBlockExpr, location: Location):
        super().__init__(location)
        self.name: str = name.text
        self.parameters = parameters
        self.is_static = is_static
        self.self_name: Token | None = self_name
        self.return_type = return_type
        self.body = body

    def pretty_print(self, printer: Printer):
        printer.print("Method:")
        with printer.indent():
            printer.print(f"Name={self.name}")
            printer.print(f"Is Static={self.is_static}")
            printer.print(f"Parameters:")
            with printer.indent():
                for param in self.parameters:
                    param.pretty_print(printer)
            printer.print(f"Self={self.self_name}")
            printer.print(f"Return Type:")
            with printer.indent():
                self.return_type.pretty_print(printer)
            printer.print(f"Body:")
            with printer.indent():
                for stmt in self.body.stmts:
                    stmt.pretty_print(printer)


class ASTTypeVariable(ASTNode):
    def __init__(self, name: str, bound: ASTType | None, location: Location):
        super().__init__(location)
        self.name = name
        self.bound = bound

    def pretty_print(self, printer: Printer):
        printer.print("Type Variable:")
        with printer.indent():
            printer.print(f"Name={self.name}")
            if self.bound is None:
                printer.print(f"Bound: None")
            else:
                printer.print(f"Bound:")
                with printer.indent():
                    self.bound.pretty_print(printer)


class ASTStmt(ASTNode):
    def pretty_print(self, printer: Printer):
        raise NotImplementedError()


class ASTLetStmt(ASTStmt):
    def __init__(self, let_token: Token, name: Token, type: ASTType | None, init: ASTExpr, location: Location):
        super().__init__(location)
        self.name: str = name.text
        self.type = type
        self.init = init

    def pretty_print(self, printer: Printer):
        printer.print("Let Statement:")
        with printer.indent():
            printer.print(f"Name={self.name}")
            if self.type is not None:
                printer.print(f"Type:")
                with printer.indent():
                    self.type.pretty_print(printer)
            printer.print("Init:")
            with printer.indent():
                self.init.pretty_print(printer)


class ASTVarStmt(ASTStmt):
    def __init__(self, var_token: Token, name: Token, type: ASTType | None, init: ASTExpr, location: Location):
        super().__init__(location)
        self.name: str = name.text
        self.type: ASTType = type
        self.init: ASTExpr = init

    def pretty_print(self, printer: Printer):
        printer.print("Var Statement:")
        with printer.indent():
            printer.print(f"Name={self.name}")
            if self.type is not None:
                printer.print(f"Type:")
                with printer.indent():
                    self.type.pretty_print(printer)
            printer.print("Init:")
            with printer.indent():
                self.init.pretty_print(printer)


class ASTWhileStmt(ASTStmt):
    def __init__(self, cond: ASTExpr, body: ASTExpr, location: Location):
        super().__init__(location)
        self.cond = cond
        self.body = body

    def pretty_print(self, printer: Printer):
        printer.print("While Statement:")
        with printer.indent():
            printer.print(f"Cond:")
            with printer.indent():
                self.cond.pretty_print(printer)
            printer.print("Body:")
            with printer.indent():
                self.body.pretty_print(printer)


class ASTForStmt(ASTStmt):
    def __init__(self, iter_var: str, iterator: ASTExpr, body: ASTExpr, location: Location):
        super().__init__(location)
        self.iter_var = iter_var
        self.iterator = iterator
        self.body = body

    def pretty_print(self, printer: Printer):
        printer.print("For Statement:")
        with printer.indent():
            printer.print(f"Iter Var: {self.iter_var}")
            printer.print(f"Iterator:")
            with printer.indent():
                self.iterator.pretty_print(printer)
            printer.print("Body:")
            with printer.indent():
                self.body.pretty_print(printer)


class ASTExprStmt(ASTStmt):
    def __init__(self, expr: ASTExpr, has_trailing_semicolon: bool, loc: Location):
        super().__init__(loc)
        self.trailing_semicolon = has_trailing_semicolon
        self.expr: ASTExpr = expr

    def pretty_print(self, printer: Printer):
        printer.print("Expression Statement:")
        with printer.indent():
            self.expr.pretty_print(printer)


class ASTReturnStmt(ASTStmt):
    def __init__(self, expr: ASTExpr, location: Location):
        super().__init__(location)
        self.expr = expr

    def pretty_print(self, printer: Printer):
        printer.print("Return:")
        with printer.indent():
            self.expr.pretty_print(printer)


class ASTExpr(ASTNode):
    @staticmethod
    def requires_semicolon():
        return True

    def pretty_print(self, printer: Printer):
        raise NotImplementedError()


class ASTIfExpr(ASTExpr):
    def __init__(self, cond: ASTExpr, then_do: ASTExpr, else_do: ASTExpr | None, location: Location):
        super().__init__(location)
        self.cond = cond
        self.then_do = then_do
        self.else_do = else_do

    @staticmethod
    def requires_semicolon():
        return False

    def pretty_print(self, printer: Printer):
        printer.print(f"If:")
        with printer.indent():
            printer.print(f"Cond:")
            with printer.indent():
                self.cond.pretty_print(printer)
            printer.print(f"Then:")
            with printer.indent():
                self.then_do.pretty_print(printer)
            if self.else_do:
                printer.print(f"Else:")
                with printer.indent():
                    self.else_do.pretty_print(printer)


class ASTBlockExpr(ASTExpr):
    def __init__(self, body: list[ASTStmt], return_unit: bool, location: Location):
        super().__init__(location)
        self.stmts = body
        self.return_unit = return_unit

    @staticmethod
    def requires_semicolon():
        return False

    def pretty_print(self, printer: Printer):
        printer.print("Method:")
        with printer.indent():
            for stmt in self.stmts:
                stmt.pretty_print(printer)


class ASTAssign(ASTExpr):
    def __init__(self, name: ASTIdentExpr, op: str, value: ASTExpr, location: Location):
        super().__init__(location)
        self.name: str = name.ident
        self.op = op
        self.value = value

    def pretty_print(self, printer: Printer):
        # printer.print("Assign:")
        # with printer.indent():
        #     printer.print(f"Name={self.name}")
        #     printer.print(f"Value:")
        #     with printer.indent():
        #         self.value.pretty_print(printer)
        raise NotImplementedError()


class ASTAttrAssign(ASTExpr):
    def __init__(self, obj: ASTExpr, attr: str, op: str, value: ASTExpr, location: Location):
        super().__init__(location)
        self.obj = obj
        self.attr = attr
        self.op = op
        self.value = value

    def pretty_print(self, printer: Printer):
        raise NotImplementedError()


class ASTBinaryExpr(ASTExpr):
    NAME: str

    def __init__(self, left: ASTExpr, right: ASTExpr, location: Location):
        super().__init__(location)
        self.left: ASTExpr = left
        self.right: ASTExpr = right

    def pretty_print(self, printer: Printer):
        printer.print(f"{self.NAME}:")
        with printer.indent():
            printer.print(f"Left:")
            with printer.indent():
                self.left.pretty_print(printer)
            printer.print(f"Right:")
            with printer.indent():
                self.right.pretty_print(printer)


class ASTAddExpr(ASTBinaryExpr):
    NAME = "Add"


class ASTSubExpr(ASTBinaryExpr):
    NAME = "Sub"


class ASTMulExpr(ASTBinaryExpr):
    NAME = "Mul"


class ASTDivExpr(ASTBinaryExpr):
    NAME = "Div"


class ASTModExpr(ASTBinaryExpr):
    NAME = "Mod"


class ASTPowExpr(ASTBinaryExpr):
    NAME = "Pow"


class ASTOrExpr(ASTBinaryExpr):
    NAME = "Or"


class ASTAndExpr(ASTBinaryExpr):
    NAME = "And"


class ASTLessExpr(ASTBinaryExpr):
    NAME = "Less"


class ASTLessEqualExpr(ASTBinaryExpr):
    NAME = "LessEqual"


class ASTGreaterExpr(ASTBinaryExpr):
    NAME = "Greater"


class ASTGreaterEqualExpr(ASTBinaryExpr):
    NAME = "GreaterEqual"


class ASTEqualExpr(ASTBinaryExpr):
    NAME = "Equal"


class ASTNotEqualExpr(ASTBinaryExpr):
    NAME = "NotEqual"


class ASTNegExpr(ASTExpr):
    def __init__(self, token: Token, right: ASTExpr, location: Location):
        super().__init__(location)
        self.right = right

    def pretty_print(self, printer: Printer):
        printer.print("Neg:")
        with printer.indent():
            self.right.pretty_print(printer)


class ASTNotExpr(ASTExpr):
    def __init__(self, token: Token, right: ASTExpr, location: Location):
        super().__init__(location)
        self.right = right

    def pretty_print(self, printer: Printer):
        printer.print("Neg:")
        with printer.indent():
            self.right.pretty_print(printer)


class ASTLambda(ASTExpr):
    def __init__(self, parameters: list[ASTParameter], ret_type: ASTType | None, expr: ASTExpr, loc: Location):
        super().__init__(loc)
        self.parameters = parameters
        self.ret_type = ret_type
        self.expr = expr

    def pretty_print(self, printer: Printer):
        raise NotImplementedError()


class ASTCallExpr(ASTExpr):
    def __init__(self, callee: ASTExpr, arguments: list[ASTExpr], location: Location):
        super().__init__(location)
        self.callee = callee
        self.arguments = arguments

    def pretty_print(self, printer: Printer):
        printer.print("Call:")
        with printer.indent():
            printer.print("Callee:")
            with printer.indent():
                self.callee.pretty_print(printer)
            printer.print("Arguments:")
            with printer.indent():
                for arg in self.arguments:
                    arg.pretty_print(printer)


class ASTGenericExpr(ASTExpr):
    def __init__(self, generic: ASTExpr, arguments: list[ASTType], loc: Location):
        super().__init__(loc)
        self.generic = generic
        self.arguments = arguments

    def pretty_print(self, printer: Printer):
        raise NotImplementedError()


class ASTAttrExpr(ASTExpr):
    def __init__(self, object: ASTExpr, attr: Token, location: Location):
        super().__init__(location)
        self.object = object
        self.attr: str = attr.text

    def pretty_print(self, printer: Printer):
        printer.print("Attr:")
        with printer.indent():
            printer.print("Object:")
            with printer.indent():
                self.object.pretty_print(printer)
            printer.print(f"Name={self.attr}")


class ASTIntegerExpr(ASTExpr):
    def __init__(self, number: Token):
        super().__init__(number.location)
        if number.type == TokenType.BINARY:
            self.number: int = int(number.text, 2)
        elif number.type == TokenType.HEX:
            self.number: int = int(number.text, 16)
        else:
            self.number: int = int(number.text, 10)

    def pretty_print(self, printer: Printer):
        printer.print(f"Integer={self.number}")


class ASTStringExpr(ASTExpr):
    def __init__(self, string: Token):
        super().__init__(string.location)
        self.string = string.text[1:-1]
        #TODO replace \ things

    def pretty_print(self, printer: Printer):
        printer.print(f"String={self.string!r}")


class ASTGroupExpr(ASTExpr):
    def __init__(self, expr: ASTExpr, location: Location):
        super().__init__(location)
        self.expr = expr

    def pretty_print(self, printer: Printer):
        printer.print(f"Group:")
        with printer.indent():
            self.expr.pretty_print(printer)


class ASTIdentExpr(ASTExpr):
    def __init__(self, ident: Token):
        super().__init__(ident.location)
        self.ident: str = ident.text

    def pretty_print(self, printer: Printer):
        printer.print(f"Ident={self.ident!r}")


class ASTType(ASTNode):
    def pretty_print(self, printer: Printer):
        raise NotImplementedError()


class ASTTypeGeneric(ASTType):
    def __init__(self, generic: ASTType, type_arguments: list[ASTType], loc: Location):
        super().__init__(loc)
        self.generic = generic
        self.type_arguments = type_arguments

    def pretty_print(self, printer: Printer):
        #TODO
        pass


class ASTTypeIdent(ASTType):
    def __init__(self, name: str, loc: Location):
        super().__init__(loc)
        self.name: str = name

    def pretty_print(self, printer: Printer):
        printer.print(f"Type Ident={self.name!r}")


class ASTTypeFunction(ASTType):
    def __init__(self, parameters: list[ASTType], ret_type: ASTType, loc: Location):
        super().__init__(loc)
        self.parameters = parameters
        self.ret_type = ret_type

    def pretty_print(self, printer: Printer):
        raise NotImplementedError()


class ASTTypeUnit(ASTType):
    def __init__(self, loc: Location):
        super().__init__(loc)

    def pretty_print(self, printer: Printer):
        raise NotImplementedError()