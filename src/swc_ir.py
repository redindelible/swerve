from __future__ import annotations

from typing import Callable
from dataclasses import dataclass, field

from .common import Location, BuiltinLocation, NamedTuple, UniqueList, CompilerMessage, ErrorType



__all__ = ['IRNode', 'IRValue', 'IRTypeVarType', 'IRType', 'IRBlock', 'IRValueDecl', 'IRIntegerType', "IRFunctionType",
           'IRParameter', 'IRFunction', 'IRTypeDecl', 'IRNameExpr', "IRResolvedType", 'IRTypeVariable', 'IRIndexExpr',
           'IRUnresolvedUnknownType', 'IRExpr', 'IRStruct', 'IRStructType', 'IRUnresolvedGenericType', 'IRMethod',
           'IRUnitType', 'IRUnresolvedNameType', 'IRProgram', 'IRMethodCallExpr', 'IRField', 'IRAttrExpr', 'IRExprStmt',
           'IRWhileStmt', 'IRDeclStmt', 'IRUnresolvedFunctionType', 'IRNotExpr', 'IRNegExpr', 'IRLambda', 'IRAttrAssign',
           'IRAssign', 'IRIf', 'IRBoolType', 'IRIntegerExpr', 'IRGenericExpr', 'IRReturnStmt', 'IRCallExpr', 'IRBinaryExpr',
           'IRStmt', 'IRUnresolvedType', 'ArrayVariant', 'IRTrait', 'IRTraitType', "Namespace", "IRGenericOrIndexExpr",
           'IRGenericAttrExpr']


def check_name(name: str) -> bool:
    if len(name) == 0:
        return False
    if not (name[0] == "_" or name[0].isalpha()):
        return False
    if not all(c == "_" or c.isalnum() for c in name[1:]):
        return False
    return True


def validate_name(name: str, loc: Location):
    if not check_name(name):
        raise CompilerMessage(ErrorType.COMPILATION, f"'{name}' is not a valid name", loc)


class Namespace:
    def __init__(self, *, is_lambda: bool = False):
        self.value_names: dict[str, IRValueDecl] = {}
        self.type_names: dict[str, IRTypeDecl] = {}
        self.namespace_names: dict[str, Namespace] = {}

        self.is_lambda = is_lambda
        self.exterior_names: list[IRValueDecl] = []

        self.not_yet_imported: set[str] = set()

    def declare_namespace(self, name: str, namespace: Namespace, loc: Location) -> Namespace:
        validate_name(name, loc)
        if self.has_namespace(name):
            raise CompilerMessage(ErrorType.COMPILATION, f"Name '{name}' is already used as a namespace in this scope", loc)
        self.namespace_names[name] = namespace
        return namespace

    def has_namespace(self, name: str) -> bool:
        return name in self.namespace_names

    def get_namespace(self, name: str, loc: Location) -> Namespace:
        if self.has_namespace(name):
            return self.namespace_names[name]
        else:
            raise CompilerMessage(ErrorType.COMPILATION, f"Name '{name}' does not exist for a namespace in this scope", loc)

    def has_value(self, name: str) -> bool:
        return name in self.value_names

    def declare_value(self, name: str, decl: IRValueDecl) -> IRValueDecl:
        validate_name(name, decl.location)
        if self.has_value(name):
            raise CompilerMessage(ErrorType.COMPILATION, f"Name '{name}' is already used as a value in this scope", decl.location,
                                  [CompilerMessage(ErrorType.NOTE, "Previously declared here", self.get_value(name, decl.location).location)])
        self.value_names[name] = decl
        return decl

    def get_value(self, name: str, loc: Location) -> IRValueDecl:
        if self.has_value(name):
            return self.value_names[name]
        else:
            raise CompilerMessage(ErrorType.COMPILATION, f"Name '{name}' does not exist for a value in this scope", loc)

    def has_type(self, name: str) -> bool:
        return name in self.type_names

    def declare_type(self, name: str, decl: IRTypeDecl) -> IRTypeDecl:
        validate_name(name, decl.location)
        if self.has_type(name):
            raise CompilerMessage(ErrorType.COMPILATION, f"Name '{name}' is already used as a type in this scope", decl.location,
                                  [CompilerMessage(ErrorType.NOTE, "Previously declared here", self.get_type(name, decl.location).location)])
        self.type_names[name] = decl
        return decl

    def get_type(self, name: str, loc: Location) -> IRTypeDecl:
        if self.has_type(name):
            return self.type_names[name]
        else:
            raise CompilerMessage(ErrorType.COMPILATION, f"Name '{name}' does not exist for a type in this scope", loc)



