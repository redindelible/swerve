from __future__ import annotations

from pathlib import Path
from contextlib import contextmanager

from common import Location, SourceLocation
from tokens import Token, TokenType


__all__ = ["ASTFunction", "ASTParameter", "ASTStmt", "ASTLetStmt", "ASTVarStmt", "ASTExprStmt", "ASTExpr", "ASTBlockExpr",
    "ASTReturnExpr", "ASTAssign", "ASTAddExpr", "ASTSubExpr", "ASTMulExpr", "ASTDivExpr", "ASTPowExpr", "ASTOrExpr", "ASTAndExpr",
    "ASTNegExpr", "ASTNotExpr", "ASTCallExpr", "ASTAttrExpr", "ASTIntegerExpr", "ASTStringExpr", "ASTGroupExpr", "ASTIdentExpr",
    "ASTType", "ASTTypeIdent", "ASTFile", "ASTNode", "ASTProgram", "ASTTopLevel", "ASTStruct", "ASTTypeVariable", "ASTMethod",
    "ASTStructField", "ASTImport"]


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
        self.location = loc

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
    def __init__(self, path: Path, top_levels: list[ASTTopLevel]):
        self.path = path
        self.top_levels = top_levels

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
                for stmt in self.body.body:
                    stmt.pretty_print(printer)


class ASTParameter(ASTNode):
    def __init__(self, name: str, type: ASTType, location: Location):
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
        self.self_name: str | None = self_name.text if self_name is not None else None
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
                for stmt in self.body.body:
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
            printer.print(f"Type:")
            with printer.indent():
                self.type.pretty_print(printer)
            printer.print("Init:")
            with printer.indent():
                self.init.pretty_print(printer)


class ASTExprStmt(ASTStmt):
    def __init__(self, expr: ASTExpr, loc: Location):
        super().__init__(loc)
        self.expr: ASTExpr = expr

    def pretty_print(self, printer: Printer):
        printer.print("Expression Statement:")
        with printer.indent():
            self.expr.pretty_print(printer)


class ASTExpr(ASTNode):
    def pretty_print(self, printer: Printer):
        raise NotImplementedError()


class ASTBlockExpr(ASTExpr):
    def __init__(self, body: list[ASTStmt], location: Location):
        super().__init__(location)
        self.body = body

    def pretty_print(self, printer: Printer):
        printer.print("Method:")
        with printer.indent():
            for stmt in self.body:
                stmt.pretty_print(printer)


class ASTReturnExpr(ASTExpr):
    def __init__(self, expr: ASTExpr, location: Location):
        super().__init__(location)
        self.expr = expr

    def pretty_print(self, printer: Printer):
        printer.print("Return:")
        with printer.indent():
            self.expr.pretty_print(printer)


class ASTAssign(ASTExpr):
    def __init__(self, name: ASTIdentExpr, value: ASTExpr, location: Location):
        super().__init__(location)
        self.name: str = name.ident
        self.value = value

    def pretty_print(self, printer: Printer):
        printer.print("Assign:")
        with printer.indent():
            printer.print(f"Name={self.name}")
            printer.print(f"Value:")
            with printer.indent():
                self.value.pretty_print(printer)


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


class ASTPowExpr(ASTBinaryExpr):
    NAME = "Pow"


class ASTOrExpr(ASTBinaryExpr):
    NAME = "Or"


class ASTAndExpr(ASTBinaryExpr):
    NAME = "And"


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


class ASTCallExpr(ASTExpr):
    def __init__(self, callee: ASTExpr, arguments: list[ASTExpr], end: Token, location: Location):
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


class ASTTypeIdent(ASTType):
    def __init__(self, ident: str, loc: Location):
        super().__init__(loc)
        self.ident: str = ident

    def pretty_print(self, printer: Printer):
        printer.print(f"Type Ident={self.ident!r}")
