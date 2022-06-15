from __future__ import annotations

from pathlib import Path

from .common import Location, SourceLocation, CompilerMessage, ErrorType
from .tokens import Token, TokenType


__all__ = ["ASTFunction", "ASTParameter", "ASTStmt", "ASTLetStmt", "ASTVarStmt", "ASTExprStmt", "ASTExpr", "ASTBlockExpr",
    "ASTReturnStmt", "ASTAssign", "ASTAddExpr", "ASTSubExpr", "ASTMulExpr", "ASTDivExpr", "ASTPowExpr", "ASTOrExpr", "ASTAndExpr",
    "ASTNegExpr", "ASTNotExpr", "ASTCallExpr", "ASTAttrExpr", "ASTIntegerExpr", "ASTNameExpr", "ASTMaybeUnit", "ASTGenericAttrExpr",
    "ASTType", "ASTNameType", "ASTFile", "ASTNode", "ASTProgram", "ASTTopLevel", "ASTStruct", "ASTTypeVariable", "ASTMethod",
    "ASTStructField", "ASTImport", "ASTBinaryExpr", "ASTForStmt", "ASTIfExpr", "ASTWhileStmt", "ASTGenericType", "ASTGenericExpr",
    "ASTLessExpr", "ASTLessEqualExpr", "ASTGreaterExpr", "ASTGreaterEqualExpr", "ASTAttrAssign", "ASTUnitType", "ASTFunctionType",
    "ASTLambda", "ASTEqualExpr", "ASTNotEqualExpr", "ASTModExpr", "ASTGenericFunction", "ASTTrait", "ASTMaybeExpr",
    "ASTIndexExpr", "ASTMaybeName", "ASTIndexOrGenericExpr", "ASTNamespace", "ASTMaybeGeneric"]


class ASTNode:
    def __init__(self, loc: Location):
        self.loc = loc


class ASTProgram:
    def __init__(self, files: list[ASTFile]):
        self.files = files


class ASTFile:
    def __init__(self, path: Path, top_levels: list[ASTTopLevel], is_main: bool):
        self.path = path
        self.top_levels = top_levels
        self.is_main = is_main


class ASTTopLevel(ASTNode):
    pass


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


class ASTFunction(ASTTopLevel):
    def __init__(self, name: str, is_extern: bool, parameters: list[ASTParameter], return_type: ASTType, body: ASTBlockExpr, location: Location):
        super().__init__(location)
        self.name = name
        self.is_extern = is_extern
        self.parameters = parameters
        self.return_type = return_type
        self.body = body


class ASTGenericFunction(ASTFunction):
    def __init__(self, name: str, type_vars: list[ASTTypeVariable], parameters: list[ASTParameter], return_type: ASTType, body: ASTBlockExpr, location: Location):
        super().__init__(name, False, parameters, return_type, body, location)
        self.type_vars = type_vars


class ASTParameter(ASTNode):
    def __init__(self, name: str, type: ASTType | None, location: Location):
        super().__init__(location)
        self.name = name
        self.type = type


class ASTStruct(ASTTopLevel):
    def __init__(self, name: str, type_variables: list[ASTTypeVariable], traits: list[ASTType], fields: list[ASTStructField], methods: list[ASTMethod], location: SourceLocation):
        super().__init__(location)
        self.name = name
        self.type_variables = type_variables
        self.traits = traits
        self.fields = fields
        self.methods = methods


class ASTTrait(ASTTopLevel):
    def __init__(self, name: str, type_variables: list[ASTTypeVariable], traits: list[ASTType], methods: list[ASTMethod], location: SourceLocation):
        super().__init__(location)
        self.name = name
        self.type_variables = type_variables
        self.traits = traits
        self.methods = methods


class ASTStructField(ASTNode):
    def __init__(self, name: Token, type: ASTType, location: Location):
        super().__init__(location)
        self.name: str = name.text
        self.type = type


class ASTMethod(ASTNode):
    def __init__(self, name: str, parameters: list[ASTParameter], return_type: ASTType,
                 is_static: bool, self_name: Token | None, is_virtual: bool, body: ASTBlockExpr, location: Location):
        super().__init__(location)
        self.name = name
        self.parameters = parameters
        self.is_static = is_static
        self.self_name: Token | None = self_name
        self.is_virtual = is_virtual
        self.return_type = return_type
        self.body = body


class ASTTypeVariable(ASTNode):
    def __init__(self, name: str, bound: ASTType | None, location: Location):
        super().__init__(location)
        self.name = name
        self.bound = bound


class ASTStmt(ASTNode):
    pass