@dataclass()
class IRNode:
    loc: Location = field(init=False, repr=False)

    def __post_init__(self):
        self.loc = BuiltinLocation()

    def set_loc(self, loc: Location):
        self.loc = loc
        return self


class IRValue(NamedTuple):
    type: IRResolvedType
    value: IRValueDecl | None


@dataclass()
class IRValueDecl:
    type: IRType
    location: Location
    is_runtime: bool

    declarer: IRNode | None = None
    put_in_closure: bool = False
    closure_index: int = 0
    in_block: IRBlock | None = None

    def __hash__(self):
        return id(self)


class IRTypeDecl:
    def __init__(self, type: IRType, location: Location):
        self.type = type
        self.location = location


@dataclass()
class IRType:
    loc: Location = field(init=False, repr=False)

    def __post_init__(self):
        self.loc = BuiltinLocation()

    def set_loc(self, loc: Location):
        self.loc = loc
        return self

    def is_resolved(self) -> bool:
        raise NotImplementedError()

    def __str__(self):
        raise NotImplementedError()


@dataclass()
class IRUnresolvedType(IRType):
    def is_resolved(self) -> bool:
        return False

    def __str__(self):
        raise NotImplementedError()


@dataclass()
class IRUnresolvedUnknownType(IRUnresolvedType):
    def __str__(self):
        return "a type"


@dataclass()
class IRUnresolvedNameType(IRUnresolvedType):
    decl: IRTypeDecl

    def __str__(self):
        return "an unresolved name type"


@dataclass()
class IRUnresolvedFunctionType(IRUnresolvedType):
    parameters: list[IRType]
    ret_type: IRType

    def __str__(self):
        return f"({', '.join(str(param) for param in self.parameters)}) -> {self.ret_type}"


@dataclass()
class IRUnresolvedGenericType(IRUnresolvedType):
    generic: IRType
    type_args: list[IRType]

    def __str__(self):
        return "an unresolved generic type"


@dataclass()
class IRResolvedType(IRType):
    def is_resolved(self) -> bool:
        return True

    def is_subtype(self, bound: IRResolvedType) -> bool:
        raise NotImplementedError()

    def is_concrete(self) -> bool:
        return len(self.get_type_vars()) == 0

    def get_type_vars(self) -> set[IRTypeVarType]:
        raise NotImplementedError()

    def __str__(self):
        raise NotImplementedError()

    def __repr__(self):
        return str(self)

    def __eq__(self, other: IRResolvedType):
        raise NotImplementedError()

    def __hash__(self):
        raise NotImplementedError()


@dataclass()
class IRFunctionType(IRResolvedType):
    param_types: list[IRResolvedType]
    ret_type: IRResolvedType

    # callback: Callable[[dict[IRTypeVarType, IRResolvedType], Location], tuple[IRFunctionType, IRExpr]]

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

    def get_type_vars(self) -> set[IRTypeVarType]:
        type_vars = self.ret_type.get_type_vars()
        for param_type in self.param_types:
            type_vars |= param_type.get_type_vars()
        return type_vars

    def __str__(self):
        return f"({', '.join(str(param) for param in self.param_types)}) -> {self.ret_type}"

    def __eq__(self, other: IRFunctionType):
        return type(other) == IRFunctionType and self.param_types == other.param_types and self.ret_type == other.ret_type

    def __hash__(self):
        return hash((tuple(self.param_types), self.ret_type))


