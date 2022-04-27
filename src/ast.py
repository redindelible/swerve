from __future__ import annotations

from src.common import Location, SourceLocation
from src.token import Token, TokenType


__all__ = ["ASTFunction", "ASTParameter", "ASTStmt", "ASTLetStmt", "ASTVarStmt", "ASTExprStmt", "ASTExpr", "ASTBlockExpr",
    "ASTReturnExpr", "ASTAssign", "ASTAddExpr", "ASTSubExpr", "ASTMulExpr", "ASTDivExpr", "ASTPowExpr", "ASTOrExpr", "ASTAndExpr",
    "ASTNegExpr", "ASTNotExpr", "ASTCallExpr", "ASTAttrExpr", "ASTIntegerExpr", "ASTStringExpr", "ASTGroupExpr", "ASTIdentExpr",
    "ASTType", "ASTTypeIdent", "ASTFile", "ASTNode", "ASTProgram", "ASTTopLevel", "ASTStruct", "ASTTypeVariable", "ASTMethod",
    "ASTStructField"]


class ASTNode:
    def __init__(self, loc: Location):
        self.location = loc


class ASTProgram:
    def __init__(self, files: list[ASTFile]):
        self.files = files


class ASTFile:
    def __init__(self, name: str, top_levels: list[ASTTopLevel]):
        self.name = name
        self.top_levels = top_levels


class ASTTopLevel(ASTNode):
    pass


class ASTFunction(ASTTopLevel):
    def __init__(self, def_token: Token, name: Token, parameters: list[ASTParameter], return_type: ASTType, body: ASTBlockExpr, location: Location):
        super().__init__(location)
        self.name: str = name.text
        self.parameters = parameters
        self.return_type = return_type
        self.body = body


class ASTParameter(ASTNode):
    def __init__(self, name: str, type: ASTType, location: Location):
        super().__init__(location)
        self.name = name
        self.type = type


class ASTStruct(ASTTopLevel):
    def __init__(self, name: Token, type_variables: list[ASTTypeVariable], supertraits: list[ASTType],
                 fields: list[ASTStructField], methods: list[ASTMethod], location: SourceLocation):
        super().__init__(location)
        self.name: str = name.text
        self.type_variables = type_variables
        self.supertraits = supertraits
        self.fields = fields
        self.methods = methods


class ASTStructField(ASTNode):
    def __init__(self, name: Token, type: ASTType, location: Location):
        super().__init__(location)
        self.name: str = name.text
        self.type = type


class ASTMethod(ASTNode):
    def __init__(self, start: Token, name: Token, parameters: list[ASTParameter], is_static: bool, self_name: Token | None, return_type: ASTType, body: ASTBlockExpr, location: Location):
        super().__init__(location)
        self.name: str = name.text
        self.parameters = parameters
        self.is_static = is_static
        self.self_name: str | None = self_name.text if self_name is not None else None
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


class ASTExprStmt(ASTStmt):
    def __init__(self, expr: ASTExpr):
        super().__init__(expr.location)
        self.expr: ASTExpr = expr


class ASTExpr(ASTNode):
    pass


class ASTBlockExpr(ASTExpr):
    def __init__(self, body: list[ASTStmt], location: Location):
        super().__init__(location)
        self.body = body


class ASTReturnExpr(ASTExpr):
    def __init__(self, expr: ASTExpr, location: Location):
        super().__init__(location)
        self.expr = expr


class ASTAssign(ASTExpr):
    def __init__(self, name: ASTIdentExpr, value: ASTExpr, location: Location):
        super().__init__(location)
        self.name: str = name.ident
        self.value = value


class ASTAddExpr(ASTExpr):
    def __init__(self, left: ASTExpr, right: ASTExpr, location: Location):
        super().__init__(location)
        self.left: ASTExpr = left
        self.right: ASTExpr = right


class ASTSubExpr(ASTExpr):
    def __init__(self, left: ASTExpr, right: ASTExpr, location: Location):
        super().__init__(location)
        self.left: ASTExpr = left
        self.right: ASTExpr = right


class ASTMulExpr(ASTExpr):
    def __init__(self, left: ASTExpr, right: ASTExpr, location: Location):
        super().__init__(location)
        self.left: ASTExpr = left
        self.right: ASTExpr = right


class ASTDivExpr(ASTExpr):
    def __init__(self, left: ASTExpr, right: ASTExpr, location: Location):
        super().__init__(location)
        self.left: ASTExpr = left
        self.right: ASTExpr = right


class ASTPowExpr(ASTExpr):
    def __init__(self, left: ASTExpr, right: ASTExpr, location: Location):
        super().__init__(location)
        self.left: ASTExpr = left
        self.right: ASTExpr = right


class ASTOrExpr(ASTExpr):
    def __init__(self, left: ASTExpr, right: ASTExpr, location: Location):
        super().__init__(location)
        self.left: ASTExpr = left
        self.right: ASTExpr = right


class ASTAndExpr(ASTExpr):
    def __init__(self, left: ASTExpr, right: ASTExpr, location: Location):
        super().__init__(location)
        self.left: ASTExpr = left
        self.right: ASTExpr = right


class ASTNegExpr(ASTExpr):
    def __init__(self, token: Token, right: ASTExpr, location: Location):
        super().__init__(location)
        self.right = right


class ASTNotExpr(ASTExpr):
    def __init__(self, token: Token, right: ASTExpr, location: Location):
        super().__init__(location)
        self.right = right


class ASTCallExpr(ASTExpr):
    def __init__(self, callee: ASTExpr, arguments: list[ASTExpr], end: Token, location: Location):
        super().__init__(location)
        self.callee = callee
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


class ASTStringExpr(ASTExpr):
    def __init__(self, string: Token):
        super().__init__(string.location)
        self.string = string.text[1:-1]
        #TODO replace \ things


class ASTGroupExpr(ASTExpr):
    def __init__(self, expr: ASTExpr, location: Location):
        super().__init__(location)
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