class ASTLetStmt(ASTStmt):
    def __init__(self, let_token: Token, name: Token, type: ASTType | None, init: ASTExpr, location: Location):
        super().__init__(location)
        self.name: str = name.text
        self.type = type
        self.init = init


class ASTVarStmt(ASTStmt):
    def __init__(self, var_token: Token, name: Token, type: ASTType | None, init: ASTExpr, location: Location):
        super().__init__(location)
        self.name: str = name.text
        self.type: ASTType = type
        self.init: ASTExpr = init


class ASTWhileStmt(ASTStmt):
    def __init__(self, cond: ASTExpr, body: ASTExpr, location: Location):
        super().__init__(location)
        self.cond = cond
        self.body = body


class ASTForStmt(ASTStmt):
    def __init__(self, iter_var: str, iterator: ASTExpr, body: ASTExpr, location: Location):
        super().__init__(location)
        self.iter_var = iter_var
        self.iterator = iterator
        self.body = body

class ASTExprStmt(ASTStmt):
    def __init__(self, expr: ASTExpr, has_trailing_semicolon: bool, loc: Location):
        super().__init__(loc)
        self.trailing_semicolon = has_trailing_semicolon
        self.expr: ASTExpr = expr


class ASTReturnStmt(ASTStmt):
    def __init__(self, expr: ASTExpr, location: Location):
        super().__init__(location)
        self.expr = expr


class ASTMaybeExpr(ASTNode):
    @staticmethod
    def is_certain() -> bool:
        return False

    def as_expr(self) -> ASTExpr:
        raise CompilerMessage(ErrorType.PARSE, f"Could not interpret this as an expression", self.loc)

    def as_type(self) -> ASTType:
        raise CompilerMessage(ErrorType.PARSE, f"Could not interpret this as a type", self.loc)

    def as_namespace(self) -> ASTNamespace:
        raise CompilerMessage(ErrorType.PARSE, f"Could not interpret this as a namespace", self.loc)


class ASTMaybeName(ASTMaybeExpr):
    def __init__(self, name: str, ns: ASTNamespace | None, loc: Location):
        super().__init__(loc)
        self.name = name
        self.ns = ns

    def as_expr(self) -> ASTNameExpr:
        return ASTNameExpr(self.name, self.ns, self.loc)

    def as_type(self) -> ASTNameType:
        return ASTNameType(self.name, self.ns, self.loc)

    def as_namespace(self) -> ASTNamespace:
        return ASTNamespace(self.name, self.ns, self.loc)


class ASTMaybeUnit(ASTMaybeExpr):
    def __init__(self, loc: Location):
        super().__init__(loc)

    def as_type(self) -> ASTUnitType:
        return ASTUnitType(self.loc)


class ASTMaybeGeneric(ASTMaybeExpr):
    def __init__(self, generic: ASTMaybeExpr, arguments: list[ASTMaybeExpr], loc: Location):
        super().__init__(loc)
        self.generic = generic
        self.arguments = arguments

    def as_expr(self) -> ASTExpr:
        generic = self.generic
        if len(self.arguments) == 1:
            arg = self.arguments[0]
            can_be_expr = False
            try:
                arg.as_expr()
                can_be_expr = True
            except CompilerMessage:
                pass
            can_be_type = False
            try:
                arg.as_type()
                can_be_type = True
            except CompilerMessage:
                pass
            if isinstance(generic, ASTMaybeName):
                if can_be_expr and can_be_type:
                    return ASTIndexOrGenericExpr(generic.as_expr(), arg, self.loc)
                elif can_be_type:
                    return ASTGenericExpr(generic.as_expr(), [arg.as_type()], self.loc)
                elif can_be_expr:
                    return ASTIndexExpr(generic.as_expr(), arg.as_expr(), self.loc)
                else:
                    raise CompilerMessage(ErrorType.PARSE, f"Cannot interpret as an expression", self.loc)
            else:
                return ASTIndexExpr(generic.as_expr(), arg.as_expr(), self.loc)
        else:
            if isinstance(generic, ASTMaybeName):
                return ASTGenericExpr(generic.as_expr(), [arg.as_type() for arg in self.arguments], self.loc)
            else:
                raise CompilerMessage(ErrorType.PARSE, f"Cannot interpret as an expression", self.loc)

    def as_type(self) -> ASTGenericType:
        generic = self.generic
        if isinstance(generic, ASTMaybeName):
            return ASTGenericType(generic.as_type(), [arg.as_type() for arg in self.arguments], self.loc)
        else:
            raise CompilerMessage(ErrorType.PARSE, f"Cannot interpret as a type", self.loc)