@dataclass()
class IRStructType(IRResolvedType):
    struct: IRStruct

    def is_subtype(self, bound: IRResolvedType) -> bool:
        return self is bound or bound in self.struct.supertraits

    def get_type_vars(self) -> set[IRTypeVarType]:
        return set(self.struct.get_type_vars())

    def __str__(self):
        return f"struct '{self.struct.name}'"

    def __eq__(self, other: IRStructType):
        return type(other) == IRStructType and other.struct is self.struct

    def __hash__(self):
        return hash(self.struct)


@dataclass()
class IRTraitType(IRResolvedType):
    trait: IRTrait

    def is_subtype(self, bound: IRResolvedType) -> bool:
        return self is bound

    def get_type_vars(self) -> set[IRTypeVarType]:
        return set(self.trait.get_type_vars())

    def __str__(self):
        return f"trait '{self.trait.name}'"

    def __eq__(self, other: IRTraitType):
        return type(other) == IRTraitType and other.trait is self.trait

    def __hash__(self):
        return hash(self.trait)


@dataclass()
class IRIntegerType(IRResolvedType):
    bits: int

    def is_subtype(self, bound: IRResolvedType) -> bool:
        return isinstance(bound, IRIntegerType)

    def get_type_vars(self) -> set[IRTypeVariable]:
        return set()

    def __str__(self):
        if self.bits == 64:
            return "int"
        else:
            return f"i{self.bits}"

    def __eq__(self, other: IRIntegerType):
        return type(other) == IRIntegerType and self.bits == other.bits

    def __hash__(self):
        return hash((type(self), self.bits))


@dataclass()
class IRBoolType(IRResolvedType):
    def is_subtype(self, bound: IRResolvedType) -> bool:
        return isinstance(bound, IRBoolType)

    def get_type_vars(self) -> set[IRTypeVariable]:
        return set()

    def __str__(self):
        return "bool"

    def __eq__(self, other: IRBoolType):
        return type(other) == IRBoolType

    def __hash__(self):
        return hash(type(self))


@dataclass()
class IRUnitType(IRResolvedType):
    def is_subtype(self, bound: IRResolvedType) -> bool:
        return isinstance(bound, IRUnitType)

    def get_type_vars(self) -> set[IRTypeVariable]:
        return set()

    def __str__(self):
        return "unit"

    def __eq__(self, other: IRUnitType):
        return type(other) == IRUnitType

    def __hash__(self):
        return hash(type(self))


@dataclass()
class IRTypeVarType(IRResolvedType):
    type_var: IRTypeVariable

    def is_subtype(self, bound: IRResolvedType) -> bool:
        return self is bound

    def get_type_vars(self) -> set[IRTypeVarType]:
        return {self}

    def __str__(self):
        return f"{self.type_var.name}"

    def __eq__(self, other: IRTypeVarType):
        return type(other) == IRTypeVarType and self.type_var is other.type_var

    def __hash__(self):
        return hash(self.type_var)


class ArrayVariant(NamedTuple):
    type: IRResolvedType
    array: IRStruct
    constructor: IRValueDecl
    get: IRValueDecl
    set: IRValueDecl


class IRProgram:
    def __init__(self, functions: list[IRFunction], structs: list[IRStruct], traits: list[IRTrait]):
        self.functions = functions
        self.structs = structs
        self.traits = traits

        self.main_func: IRFunction | None = None

        self.array_decl: IRTypeDecl | None = None
        self.array_constructor_decl: IRValueDecl | None = None
        self.array_variants: dict[IRResolvedType, ArrayVariant] = {}
        self.array_reifications: dict[tuple[IRResolvedType], IRStruct] = {}


