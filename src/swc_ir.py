from __future__ import annotations

from typing import Callable
from common import Location, BuiltinLocation


# __all__ = []


class IRNode:
    def __init__(self):
        self.loc: Location = BuiltinLocation()

    def set_loc(self, loc: Location):
        self.loc = loc
        return self


class IRValueDecl:
    def __init__(self, type: IRType, location: Location):
        self.type = type
        self.location = location


class IRTypeDecl:
    def __init__(self, type: IRType, location: Location):
        self.type = type
        self.location = location


class IRType:
    def __init__(self):
        self.loc: Location = BuiltinLocation()

    def set_loc(self, loc: Location):
        self.loc = loc
        return self

    def is_resolved(self) -> bool:
        raise NotImplementedError()

    def __str__(self):
        raise NotImplementedError()


class IRUnresolvedType(IRType):
    def is_resolved(self) -> bool:
        return False

    def __str__(self):
        raise NotImplementedError()


class IRUnresolvedUnknownType(IRUnresolvedType):
    def __str__(self):
        return "a type"


class IRUnresolvedNameType(IRUnresolvedType):
    def __init__(self, decl: IRTypeDecl):
        super().__init__()
        self.decl = decl
        self.set_loc(self.loc)

    def __str__(self):
        return "an unresolved name type"


class IRUnresolvedGenericType(IRUnresolvedType):
    def __init__(self, generic: IRType, type_args: list[IRType]):
        super().__init__()
        self.generic = generic
        self.type_args = type_args

    def __str__(self):
        return "an unresolved generic type"


class IRResolvedType(IRType):
    def is_resolved(self) -> bool:
        return True

    def is_subtype(self, bound: IRResolvedType) -> bool:
        raise NotImplementedError()

    def is_concrete(self) -> bool:
        raise NotImplementedError()

    def __str__(self):
        raise NotImplementedError()


class IRFunctionType(IRResolvedType):
    def __init__(self, param_types: list[tuple[IRResolvedType, Location]], ret_type: IRResolvedType):
        super().__init__()
        self.param_types = param_types
        self.ret_type = ret_type

    def is_subtype(self, bound: IRResolvedType) -> bool:
        if not isinstance(bound, IRFunctionType):
            return False

        if len(bound.param_types) != len(self.param_types):
            return False

        for (this_type, _), (bound_type, _) in zip(self.param_types, bound.param_types):
            if not bound_type.is_subtype(this_type):   # parameters are contravariant
                return False

        if not self.ret_type.is_subtype(bound.ret_type):
            return False

        return True

    def is_concrete(self) -> bool:
        return all(param_type.is_resolved() for param_type, _ in self.param_types) and self.ret_type.is_resolved()

    def __str__(self):
        return f"({', '.join(str(param) for param in self.param_types)}) -> {self.ret_type}"


class IRGenericFunctionType(IRFunctionType):
    def __init__(self, type_vars: list[IRTypeVariable], param_types: list[tuple[IRResolvedType, Location]], ret_type: IRResolvedType,
                 callback: Callable[[list[IRResolvedType], Location], tuple[IRFunctionType, IRExpr]]):
        super().__init__(param_types, ret_type)
        self.type_vars = type_vars

        self.callback = callback

    def is_subtype(self, bound: IRResolvedType) -> bool:
        # TODO
        # I don't want to think about this
        return False

    def is_concrete(self) -> bool:
        return False


class IRStructType(IRResolvedType):
    def __init__(self, struct: IRStruct):
        super().__init__()
        self.struct = struct

    def is_subtype(self, bound: IRResolvedType) -> bool:
        return self is bound

    def is_concrete(self) -> bool:
        return True

    def __str__(self):
        return f"struct '{self.struct.name}'"


class IRGenericStructType(IRResolvedType):
    def __init__(self, generic: IRGenericStruct):
        super().__init__()
        self.generic = generic

    def is_subtype(self, bound: IRResolvedType) -> bool:
        return self is bound

    def is_concrete(self) -> bool:
        return False

    def __str__(self):
        return f"struct '{self.generic.name}'"


class IRGenericType(IRResolvedType):
    def __init__(self, generic: IRGenericStruct, type_parameters: list[IRResolvedType]):
        super().__init__()
        self.generic = generic
        self.type_parameters = type_parameters

    def is_subtype(self, bound: IRResolvedType) -> bool:
        # TODO this is just wrong
        return self is bound

    def is_concrete(self) -> bool:
        return False

    def __str__(self):
        return f"{self.generic}[{', '.join(str(arg) for arg in self.type_parameters)}]"


