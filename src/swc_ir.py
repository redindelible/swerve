from __future__ import annotations

from common import Location


# __all__ = []


class IRNode:
    pass


class IRValueDecl:
    def __init__(self, type: IRType, location: Location):
        self.type = type
        self.location = location


class IRTypeDecl:
    def __init__(self, type: IRType, location: Location):
        self.type = type
        self.location = location


class IRType:
    def is_resolved(self) -> bool:
        raise NotImplementedError()


class IRUnresolvedType(IRType):
    def is_resolved(self) -> bool:
        return False


class IRUnresolvedUnknownType(IRUnresolvedType):
    pass


class IRUnresolvedNameType(IRUnresolvedType):
    def __init__(self, decl: IRTypeDecl):
        self.decl = decl


class IRResolvedType(IRType):
    def is_resolved(self) -> bool:
        return True

    def is_subtype(self, bound: IRResolvedType) -> bool:
        raise NotImplementedError()

    def is_concrete(self) -> bool:
        raise NotImplementedError()


class IRFunctionType(IRResolvedType):
    def __init__(self, param_types: list[IRResolvedType], ret_type: IRResolvedType):
        self.param_types = param_types
        self.ret_type = ret_type

    def is_subtype(self, bound: IRResolvedType) -> bool:
        if not isinstance(bound, IRFunctionType):
            return False

        if len(bound.param_types) != len(self.param_types):
            return False

        for this_type, bound_type in zip(self.param_types, bound.param_types):
            if not bound_type.is_subtype(this_type):   # parameters are contravariant
                return False

        if not self.ret_type.is_subtype(bound.ret_type):
            return False

        return True

    def is_concrete(self) -> bool:
        return all(param_type.is_resolved() for param_type in self.param_types) and self.ret_type.is_resolved()


class IRStructType(IRResolvedType):
    def __init__(self, struct: IRStruct):
        self.struct = struct

    def is_subtype(self, bound: IRResolvedType) -> bool:
        return self is bound

    def is_concrete(self) -> bool:
        return True


class IRGenericType(IRResolvedType):
    def __init__(self, generic: IRGenericStruct, type_parameters: list[IRResolvedType]):
        self.generic = generic
        self.type_parameters = type_parameters

    def is_subtype(self, bound: IRResolvedType) -> bool:
        # TODO this is just wrong
        return self is bound

    def is_concrete(self) -> bool:
        return False


class IRIntegerType(IRResolvedType):
    def __init__(self, bits: int):
        self.bits = bits

    def is_subtype(self, bound: IRResolvedType) -> bool:
        return isinstance(bound, IRIntegerType)

    def is_concrete(self) -> bool:
        return True


class IRStringType(IRResolvedType):
    def is_subtype(self, bound: IRResolvedType) -> bool:
        return isinstance(bound, IRStringType)

    def is_concrete(self) -> bool:
        return True


class IRTypeVarType(IRResolvedType):
    def __init__(self, type_var: IRTypeVariable):
        self.type_var = type_var

    def is_subtype(self, bound: IRResolvedType) -> bool:
        return self is bound

    def is_concrete(self) -> bool:
        return False


class IRProgram:
    def __init__(self, functions: list[IRFunction], structs: list[IRStruct], generic_structs: list[IRGenericStruct]):
        self.functions = functions
        self.structs = structs
        self.generic_structs = generic_structs


class IRStruct:
    def __init__(self, type_decl: IRTypeDecl, constructor: IRValueDecl, name: str, supertraits: list[IRType], fields: dict[str, IRType], methods: list[IRMethod]):
        self.type_decl = type_decl
        self.constructor = constructor
        self.name = name
        self.supertraits = supertraits
        self.methods = methods
        self.fields = fields


class IRGenericStruct:
    def __init__(self, type_decl: IRTypeDecl, constructor: IRValueDecl, name: str, type_vars: list[IRTypeVariable], supertraits: list[IRType],
                 fields: dict[str, IRType], methods: list[IRMethod], generic_methods: list[IRGenericMethod]):
        self.type_decl = type_decl
        self.constructor = constructor
        self.name = name
        self.type_vars = type_vars
        self.supertraits = supertraits
        self.methods = methods
        self.fields = fields