@dataclass(repr=False)
class IRStruct(IRNode):
    type_decl: IRTypeDecl
    constructor: IRValueDecl
    base_name: str
    supertraits: list[IRType]
    fields: list[IRField]
    methods: list[IRMethod]

    type_args: tuple[IRResolvedType, ...]
    reifications: dict[tuple[IRResolvedType], IRStruct]
    substitute: Callable[[dict[IRTypeVarType, IRResolvedType], Location], IRStruct] | None

    @property
    def name(self) -> str:
        if self.type_args:
            return f"{self.base_name}[{', '.join(str(arg) for arg in self.type_args)}]"
        else:
            return f"{self.base_name}"

    def get_type_vars(self) -> tuple[IRTypeVarType]:
        type_vars: UniqueList[IRTypeVarType] = UniqueList([])
        for arg in self.type_args:
            type_vars.extend(arg.get_type_vars())
        return tuple(type_vars)

    def has_field(self, name: str) -> int | None:
        for i, field in enumerate(self.fields):
            if field.name == name:
                return i
        else:
            return None

    def has_method(self, name: str) -> int | None:
        for i, method in enumerate(self.methods):
            if method.name == name:
                return i
        else:
            return None

    def __hash__(self):
        return id(self)


@dataclass(repr=False)
class IRTrait(IRNode):
    type_decl: IRTypeDecl
    base_name: str
    methods: list[IRMethod]

    type_args: tuple[IRResolvedType, ...]
    reifications: dict[tuple[IRResolvedType], IRTrait]
    substitute: Callable[[dict[IRTypeVarType, IRResolvedType], Location], IRTrait] | None

    @property
    def name(self) -> str:
        if self.type_args:
            return f"{self.base_name}[{', '.join(str(arg) for arg in self.type_args)}]"
        else:
            return f"{self.base_name}"

    def get_virtual_methods(self) -> list[IRMethod]:
        return [method for method in self.methods if method.is_virtual]

    def get_type_vars(self) -> tuple[IRTypeVarType]:
        type_vars: UniqueList[IRTypeVarType] = UniqueList([])
        for arg in self.type_args:
            type_vars.extend(arg.get_type_vars())
        return tuple(type_vars)

    def has_method(self, name: str) -> int | None:
        for i, method in enumerate(self.methods):
            if method.name == name:
                return i
        else:
            return None

    def __hash__(self):
        return id(self)


@dataclass()
class IRField(IRNode):
    name: str
    type: IRType


@dataclass()
class IRMethod(IRNode):
    name: str
    is_virtual: bool
    is_static: bool
    is_self: bool
    function: IRFunction


@dataclass()
class IRTypeVariable(IRNode):
    name: str
    bound: IRType | None
    type_decl: IRTypeDecl

    def __hash__(self):
        return id(self)


@dataclass()
class IRFunction(IRNode):
    decl: IRValueDecl
    name: str
    type_args: tuple[IRResolvedType, ...]
    parameters: list[IRParameter]
    return_type: IRType
    body: IRBlock

    is_extern: bool
    is_builtin: bool
    callback: Callable[[dict[IRTypeVarType, IRResolvedType], Location], IRValue] | None
    reifications: dict[tuple[IRResolvedType], IRFunction] = field(default_factory=dict)

    def __post_init__(self):
        super().__post_init__()
        self.decl.declarer = self

    def get_type_vars(self) -> tuple[IRTypeVarType]:
        type_vars: UniqueList[IRTypeVarType] = UniqueList([])
        for arg in self.type_args:
            type_vars.extend(arg.get_type_vars())
        return tuple(type_vars)

    @property
    def function_type(self):
        # noinspection PyTypeChecker
        return IRFunctionType([param.type for param in self.parameters], self.return_type)

    def __hash__(self):
        return id(self)


@dataclass()
class IRParameter(IRNode):
    decl: IRValueDecl
    name: str
    type: IRType


@dataclass()
class IRStmt(IRNode):
    # noinspection PyMethodMayBeStatic
    def always_returns(self) -> bool:
        return False