class ASTExpr(ASTMaybeExpr):
    @staticmethod
    def is_certain():
        return True

    def as_expr(self) -> ASTExpr:
        return self

    @staticmethod
    def requires_semicolon():
        return True


class ASTIfExpr(ASTExpr):
    def __init__(self, cond: ASTExpr, then_do: ASTExpr, else_do: ASTExpr | None, location: Location):
        super().__init__(location)
        self.cond = cond
        self.then_do = then_do
        self.else_do = else_do

    @staticmethod
    def requires_semicolon():
        return False


class ASTBlockExpr(ASTExpr):
    def __init__(self, body: list[ASTStmt], return_unit: bool, location: Location):
        super().__init__(location)
        self.stmts = body
        self.return_unit = return_unit

    @staticmethod
    def requires_semicolon():
        return False


class ASTAssign(ASTExpr):
    def __init__(self, name: ASTNameExpr, op: str, value: ASTExpr, location: Location):
        super().__init__(location)
        self.name: str = name.ident
        self.op = op
        self.value = value


class ASTAttrAssign(ASTExpr):
    def __init__(self, obj: ASTExpr, attr: str, op: str, value: ASTExpr, location: Location):
        super().__init__(location)
        self.obj = obj
        self.attr = attr
        self.op = op
        self.value = value


class ASTBinaryExpr(ASTExpr):
    NAME: str

    def __init__(self, left: ASTExpr, right: ASTExpr, location: Location):
        super().__init__(location)
        self.left: ASTExpr = left
        self.right: ASTExpr = right


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


class ASTNotExpr(ASTExpr):
    def __init__(self, token: Token, right: ASTExpr, location: Location):
        super().__init__(location)
        self.right = right


class ASTLambda(ASTExpr):
    def __init__(self, parameters: list[ASTParameter], ret_type: ASTType | None, expr: ASTExpr, loc: Location):
        super().__init__(loc)
        self.parameters = parameters
        self.ret_type = ret_type
        self.expr = expr


class ASTCallExpr(ASTExpr):
    def __init__(self, callee: ASTExpr, arguments: list[ASTExpr], location: Location):
        super().__init__(location)
        self.callee = callee
        self.arguments = arguments


class ASTIndexOrGenericExpr(ASTExpr):
    def __init__(self, obj: ASTNameExpr, index_or_arg: ASTMaybeExpr, loc: Location):
        super().__init__(loc)
        self.obj = obj
        self.index_or_arg = index_or_arg


class ASTIndexExpr(ASTExpr):
    def __init__(self, obj: ASTExpr, index: ASTExpr, loc: Location):
        super().__init__(loc)
        self.obj = obj
        self.index = index


class ASTGenericExpr(ASTExpr):
    def __init__(self, generic: ASTNameExpr, arguments: list[ASTType], loc: Location):
        super().__init__(loc)
        self.generic = generic
        self.arguments = arguments


class ASTAttrExpr(ASTExpr):
    def __init__(self, object: ASTExpr, attr: Token, location: Location):
        super().__init__(location)
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


class ASTNameExpr(ASTExpr):
    def __init__(self, name: str, ns: ASTNamespace | None, loc: Location):
        super().__init__(loc)
        self.ident = name
        self.ns = ns


class ASTGenericAttrExpr(ASTExpr):
    def __init__(self, generic: ASTGenericType, name: str, loc: Location):
        super().__init__(loc)
        self.generic = generic
        self.name = name


class ASTType(ASTMaybeExpr):
    @staticmethod
    def is_certain():
        return True

    def as_type(self) -> ASTType:
        return self


class ASTGenericType(ASTType):
    def __init__(self, generic: ASTNameType, type_arguments: list[ASTType], loc: Location):
        super().__init__(loc)
        self.generic = generic
        self.type_arguments = type_arguments


class ASTNameType(ASTType):
    def __init__(self, name: str, ns: ASTNamespace | None, loc: Location):
        super().__init__(loc)
        self.name: str = name
        self.ns = ns


class ASTFunctionType(ASTType):
    def __init__(self, parameters: list[ASTType], ret_type: ASTType, loc: Location):
        super().__init__(loc)
        self.parameters = parameters
        self.ret_type = ret_type


class ASTUnitType(ASTType):
    def __init__(self, loc: Location):
        super().__init__(loc)


class ASTNamespace(ASTMaybeExpr):
    def __init__(self, name: str, ns: ASTNamespace, loc: Location):
        super().__init__(loc)
        self.name = name
        self.ns = ns

    @staticmethod
    def is_certain() -> bool:
        return True

    def as_namespace(self) -> ASTNamespace:
        return self