class IRIntegerType(IRResolvedType):
    def __init__(self, bits: int):
        super().__init__()
        self.bits = bits

    def is_subtype(self, bound: IRResolvedType) -> bool:
        return isinstance(bound, IRIntegerType)

    def is_concrete(self) -> bool:
        return True

    def __str__(self):
        if self.bits == 64:
            return "int"
        else:
            return f"i{self.bits}"


class IRStringType(IRResolvedType):
    def is_subtype(self, bound: IRResolvedType) -> bool:
        return isinstance(bound, IRStringType)

    def is_concrete(self) -> bool:
        return True

    def __str__(self):
        return "str"


class IRTypeVarType(IRResolvedType):
    def __init__(self, type_var: IRTypeVariable):
        super().__init__()
        self.type_var = type_var

    def is_subtype(self, bound: IRResolvedType) -> bool:
        return self is bound

    def is_concrete(self) -> bool:
        return False

    def __str__(self):
        return self.type_var.name


class IRProgram:
    def __init__(self, functions: list[IRFunction], structs: list[IRStruct]):
        self.functions = functions
        self.structs = structs


class IRStruct(IRNode):
    def __init__(self, type_decl: IRTypeDecl, constructor: IRValueDecl, name: str, supertraits: list[IRType], fields: list[IRField], methods: list[IRMethod]):
        super().__init__()
        self.type_decl = type_decl
        self.constructor = constructor
        self.name = name
        self.supertraits = supertraits
        self.methods = methods
        self.fields = fields


class IRGenericStruct(IRStruct):
    def __init__(self, type_decl: IRTypeDecl, constructor: IRValueDecl, name: str, type_vars: list[IRTypeVariable], supertraits: list[IRType],
                 fields: list[IRField], methods: list[IRMethod], generic_methods: list[IRGenericMethod]):
        super().__init__(type_decl, constructor, name, supertraits, fields, methods)
        self.type_vars = type_vars

        self.reifications: dict[tuple[IRResolvedType], IRStruct] = {}


class IRField(IRNode):
    def __init__(self, name: str, type: IRType):
        super().__init__()
        self.name = name
        self.type = type


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
    def __init__(self, name: str, bound: IRType | None, type_decl: IRTypeDecl):
        super().__init__()
        self.name = name
        self.bound = bound
        self.type_decl = type_decl


class IRFunction(IRNode):
    def __init__(self, decl: IRValueDecl, name: str, parameters: list[IRParameter], return_type: IRType, body: IRBlock):
        super().__init__()
        self.decl = decl
        self.name = name
        self.parameters = parameters
        self.return_type = return_type
        self.body = body

        self.function_type: IRFunctionType | None = None


class IRGenericFunction(IRNode):
    def __init__(self, decl: IRValueDecl, name: str, type_vars: list[IRTypeVariable], parameters: list[IRParameter], return_type: IRType, body: IRBlock):
        super().__init__()
        self.decl = decl
        self.name = name
        self.type_vars = type_vars
        self.parameters = parameters
        self.return_type = return_type
        self.body = body

        self.function_type: IRFunctionType | None = None


class IRParameter(IRNode):
    def __init__(self, decl: IRValueDecl, name: str, type: IRType):
        super().__init__()
        self.decl = decl
        self.name = name
        self.type = type


class IRStmt(IRNode):
    pass


class IRExprStmt(IRStmt):
    def __init__(self, expr: IRExpr):
        super().__init__()
        self.expr = expr


class IRDeclStmt(IRStmt):
    def __init__(self, decl: IRValueDecl, type: IRType, init: IRExpr):
        super().__init__()
        self.decl = decl
        self.type = type
        self.init = init


class IRWhileStmt(IRStmt):
    def __init__(self, cond: IRExpr, body: IRExpr):
        super().__init__()
        self.cond = cond
        self.body = body


class IRForStmt(IRStmt):
    def __init__(self, iter_var: IRValueDecl, iterator: IRExpr, body: IRExpr):
        super().__init__()
        self.iter_var = iter_var
        self.iterator = iterator
        self.body = body


class IRReturnStmt(IRStmt):
    def __init__(self, expr: IRExpr):
        super().__init__()
        self.expr = expr


class IRExpr(IRNode):
    def __init__(self):
        super().__init__()
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


class IRGenericExpr(IRExpr):
    def __init__(self, generic: IRExpr, arguments: list[IRType]):
        super().__init__()
        self.generic = generic
        self.arguments = arguments

        self.replacement_expr: IRExpr | None = None


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