@dataclass()
class IRExprStmt(IRStmt):
    expr: IRExpr

    def always_returns(self) -> bool:
        return self.expr.always_returns()


@dataclass()
class IRDeclStmt(IRStmt):
    decl: IRValueDecl
    type: IRType
    init: IRExpr


@dataclass()
class IRWhileStmt(IRStmt):
    cond: IRExpr
    body: IRExpr


# @dataclass()
# class IRForStmt(IRStmt):
#     iter_var: IRValueDecl
#     iterator: IRExpr
#     body: IRExpr


@dataclass()
class IRReturnStmt(IRStmt):
    expr: IRExpr

    def always_returns(self) -> bool:
        return True


@dataclass()
class IRExpr(IRNode):
    yield_type: IRResolvedType | None = field(init=False, default=None)
    cast: IRResolvedType | None = field(init=False, default=None)

    # noinspection PyMethodMayBeStatic
    def always_returns(self) -> bool:
        return False


@dataclass()
class IRBlock(IRExpr):
    body: list[IRStmt]
    declared: list[IRValueDecl]
    return_unit: bool

    def __post_init__(self):
        super().__post_init__()
        for decl in self.declared:
            decl.in_block = True

    def always_returns(self) -> bool:
        if len(self.body) == 0:
            return False
        return self.body[-1].always_returns()


@dataclass()
class IRIf(IRExpr):
    cond: IRExpr
    then_do: IRExpr
    else_do: IRExpr | None

    def always_returns(self) -> bool:
        if self.else_do:
            return self.then_do.always_returns() and self.else_do.always_returns()
        return False


@dataclass()
class IRAssign(IRExpr):
    name: IRValueDecl
    op: str
    value: IRExpr


@dataclass()
class IRAttrAssign(IRExpr):
    obj: IRExpr
    attr: str
    op: str
    value: IRExpr
    index: int | None = None


@dataclass()
class IRLambda(IRExpr):
    exterior_names: list[IRValueDecl]
    parameters: list[IRParameter]
    ret_type: IRType
    body: IRBlock


@dataclass()
class IRBinaryExpr(IRExpr):
    op: str
    left: IRExpr
    right: IRExpr


@dataclass()
class IRNegExpr(IRExpr):
    right: IRExpr


@dataclass()
class IRNotExpr(IRExpr):
    right: IRExpr


@dataclass()
class IRCallExpr(IRExpr):
    callee: IRExpr
    arguments: list[IRExpr]

    as_method_call: IRMethodCallExpr | None = field(init=False, default=None)


@dataclass()
class IRMethodCallExpr(IRExpr):
    obj: IRExpr
    from_type: IRStructType | IRTraitType
    method: IRMethod
    arguments: list[IRExpr]


@dataclass()
class IRIndexExpr(IRExpr):
    obj: IRExpr
    argument: IRExpr


@dataclass()
class IRGenericExpr(IRExpr):
    generic: IRNameExpr
    arguments: list[IRType]

    replacement_expr: IRExpr | None = field(init=False, default=None)


@dataclass()
class IRGenericOrIndexExpr(IRExpr):
    obj: IRNameExpr
    argument_as_type: IRType
    argument_as_expr: IRExpr

    as_generic: IRGenericExpr | None = field(init=False, default=None)
    as_index: IRIndexExpr | None = field(init=False, default=None)


@dataclass()
class IRGenericAttrExpr(IRExpr):
    generic: IRType
    name: str

    resolved: IRValueDecl | None = field(init=False, default=None)


@dataclass()
class IRAttrExpr(IRExpr):
    object: IRExpr
    attr: str

    index: int | None = field(init=False, default=None)


@dataclass()
class IRIntegerExpr(IRExpr):
    number: int


# @dataclass()
# class IRStringExpr(IRExpr):
#     def __init__(self, string: str):
#         super().__init__()
#         self.string = string


@dataclass()
class IRNameExpr(IRExpr):
    name: IRValueDecl