class IRMethod:
    def __init__(self, name: str, is_static: bool, is_self: bool, function: IRFunction):
        self.name = name
        self.is_static = is_static
        self.is_self = is_self
        self.function = function


class IRGenericMethod:
    def __init__(self, name: str, is_static: bool, is_self: bool, type_vars: list[IRTypeVariable], parameters: list[IRParameter], return_type: IRType, body: IRBlock):
        self.name = name
        self.is_static = is_static
        self.is_self = is_self


class IRTypeVariable(IRNode):
    def __init__(self, name: str, bound: IRType | None):
        self.name = name
        self.bound = bound


class IRField(IRNode):
    def __init__(self, name: str, type: IRType):
        self.name = name
        self.type = type


class IRFunction(IRNode):
    def __init__(self, decl: IRValueDecl, name: str, parameters: list[IRParameter], return_type: IRType, body: IRBlock):
        self.decl = decl
        self.name = name
        self.parameters = parameters
        self.return_type = return_type
        self.body = body

        self.function_type: IRFunctionType | None = None


class IRParameter(IRNode):
    def __init__(self, decl: IRValueDecl, name: str, type: IRType):
        self.decl = decl
        self.name = name
        self.type = type


class IRStmt(IRNode):
    pass


class IRExprStmt(IRStmt):
    def __init__(self, expr: IRExpr):
        self.expr = expr


class IRDeclStmt(IRStmt):
    def __init__(self, decl: IRValueDecl, type: IRType, init: IRExpr):
        self.decl = decl
        self.type = type
        self.init = init


class IRWhileStmt(IRStmt):
    def __init__(self, cond: IRExpr, body: IRExpr):
        self.cond = cond
        self.body = body


class IRForStmt(IRStmt):
    def __init__(self, iter_var: IRValueDecl, iterator: IRExpr, body: IRExpr):
        self.iter_var = iter_var
        self.iterator = iterator
        self.body = body


class IRReturnStmt(IRStmt):
    def __init__(self, expr: IRExpr):
        self.expr = expr


class IRExpr(IRNode):
    def __init__(self):
        self.yield_type: IRResolvedType | None = None


class IRBlock(IRExpr):
    def __init__(self, body: list[IRStmt]):
        super().__init__()
        self.body = body


class IRIf(IRExpr):
    def __init__(self, cond: IRExpr, then_do: IRExpr, else_do: IRExpr | None):
        super().__init__()
        self.cond = cond
        self.then_do = then_do
        self.else_do = else_do


class IRAssign(IRExpr):
    def __init__(self, name: IRValueDecl, value: IRExpr):
        super().__init__()
        self.name = name
        self.value = value


class IRBinaryExpr(IRExpr):
    def __init__(self, op: str, left: IRExpr, right: IRExpr):
        super().__init__()
        self.op = op
        self.left = left
        self.right = right


class IRNegExpr(IRExpr):
    def __init__(self, right: IRExpr):
        super().__init__()
        self.right = right


class IRNotExpr(IRExpr):
    def __init__(self, right: IRExpr):
        super().__init__()
        self.right = right


class IRCallExpr(IRExpr):
    def __init__(self, callee: IRExpr, arguments: list[IRExpr]):
        super().__init__()
        self.callee = callee
        self.arguments = arguments


class IRAttrExpr(IRExpr):
    def __init__(self, object: IRExpr, attr: str):
        super().__init__()
        self.object = object
        self.attr = attr

        self.index: int | None = None


class IRIntegerExpr(IRExpr):
    def __init__(self, number: int):
        super().__init__()
        self.number = number


class IRStringExpr(IRExpr):
    def __init__(self, string: str):
        super().__init__()
        self.string = string


class IRNameExpr(IRExpr):
    def __init__(self, name: IRValueDecl):
        super().__init__()
        self.name = name


# class IRTypeRef(IRNode):
#     pass
#
#
# class IRTypeRefName(IRTypeRef):
#     def __init__(self, decl: IRTypeDecl):
#         self.decl = decl
