from __future__ import annotations

from src.common import Location
from src.token import Token


# __all__ = []


class IRNode:
    pass


class IRValueDecl:
    def __init__(self, type: IRType | None, location: Location):
        self.type = type
        self.location = location


class IRTypeDecl:
    def __init__(self, type: IRType | None, location: Location):
        self.type = type
        self.location = location


class IRProgram:
    def __init__(self, functions: list[IRFunction], structs: list[IRStruct]):
        self.functions = functions
        self.structs = structs


class IRStruct(IRNode):
    def __init__(self, decl: IRTypeDecl, name: str, type_vars: list[IRType], supertraits: list[IRTypeDecl],
                 fields: list[IRField], methods: list[IRStructFunction]):
        self.decl = decl
        self.name = name
        self.type_vars = type_vars
        self.supertraits = supertraits
        self.fields = fields
        self.methods = methods


class IRTypeVariable(IRNode):
    def __init__(self, name: str, bound: IRType | None):
        self.name = name
        self.bound = bound


class IRField(IRNode):
    def __init__(self, name: str, type: IRType):
        self.name = name
        self.type = type


class IRStructFunction(IRNode):
    pass


class IRStaticFunction(IRStructFunction):
    def __init__(self, decl: IRValueDecl, name: str, parameters: list[IRParameter], return_type: IRType, body: IRBlock):
        self.decl = decl
        self.name = name
        self.parameters = parameters
        self.return_type = return_type
        self.body = body


class IRStaticMethod(IRStructFunction):
    def __init__(self, decl: IRValueDecl, name: str, self_name: str, parameters: list[IRParameter], return_type: IRType, body: IRBlock):
        self.decl = decl
        self.name = name
        self.parameters = parameters
        self.return_type = return_type
        self.body = body


class IRDynamicFunction(IRStructFunction):
    def __init__(self, decl: IRValueDecl, name: str, parameters: list[IRParameter], return_type: IRType, body: IRBlock):
        self.decl = decl
        self.name = name
        self.parameters = parameters
        self.return_type = return_type
        self.body = body


class IRDynamicMethod(IRStructFunction):
    def __init__(self, decl: IRValueDecl, name: str, self_name: str, parameters: list[IRParameter], return_type: IRType, body: IRBlock):
        self.decl = decl
        self.name = name
        self.parameters = parameters
        self.return_type = return_type
        self.body = body


class IRFunction(IRNode):
    def __init__(self, decl: IRValueDecl, name: str, parameters: list[IRParameter], return_type: IRType, body: IRBlock):
        self.decl = decl
        self.name = name
        self.parameters = parameters
        self.return_type = return_type
        self.body = body


class IRParameter(IRNode):
    def __init__(self, decl: IRValueDecl, name: Token, type: IRType):
        self.decl = decl
        self.name: str = name.text
        self.type = type


class IROp(IRNode):
    pass


class IRBlock(IRNode):
    def __init__(self, body: IROp):
        self.body = body


class IRReturnExpr(IROp):
    def __init__(self, expr: IROp):
        self.expr = expr


class IRAssign(IROp):
    def __init__(self, name: IRValueDecl, value: IROp):
        self.name = name
        self.value = value


class IRAddExpr(IROp):
    def __init__(self, left: IROp, right: IROp):
        self.left: IROp = left
        self.right: IROp = right


class IRSubExpr(IROp):
    def __init__(self, left: IROp, right: IROp):
        self.left: IROp = left
        self.right: IROp = right


class IRMulExpr(IROp):
    def __init__(self, left: IROp, right: IROp):
        self.left: IROp = left
        self.right: IROp = right


class IRDivExpr(IROp):
    def __init__(self, left: IROp, right: IROp):
        self.left: IROp = left
        self.right: IROp = right


class IRPowExpr(IROp):
    def __init__(self, left: IROp, right: IROp):
        self.left: IROp = left
        self.right: IROp = right


class IROrExpr(IROp):
    def __init__(self, left: IROp, right: IROp):
        self.left: IROp = left
        self.right: IROp = right


class IRAndExpr(IROp):
    def __init__(self, left: IROp, right: IROp):
        self.left: IROp = left
        self.right: IROp = right


class IRNegExpr(IROp):
    def __init__(self, token: Token, right: IROp):
        self.right = right


class IRNotExpr(IROp):
    def __init__(self, token: Token, right: IROp):
        self.right = right


class IRCallExpr(IROp):
    def __init__(self, callee: IROp, arguments: list[IROp], end: Token):
        self.callee = callee
        self.arguments = arguments


class IRAttrExpr(IROp):
    def __init__(self, object: IROp, attr: Token):
        self.object = object
        self.attr: str = attr.text


class IRIntegerExpr(IROp):
    def __init__(self, number: int):
        self.number = number


class IRStringExpr(IROp):
    def __init__(self, string: str):
        self.string = string


class IRType(IRNode):
    pass


class IRTypeIdent(IRType):
    def __init__(self, ident: Token):
        super().__init__(ident.location)
        self.ident = ident
