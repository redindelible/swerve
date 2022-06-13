from __future__ import annotations

from typing import cast

from .swc_ir import *
from .common import CompilerMessage, ErrorType, Location, ValueStack, NamedTuple


def infer_types(program: IRProgram):
    inferrer = BidirectionalTypeInference(program)
    inferrer.infer_types()


class Return(NamedTuple):
    type: IRResolvedType
    loc: Location


class BidirectionalTypeInference:
    def __init__(self, program: IRProgram):
        self.program = program

        self.expected_return: ValueStack[Return] = ValueStack()

        self.substitutions: ValueStack[dict[IRTypeVarType, IRResolvedType]] = ValueStack(initial={})

    def resolve_generic_struct(self, generic: IRStruct, arguments: dict[IRTypeVarType, IRResolvedType], loc: Location) -> IRStruct:
        if len(arguments) != len(generic.get_type_vars()):
            raise CompilerMessage(ErrorType.COMPILATION, f"Mismatched number of arguments to generic (expected {len(generic.get_type_vars())}, got {len(arguments)}):", loc, [
                CompilerMessage(ErrorType.NOTE, f"Generic defined here:", generic.loc)
            ])

        with self.substitutions.replace(arguments):
            new_type_args: tuple[IRResolvedType, ...] = tuple(self.resolve_type(arg) for arg in generic.type_args)

            if new_type_args in generic.reifications:
                return generic.reifications[new_type_args]

            struct = IRStruct(
                IRTypeDecl(IRUnresolvedUnknownType(), generic.type_decl.location),
                IRValueDecl(IRUnresolvedUnknownType(), generic.constructor.location, False),
                f"{generic.base_name}",
                generic.supertraits,
                [IRField(field.name, field.type).set_loc(field.loc) for field in generic.fields],
                [IRMethod(method.name, method.is_static, method.is_self, method.function).set_loc(method.loc) for method in generic.methods],
                new_type_args, generic.reifications,
                lambda a, l: self.resolve_generic_struct(struct, a, l)
            ).set_loc(loc)
            struct.type_decl.type = IRStructType(struct).set_loc(loc)
            generic.reifications[tuple(arguments.values())] = struct

            for field in struct.fields:
                field.type = self.resolve_type(field.type)

            for method in struct.methods:
                func = IRFunction(
                    IRValueDecl(IRUnresolvedUnknownType(), method.function.loc, False),
                    f"{struct.name}::{method.name}", new_type_args,
                    [IRParameter(IRValueDecl(param.decl.type, param.loc, True), param.name, param.type) for param in method.function.parameters],
                    method.function.return_type,
                    method.function.body, False, method.function.is_builtin, method.function.reifications
                ).set_loc(generic.loc)
                func.body = SubstituteNodes(self.substitutions.value,
                                            {old_param.decl: new_param.decl for new_param, old_param in zip(func.parameters, method.function.parameters)},
                                            self).perform_substitutions(func.body)
                method.function = func

            self.infer_struct_body(struct)
            self.infer_struct_methods(struct)

            self.program.structs.append(struct)
        return struct

    def create_array_type(self, type_decl: IRTypeDecl, value_decl: IRValueDecl) -> IRStruct:
        array_loc = BuiltinLocation()
        array_type_var = IRTypeVariable("Item", None, IRTypeDecl(IRUnresolvedUnknownType(), array_loc))
        type_var = array_type_var.type_decl.type = IRTypeVarType(array_type_var)
        array = IRStruct(
            type_decl,
            value_decl,
            "Array", [], [], [], (IRTypeVarType(array_type_var),), self.program.array_reifications,
            lambda a, l: self.array_callback(array, a, l)
        )
        array_type = array.type_decl.type = IRStructType(array)

        def constructor_callback(arguments: dict[IRTypeVarType, IRResolvedType], loc: Location) -> IRValue:
            struct = self.array_callback(array, arguments, loc)
            return IRValue(cast(IRFunctionType, struct.constructor.type), struct.constructor)

        array_func = IRFunction(value_decl, array.name, array.type_args, [
            IRParameter(IRValueDecl(IRIntegerType(64), array_loc, True), "length", IRIntegerType(64)),
            IRParameter(IRValueDecl(IRFunctionType([IRIntegerType(64)], type_var), array_loc, True), "func", type_var)
        ], array_type, IRBlock([], [], False), False, True, constructor_callback, {})
        array.constructor.type = array_func.function_type

        def get_callback(arguments: dict[IRTypeVarType, IRResolvedType], loc: Location) -> IRValue:
            struct = self.array_callback(array, arguments, loc)
            method = struct.methods[struct.has_method("get")]
            return IRValue(method.function.function_type, method.function.decl)

        get_type = IRFunctionType([array_type, IRIntegerType(64)], type_var)
        get_decl = IRValueDecl(get_type, array_loc, False)
        get_method = IRMethod(
            "get", True, True,
            IRFunction(get_decl, f"Array[{array_type}]::get", (type_var,), [
                IRParameter(IRValueDecl(array_type, array_loc, True), "self", array_type),
                IRParameter(IRValueDecl(IRIntegerType(64), array_loc, True), "index", IRIntegerType(64))
            ], type_var, IRBlock([], [], False), False, True, get_callback, {})
        )
        array.methods.append(get_method)

        def set_callback(arguments: dict[IRTypeVarType, IRResolvedType], loc: Location) -> IRValue:
            struct = self.array_callback(array, arguments, loc)
            method = struct.methods[struct.has_method("set")]
            return IRValue(method.function.function_type, method.function.decl)

        set_type = IRFunctionType([array_type, IRIntegerType(64), type_var], IRUnitType())
        set_decl = IRValueDecl(set_type, array_loc, False)
        set_method = IRMethod(
            "set", True, True,
            IRFunction(set_decl, f"Array[{array_type}]::set", (type_var,), [
                IRParameter(IRValueDecl(array_type, array_loc, True), "self", array_type),
                IRParameter(IRValueDecl(IRIntegerType(64), array_loc, True), "index", IRIntegerType(64)),
                IRParameter(IRValueDecl(type_var, array_loc, True), "value", array_type)
            ], IRUnitType(), IRBlock([], [], True), False, True, set_callback, {})
        )
        array.methods.append(set_method)
        return array

    def array_callback(self, array_type: IRStruct, arguments: dict[IRTypeVarType, IRResolvedType], loc: Location) -> IRStruct:
        if len(arguments) != 1:
            raise CompilerMessage(ErrorType.COMPILATION, f"Mismatched number of arguments to generic (expected 1, got {len(arguments)}):", loc)
        with self.substitutions.replace(arguments):
            type = self.resolve_type(array_type.type_args[0])
        if type not in self.program.array_variants:
            self.create_specific_array_type(type)
        variant = self.program.array_variants[type]
        return variant.array

    def create_specific_array_type(self, type: IRResolvedType):
        array_loc = BuiltinLocation()
        array_constructor = IRValueDecl(IRUnresolvedUnknownType(), array_loc, False)
        array = IRStruct(
            IRTypeDecl(IRUnresolvedUnknownType(), array_loc),
            array_constructor,
            f"Array", [], [], [], (type,), self.program.array_reifications,
            lambda a, l: self.array_callback(array, a, l)
        )
        array_type = array.type_decl.type = IRStructType(array)

        def constructor_callback(arguments: dict[IRTypeVarType, IRResolvedType], loc: Location) -> IRValue:
            struct = self.array_callback(array, arguments, loc)
            return IRValue(cast(IRFunctionType, struct.constructor.type), struct.constructor)

        array_func = IRFunction(array_constructor, array.name, array.type_args, [
            IRParameter(IRValueDecl(IRIntegerType(64), array_loc, True), "length", IRIntegerType(64)),
            IRParameter(IRValueDecl(IRFunctionType([IRIntegerType(64)], type), array_loc, True), "func", IRFunctionType([IRIntegerType(64)], type))
        ], array_type, IRBlock([], [], False), False, True, constructor_callback, {})
        array.constructor.type = array_func.function_type

        def get_callback(arguments: dict[IRTypeVarType, IRResolvedType], loc: Location) -> IRValue:
            struct = self.array_callback(array, arguments, loc)
            method = struct.methods[struct.has_method("get")]
            return IRValue(method.function.function_type, method.function.decl)

        get_type = IRFunctionType([array_type, IRIntegerType(64)], type)
        get_decl = IRValueDecl(get_type, array_loc, False)
        get_method = IRMethod(
            "get", True, True,
            IRFunction(get_decl, f"Array[{type}]::get", (type,), [
                IRParameter(IRValueDecl(array_type, array_loc, True), "self", array_type),
                IRParameter(IRValueDecl(IRIntegerType(64), array_loc, True), "index", IRIntegerType(64))
            ], type, IRBlock([], [], False), False, True, get_callback, {})
        )
        array.methods.append(get_method)

        def set_callback(arguments: dict[IRTypeVarType, IRResolvedType], loc: Location) -> IRValue:
            struct = self.array_callback(array, arguments, loc)
            method = struct.methods[struct.has_method("set")]
            return IRValue(method.function.function_type, method.function.decl)

        set_type = IRFunctionType([array_type, IRIntegerType(64), type], IRUnitType())
        set_decl = IRValueDecl(set_type, array_loc, False)
        set_method = IRMethod(
            "set", True, True,
            IRFunction(set_decl, f"Array[{type}]::set", (type,),[
                IRParameter(IRValueDecl(array_type, array_loc, True), "self", array_type),
                IRParameter(IRValueDecl(IRIntegerType(64), array_loc, True), "index", IRIntegerType(64)),
                IRParameter(IRValueDecl(type, array_loc, True), "value", type)
            ], IRUnitType(), IRBlock([], [], True), False, True, set_callback, {})
        )
        array.methods.append(set_method)

        self.program.array_reifications[(type,)] = array
        self.program.array_variants[type] = ArrayVariant(type, array, array_constructor, get_decl, set_decl)

    def resolve_generic_function(self, generic: IRFunction, arguments: dict[IRTypeVarType, IRResolvedType], loc: Location) -> IRFunction:
        if len(arguments) != len(generic.get_type_vars()):
            raise CompilerMessage(ErrorType.COMPILATION, f"Mismatched number of arguments to generic (expected {len(generic.get_type_vars())}, got {len(arguments)}):", loc, [
                CompilerMessage(ErrorType.NOTE, f"Generic defined here:", generic.loc)
            ])

        with self.substitutions.replace(arguments):
            new_type_args: tuple[IRResolvedType, ...] = tuple(self.resolve_type(arg) for arg in generic.type_args)
        if new_type_args in generic.reifications:
            return generic.reifications[new_type_args]

        def callback(type_args: dict[IRTypeVarType, IRResolvedType], loc: Location) -> IRValue:
            if len(new_type_args) != len(type_args):
                raise CompilerMessage(ErrorType.COMPILATION, f"Mismatched type argument counts (expected {len(new_type_args)}, got {len(type_args)}):", loc, [
                                          CompilerMessage(ErrorType.NOTE, f"Generic declared here:", generic.loc)
                                      ])
            resultant = self.resolve_generic_function(generic, type_args, loc)
            return IRValue(resultant.function_type, resultant.decl)

        if any(isinstance(arg, IRTypeVarType) for arg in arguments):
            raise ValueError()
        else:
            func = IRFunction(
                IRValueDecl(IRUnresolvedUnknownType(), generic.decl.location, False),
                f"{generic.name}[{', '.join(str(arg) for arg in arguments)}]", new_type_args,
                [IRParameter(IRValueDecl(param.decl.type, param.loc, True), param.name, param.type) for param in generic.parameters],
                generic.return_type,
                generic.body,
                False, False, callback
            ).set_loc(generic.loc)
            generic.reifications[new_type_args] = func

            # substitutions: dict[IRTypeVarType, IRResolvedType] = dict(zip((cast(IRTypeVarType, type_var.type_decl.type) for type_var in generic.type_vars), arguments))
            func.body = SubstituteNodes(arguments, {old_param.decl: new_param.decl for new_param, old_param in zip(func.parameters, generic.parameters)}, self).perform_substitutions(func.body)

            with self.substitutions.replace(arguments):
                self.infer_function_type(func)
                self.infer_function_body(func)

            self.program.functions.append(func)
            return func

    def infer_types(self):
        self.create_array_type(self.program.array_decl, self.program.array_constructor_decl)

        initial_structs = self.program.structs[:]
        initial_functions = self.program.functions[:]
        for struct in initial_structs:
            self.infer_struct_type(struct)

        for struct in initial_structs:
            self.infer_struct_body(struct)

        for struct in initial_structs:
            self.infer_struct_methods(struct)

        for function in initial_functions:
            self.infer_function_type(function)

        for function in initial_functions:
            self.infer_function_body(function)

    def infer_struct_type(self, struct: IRStruct):
        struct.substitute = lambda a, l: self.resolve_generic_struct(struct, a, l)

        struct.type_decl.type = IRStructType(struct).set_loc(struct.loc)

    def infer_struct_body(self, struct: IRStruct):
        field_param_types: list[IRParameter] = []
        field_types: list[IRResolvedType] = []
        for field in struct.fields:
            field.type = self.resolve_type(field.type)
            if field.type is None:
                raise ValueError()
            field_types.append(field.type)
            field_param_types.append(IRParameter(IRValueDecl(field.type, field.loc, True), field.name, field.type))

        for method in struct.methods:
            function = method.function
            param_types: list[IRResolvedType] = []
            for param in function.parameters:
                if len(param_types) == 0 and method.is_self:
                    if len(struct.get_type_vars()) > 0:
                        type = IRUnresolvedGenericType(struct.type_decl.type, list(struct.get_type_vars()))
                        type = self.resolve_type(type)
                    else:
                        type = struct.type_decl.type
                    param.decl.type = param.type = type
                else:
                    param.decl.type = param.type = self.resolve_type(param.type)
                    if param.type is None:
                        raise ValueError()
                param_types.append(param.type)

            function.return_type = self.resolve_type(function.return_type)
            if function.return_type is None:
                raise ValueError()

            function.decl.type = IRFunctionType(param_types, function.return_type).set_loc(method.loc)

            if function.return_type != IRUnitType() and not function.is_builtin and not function.body.always_returns():
                raise CompilerMessage(ErrorType.COMPILATION, f"Cannot prove that function always has a return value:", method.loc)

        def callback(type_args: dict[IRTypeVarType, IRResolvedType], loc: Location) -> IRValue:
            if len(struct.get_type_vars()) != len(type_args):
                raise CompilerMessage(ErrorType.COMPILATION, f"Mismatched type argument counts (expected {len(struct.get_type_vars())}, got {len(type_args)}):", loc, [
                                          CompilerMessage(ErrorType.NOTE, f"Generic declared here:", struct.loc)
                                      ])
            resultant = self.resolve_generic_struct(struct, type_args, loc)
            return IRValue(cast(IRFunction, resultant.constructor.declarer).function_type, resultant.constructor)

        struct.constructor.type = IRFunctionType(field_types, cast(IRResolvedType, struct.type_decl.type)).set_loc(struct.loc)
        func = IRFunction(struct.constructor, struct.name, struct.type_args, field_param_types, struct.type_decl.type, IRBlock([], [], False), False, True, callback, {}).set_loc(struct.loc)

    def infer_struct_methods(self, struct: IRStruct):
        for method in struct.methods:
            self.infer_function_body(method.function)

        if len(struct.get_type_vars()) == 0:
            for method in struct.methods:
                self.program.functions.append(method.function)

    def infer_function_type(self, function: IRFunction):
        param_types: list[IRParameterType] = []
        for param in function.parameters:
            param.type = param.decl.type = self.resolve_type(param.type)
            if param.type is None:
                raise ValueError()
            param_types.append(IRParameterType(param.type, param.loc))

        function.return_type = self.resolve_type(function.return_type)
        if function.return_type is None:
            raise ValueError()

        function.decl.type = function.function_type

        if not function.is_extern and function.return_type != IRUnitType() and not function.body.always_returns() :
            raise CompilerMessage(ErrorType.COMPILATION, f"Cannot prove that function always has a return value:", function.loc)

    def infer_function_body(self, function: IRFunction):
        with self.expected_return.replace(Return(cast(IRResolvedType, function.return_type), function.loc)):
            for stmt in function.body.body:
                self.infer_stmt(stmt)

    def infer_stmt(self, stmt: IRStmt):
        if isinstance(stmt, IRDeclStmt):
            self.infer_decl_stmt(stmt)
        elif isinstance(stmt, IRReturnStmt):
            self.infer_return_stmt(stmt)
        elif isinstance(stmt, IRExprStmt):
            self.unify_expr(stmt.expr, None, None)
        elif isinstance(stmt, IRWhileStmt):
            self.infer_while_stmt(stmt)
        else:
            raise ValueError(type(stmt))

    def infer_decl_stmt(self, stmt: IRDeclStmt):
        resolved_decl = self.resolve_type(stmt.type)
        type, _ = self.unify_expr(stmt.init, resolved_decl, stmt.type.loc)
        if resolved_decl is None:
            resolved_decl = type
        stmt.type = resolved_decl
        stmt.decl.type = resolved_decl

    def infer_return_stmt(self, stmt: IRReturnStmt):
        expected_return = self.expected_return.value
        self.unify_expr(stmt.expr, expected_return.type, expected_return.loc)

    def infer_while_stmt(self, stmt: IRWhileStmt):
        self.unify_expr(stmt.cond, IRBoolType(), None)
        self.unify_expr(stmt.body, None, None)

    def unify_expr(self, expr: IRExpr, bound: IRResolvedType | None, bound_loc: Location | None) -> IRValue:
        if isinstance(expr, IRIntegerExpr):
            return self.unify_integer_expr(expr, bound, bound_loc)
        # elif isinstance(expr, IRStringExpr):
        #     return self.unify_string_expr(expr, bound, bound_loc)
        elif isinstance(expr, IRNameExpr):
            return self.unify_name_expr(expr, bound, bound_loc)
        elif isinstance(expr, IRCallExpr):
            return self.unify_call_expr(expr, bound, bound_loc)
        elif isinstance(expr, IRGenericExpr):
            return self.unify_generic_expr(expr, bound, bound_loc)
        elif isinstance(expr, IRAttrExpr):
            return self.unify_attr_expr(expr, bound, bound_loc)
        elif isinstance(expr, IRBinaryExpr):
            return self.unify_binary_expr(expr, bound, bound_loc)
        elif isinstance(expr, IRIf):
            return self.unify_if_expr(expr, bound, bound_loc)
        elif isinstance(expr, IRBlock):
            return self.unify_block_expr(expr, bound, bound_loc)
        elif isinstance(expr, IRAssign):
            return self.unify_assign(expr, bound, bound_loc)
        elif isinstance(expr, IRAttrAssign):
            return self.unify_attr_assign(expr, bound, bound_loc)
        elif isinstance(expr, IRLambda):
            return self.unify_lambda(expr, bound, bound_loc)
        else:
            raise ValueError(type(expr))

    def unify_integer_expr(self, expr: IRIntegerExpr, bound: IRResolvedType | None, bound_loc: Location | None) -> IRValue:
        expr.yield_type, _ = self.unify_type(IRIntegerType(64).set_loc(expr.loc), bound, expr.loc, bound_loc)
        return IRValue(expr.yield_type, None)

    # def unify_string_expr(self, expr: IRStringExpr, bound: IRResolvedType | None, bound_loc: Location | None) -> IRResolvedType:
    #     expr.yield_type, _ = self.unify_type(IRStringType().set_loc(expr.loc), bound, expr.loc, bound_loc)
    #     return expr.yield_type

    def unify_name_expr(self, expr: IRNameExpr, bound: IRResolvedType | None, bound_loc: Location | None) -> IRValue:
        resolved_name = self.resolve_type(expr.name.type)
        if resolved_name is None:
            raise ValueError()
        expr.yield_type, _ = self.unify_type(resolved_name, bound, expr.loc, bound_loc)
        return IRValue(expr.yield_type, expr.name)

    def unify_generic_expr(self, expr: IRGenericExpr, bound: IRResolvedType | None, bound_loc: Location | None) -> IRValue:
        resolved_generic, value = self.unify_expr(expr.generic, None, None)
        if value is None:
            raise CompilerMessage(ErrorType.COMPILATION, f"Expression could not be resolved into a function", expr.loc)
        declarer = value.declarer
        if not isinstance(declarer, IRFunction):
            raise CompilerMessage(ErrorType.COMPILATION, f"Expression could not be resolved into a function", expr.loc)
        if not isinstance(resolved_generic, IRFunctionType):
            raise CompilerMessage(ErrorType.COMPILATION, f"Expression must be a function, is instead a {resolved_generic}", expr.loc)

        if len(declarer.get_type_vars()) != len(expr.arguments):
            raise CompilerMessage(ErrorType.COMPILATION, f"Mismatched type argument counts (expected {len(declarer.get_type_vars())}, got {len(expr.arguments)}):", expr.loc, [
                CompilerMessage(ErrorType.NOTE, f"Generic declared here:", resolved_generic.loc)
            ])

        expr.yield_type, replacement_name = declarer.callback({var: self.resolve_type(type) for var, type in zip(declarer.get_type_vars(), expr.arguments)}, expr.loc)
        expr.replacement_expr = IRNameExpr(replacement_name).set_loc(expr.loc)
        return IRValue(expr.yield_type, replacement_name)

    def unify_call_expr(self, expr: IRCallExpr, bound: IRResolvedType | None, bound_loc: Location | None) -> IRValue:
        if isinstance(expr.callee, IRAttrExpr):
            resolved_object, _ = self.unify_expr(expr.callee.object, None, None)
            if not isinstance(resolved_object, IRStructType):
                raise CompilerMessage(ErrorType.COMPILATION, f"Object must be a struct, is instead a {resolved_object}:", expr.callee.loc)
            if (method_index := resolved_object.struct.has_method(expr.callee.attr)) is not None:
                method = resolved_object.struct.methods[method_index]
                resolved_callee = method.function.function_type

                if len(resolved_callee.param_types) != len(expr.arguments) + (1 if method.is_self else 0):
                    raise CompilerMessage(ErrorType.COMPILATION, f"Mismatched argument counts (expected {len(resolved_callee.param_types)}, got {len(expr.arguments) + (1 if method.is_self else 0)}):", expr.loc, [
                        CompilerMessage(ErrorType.NOTE, f"Function declared here:", resolved_callee.loc)
                    ])
                for param, argument in zip(resolved_callee.param_types[(1 if method.is_self else 0):], expr.arguments):
                    self.unify_expr(argument, param, param.loc)

                expr.as_method_call = IRMethodCallExpr(expr.callee.object, method, expr.arguments[:])
                expr.yield_type, _ = self.unify_type(resolved_callee.ret_type, bound, expr.loc, bound_loc)
                return IRValue(expr.yield_type, None)

        resolved_callee, _ = self.unify_expr(expr.callee, None, None)
        if not isinstance(resolved_callee, IRFunctionType):
            raise CompilerMessage(ErrorType.COMPILATION, f"Callee must be a function, is instead a {resolved_callee}", expr.loc)
        if len(resolved_callee.param_types) != len(expr.arguments):
            raise CompilerMessage(ErrorType.COMPILATION, f"Mismatched argument counts (expected {len(resolved_callee.param_types)}, got {len(expr.arguments)}):", expr.loc, [
                CompilerMessage(ErrorType.NOTE, f"Function declared here:", resolved_callee.loc)
            ])
        for param, argument in zip(resolved_callee.param_types, expr.arguments):
            self.unify_expr(argument, param, param.loc)
        expr.yield_type, _ = self.unify_type(resolved_callee.ret_type, bound, expr.loc, bound_loc)
        return IRValue(expr.yield_type, None)

    def unify_attr_expr(self, expr: IRAttrExpr, bound: IRResolvedType | None, bound_loc: Location | None) -> IRValue:
        resolved_object, _ = self.unify_expr(expr.object, None, None)
        if not isinstance(resolved_object, IRStructType):
            raise CompilerMessage(ErrorType.COMPILATION, f"Object must be a struct, is instead a {resolved_object}:", expr.loc)
        try:
            expr.index, field = next((index, field) for index, field in enumerate(resolved_object.struct.fields) if field.name == expr.attr)
        except StopIteration:
            raise CompilerMessage(ErrorType.COMPILATION, f"Object of type {resolved_object.struct.name} does not have a field named {expr.attr}:", expr.loc, [
                                      CompilerMessage(ErrorType.NOTE, f"{resolved_object.struct.name} defined here:", resolved_object.struct.loc)
                                  ]) from None

        expr.yield_type, _ = self.unify_type(cast(IRResolvedType, field.type), bound, expr.loc, bound_loc)
        return IRValue(expr.yield_type, None)

    def unify_binary_expr(self, expr: IRBinaryExpr, bound: IRResolvedType | None, bound_loc: Location | None) -> IRValue:
        match expr.op:
            case "Add":
                left_type, _ = self.unify_expr(expr.left, None, None)
                right_type, _ = self.unify_expr(expr.right, None, None)
                if isinstance(left_type, IRIntegerType) and isinstance(right_type, IRIntegerType):
                    expr.yield_type, _ = self.unify_type(IRIntegerType(max(left_type.bits, right_type.bits)), bound, expr.loc, bound_loc)
                    return IRValue(expr.yield_type, None)
                else:
                    raise CompilerMessage(ErrorType.COMPILATION, f"Mismatched arguments to addition (left is {left_type}, right is {right_type}):", expr.loc)
            case "Sub":
                left_type, _ = self.unify_expr(expr.left, None, None)
                right_type, _ = self.unify_expr(expr.right, None, None)
                if isinstance(left_type, IRIntegerType) and isinstance(right_type, IRIntegerType):
                    expr.yield_type, _ = self.unify_type(IRIntegerType(max(left_type.bits, right_type.bits)), bound,
                                                         expr.loc, bound_loc)
                    return IRValue(expr.yield_type, None)
                else:
                    raise CompilerMessage(ErrorType.COMPILATION,
                                          f"Mismatched arguments to subtraction (left is {left_type}, right is {right_type}):",
                                          expr.loc)
            case "Mul":
                left_type, _ = self.unify_expr(expr.left, None, None)
                right_type, _ = self.unify_expr(expr.right, None, None)
                if isinstance(left_type, IRIntegerType) and isinstance(right_type, IRIntegerType):
                    expr.yield_type, _ = self.unify_type(IRIntegerType(max(left_type.bits, right_type.bits)), bound,
                                                         expr.loc, bound_loc)
                    return IRValue(expr.yield_type, None)
                else:
                    raise CompilerMessage(ErrorType.COMPILATION,
                                          f"Mismatched arguments to multiplication (left is {left_type}, right is {right_type}):",
                                          expr.loc)
            case "Div":
                left_type, _ = self.unify_expr(expr.left, None, None)
                right_type, _ = self.unify_expr(expr.right, None, None)
                if isinstance(left_type, IRIntegerType) and isinstance(right_type, IRIntegerType):
                    expr.yield_type, _ = self.unify_type(IRIntegerType(max(left_type.bits, right_type.bits)), bound,
                                                         expr.loc, bound_loc)
                    return IRValue(expr.yield_type, None)
                else:
                    raise CompilerMessage(ErrorType.COMPILATION,
                                          f"Mismatched arguments to division (left is {left_type}, right is {right_type}):",
                                          expr.loc)
            case "Mod":
                left_type, _ = self.unify_expr(expr.left, None, None)
                right_type, _ = self.unify_expr(expr.right, None, None)
                if isinstance(left_type, IRIntegerType) and isinstance(right_type, IRIntegerType):
                    expr.yield_type, _ = self.unify_type(IRIntegerType(max(left_type.bits, right_type.bits)), bound,
                                                         expr.loc, bound_loc)
                    return IRValue(expr.yield_type, None)
                else:
                    raise CompilerMessage(ErrorType.COMPILATION,
                                          f"Mismatched arguments to modulus (left is {left_type}, right is {right_type}):",
                                          expr.loc)
            case "Less" | "Greater" | "LessEqual" | "GreaterEqual" | "Equal" | "NotEqual":
                left_type, _ = self.unify_expr(expr.left, None, None)
                right_type, _ = self.unify_expr(expr.right, None, None)
                if isinstance(left_type, IRIntegerType) and isinstance(right_type, IRIntegerType):
                    expr.yield_type = IRBoolType()
                    return IRValue(expr.yield_type, None)
                else:
                    raise CompilerMessage(ErrorType.COMPILATION, f"Mismatched arguments to comparison (left is {left_type}, right is {right_type}):", expr.loc)
            case _:
                raise ValueError(expr.op)

    def unify_if_expr(self, expr: IRIf, bound: IRResolvedType | None, bound_loc: Location | None) -> IRValue:
        self.unify_expr(expr.cond, IRBoolType(), None)
        result_type, _ = self.unify_expr(expr.then_do, bound, bound_loc)
        if expr.else_do is not None:
            else_result, _ = self.unify_expr(expr.else_do, bound, bound_loc)
        else:
            else_result = IRUnitType()
        if else_result.is_subtype(result_type):
            pass
        elif result_type.is_subtype(else_result):
            result_type = else_result
        else:
            raise CompilerMessage(ErrorType.COMPILATION, f"The if expression's branches do not have reconcilable result types (then's is {result_type}, else's is {result_type}):", expr.loc)
        expr.yield_type = result_type
        return IRValue(expr.yield_type, None)

    def unify_block_expr(self, expr: IRBlock, bound: IRResolvedType | None, bound_loc: Location | None) -> IRValue:
        for stmt in expr.body:
            self.infer_stmt(stmt)
        if expr.return_unit:
            expr.yield_type = IRUnitType()
            yield_loc = expr.loc
        else:
            last_stmt = cast(IRExprStmt, expr.body[-1])
            expr.yield_type = last_stmt.expr.yield_type
            yield_loc = last_stmt.loc
        self.unify_type(expr.yield_type, bound, yield_loc, bound_loc)
        return IRValue(expr.yield_type, None)

    def unify_assign(self, expr: IRAssign, bound: IRResolvedType | None, bound_loc: Location | None) -> IRValue:
        resolved_name = self.resolve_type(expr.name.type)
        if resolved_name is None:
            raise ValueError()
        expr.yield_type, value = self.unify_expr(expr.value, bound, bound_loc)
        self.unify_type(expr.yield_type, resolved_name, expr.value.loc, expr.name.location)
        return IRValue(expr.yield_type, value)

    def unify_attr_assign(self, expr: IRAttrAssign, bound: IRResolvedType | None, bound_loc: Location | None) -> IRValue:
        resolved_object, _ = self.unify_expr(expr.obj, None, None)
        if not isinstance(resolved_object, IRStructType):
            raise CompilerMessage(ErrorType.COMPILATION, f"Object must be a struct, is instead a {resolved_object}:", expr.loc)
        try:
            expr.index, field = next((index, field) for index, field in enumerate(resolved_object.struct.fields) if field.name == expr.attr)
        except StopIteration:
            raise CompilerMessage(ErrorType.COMPILATION, f"Object of type {resolved_object.struct.name} does not have a field named {expr.attr}:", expr.loc, [
                                      CompilerMessage(ErrorType.NOTE, f"{resolved_object.struct.name} defined here:", resolved_object.struct.loc)
                                  ]) from None

        expr.yield_type, value = self.unify_expr(expr.value, bound, bound_loc)

        self.unify_type(expr.yield_type, cast(IRResolvedType, field.type), expr.value.loc, field.loc)
        return IRValue(expr.yield_type, value)

    def unify_lambda(self, expr: IRLambda, bound: IRResolvedType | None, bound_loc: Location | None) -> IRValue:
        if isinstance(bound, IRFunctionType):
            if len(expr.parameters) != len(bound.param_types):
                raise CompilerMessage(ErrorType.COMPILATION, f"Mismatched argument counts (expected {len(bound.param_types)}, got {len(expr.parameters)}):", expr.loc, [
                    CompilerMessage(ErrorType.NOTE, f"Expectation is derived from here:", bound_loc)
                ])
            for param, expected_param in zip(expr.parameters, bound.param_types):
                param.type, _ = self.unify_type(self.resolve_type(param.type), expected_param, param.loc, expected_param.loc)
                param.decl.type = param.type
            expr.ret_type, _ = self.unify_type(self.resolve_type(expr.ret_type), bound.ret_type, expr.loc, bound.loc)
        else:
            for param in expr.parameters:
                param.type = self.resolve_type(param.type)
                param.decl.type = param.type
                if param.type is None:
                    raise CompilerMessage(ErrorType.COMPILATION, f"Type of parameter could not be inferred", param.loc)
            expr.ret_type = self.resolve_type(expr.ret_type)
            if expr.ret_type is None:
                raise CompilerMessage(ErrorType.COMPILATION, f"Type of return type could not be inferred", expr.loc)
        with self.expected_return.replace(Return(expr.ret_type, expr.loc)):
            self.unify_expr(expr.body, expr.ret_type, expr.loc)

        expr.yield_type = IRFunctionType([param.type for param in expr.parameters], expr.ret_type).set_loc(expr.loc)
        self.unify_type(expr.yield_type, bound, expr.loc, bound_loc)
        return IRValue(expr.yield_type, None)

    def unify_type(self, yield_type: IRResolvedType | None, bound_type: IRResolvedType | None, yield_loc: Location, expected_loc: Location | None) -> tuple[IRResolvedType, IRResolvedType]:
        if yield_type is None and bound_type is None:
            raise ValueError()
        elif yield_type is None:
            return bound_type, bound_type
        elif bound_type is None:
            return yield_type, yield_type
        else:
            if yield_type.is_subtype(bound_type):
                return yield_type, bound_type
            else:
                if expected_loc is not None:
                    raise CompilerMessage(ErrorType.COMPILATION, f"Types do not agree. Expected {bound_type}, got {yield_type}", yield_loc, [
                        CompilerMessage(ErrorType.NOTE, f"Expectation is derived from here:", expected_loc)
                    ])
                else:
                    raise CompilerMessage(ErrorType.COMPILATION, f"Types do not agree. Expected {bound_type}, got {yield_type}", yield_loc)

    def resolve_type(self, type: IRType) -> IRResolvedType | None:
        if isinstance(type, IRResolvedType):
            if type.is_concrete():
                return type
            elif isinstance(type, IRTypeVarType):
                if type in self.substitutions.value:
                    return self.substitutions.value[type]
                else:
                    return type
            elif isinstance(type, IRStructType):
                new_type = type.struct.substitute({type_var: self.resolve_type(type_var) for type_var in type.struct.get_type_vars()}, type.loc)
                return cast(IRResolvedType, new_type.type_decl.type)
            elif isinstance(type, IRFunctionType):
                return IRFunctionType([self.resolve_type(param) for param in type.param_types], self.resolve_type(type.ret_type)).set_loc(type.loc)
            else:
                raise ValueError(type.__class__)
        else:
            if isinstance(type, IRUnresolvedNameType):
                referred_type = type.decl.type
                if isinstance(referred_type, IRResolvedType):
                    return referred_type
                else:
                    raise CompilerMessage(ErrorType.COMPILATION, f"Type could not be resolved", type.decl.location)
            elif isinstance(type, IRUnresolvedUnknownType):
                return None
            elif isinstance(type, IRUnresolvedGenericType):
                generic_type = self.resolve_type(type.generic)
                if not isinstance(generic_type, IRStructType):
                    raise ValueError()
                type_args = [self.resolve_type(type_arg) for type_arg in type.type_args]
                new_type = generic_type.struct.substitute({type_var: arg for type_var, arg in zip(generic_type.struct.get_type_vars(), type_args)}, type.loc)
                # noinspection PyTypeChecker
                return new_type.type_decl.type
            elif isinstance(type, IRUnresolvedFunctionType):
                return IRFunctionType([self.resolve_type(param) for param in type.parameters], self.resolve_type(type.ret_type)).set_loc(type.loc)
            else:
                raise ValueError(type)


class SubstituteNodes:
    def __init__(self, substitutions: dict[IRTypeVarType, IRResolvedType], value_decl: dict[IRValueDecl, IRValueDecl], inferrer: BidirectionalTypeInference):
        self.substitutions = substitutions
        self.inferrer = inferrer
        self.value_decl: dict[IRValueDecl, IRValueDecl] = value_decl

    def perform_substitutions(self, block: IRBlock) -> IRBlock:
        new_stmts = []
        for stmt in block.body:
            new_stmts.append(self.substitute_stmt(stmt))
        return IRBlock(new_stmts, [self.value_decl[decl] for decl in self.value_decl], block.return_unit)

    def substitute_stmt(self, stmt: IRStmt) -> IRStmt:
        if isinstance(stmt, IRExprStmt):
            return IRExprStmt(self.substitute_expr(stmt.expr)).set_loc(stmt.loc)
        elif isinstance(stmt, IRReturnStmt):
            return IRReturnStmt(self.substitute_expr(stmt.expr)).set_loc(stmt.loc)
        elif isinstance(stmt, IRDeclStmt):
            decl = IRValueDecl(self.substitute_type(stmt.type), stmt.loc, True)
            self.value_decl[stmt.decl] = decl
            return IRDeclStmt(decl, decl.type, self.substitute_expr(stmt.init)).set_loc(stmt.loc)
        elif isinstance(stmt, IRWhileStmt):
            return IRWhileStmt(self.substitute_expr(stmt.cond), self.substitute_expr(stmt.body)).set_loc(stmt.loc)
        else:
            raise ValueError(type(stmt))

    def substitute_expr(self, expr: IRExpr) -> IRExpr:
        if isinstance(expr, IRIntegerExpr):
            return IRIntegerExpr(expr.number).set_loc(expr.loc)
        elif isinstance(expr, IRNameExpr):
            if expr.name.is_runtime:
                return IRNameExpr(self.value_decl[expr.name]).set_loc(expr.loc)
            else:
                return IRNameExpr(expr.name).set_loc(expr.loc)
        elif isinstance(expr, IRBinaryExpr):
            return IRBinaryExpr(expr.op, self.substitute_expr(expr.left), self.substitute_expr(expr.right)).set_loc(expr.loc)
        elif isinstance(expr, IRAttrExpr):
            return IRAttrExpr(self.substitute_expr(expr.object), expr.attr).set_loc(expr.loc)
        elif isinstance(expr, IRCallExpr):
            return IRCallExpr(self.substitute_expr(expr.callee), [self.substitute_expr(arg) for arg in expr.arguments]).set_loc(expr.loc)
        elif isinstance(expr, IRGenericExpr):
            return IRGenericExpr(self.substitute_expr(expr.generic), [self.substitute_type(arg) for arg in expr.arguments]).set_loc(expr.loc)
        elif isinstance(expr, IRBlock):
            return IRBlock([self.substitute_stmt(stmt) for stmt in expr.body], [self.value_decl[decl] for decl in self.value_decl], expr.return_unit).set_loc(expr.loc)
        elif isinstance(expr, IRIf):
            return IRIf(self.substitute_expr(expr.cond), self.substitute_expr(expr.then_do), None if expr.else_do is None else self.substitute_expr(expr.else_do)).set_loc(expr.loc)
        elif isinstance(expr, IRAssign):
            # TODO check if can be assigned because apparently this can be done after the normal infer
            return IRAssign(self.value_decl[expr.name], expr.op, self.substitute_expr(expr.value))
        elif isinstance(expr, IRAttrAssign):
            return IRAttrAssign(self.substitute_expr(expr.obj), expr.attr, expr.op, self.substitute_expr(expr.value))
        elif isinstance(expr, IRLambda):
            parameters = []
            for param in expr.parameters:
                type_ = self.substitute_type(param.type)
                decl = IRValueDecl(type_, param.loc, True)
                self.value_decl[param.decl] = decl
                parameters.append(IRParameter(decl, param.name, type_).set_loc(param.loc))
            return IRLambda(
                [self.value_decl[decl] for decl in expr.exterior_names],
                parameters, self.substitute_type(expr.ret_type), cast(IRBlock, self.substitute_expr(expr.body))
            ).set_loc(expr.loc)
        elif isinstance(expr, IRNegExpr):
            return IRNegExpr(self.substitute_expr(expr.right)).set_loc(expr.loc)
        elif isinstance(expr, IRNotExpr):
            return IRNotExpr(self.substitute_expr(expr.right)).set_loc(expr.loc)
        else:
            raise ValueError(type(expr))

    def substitute_type(self, type: IRType) -> IRResolvedType:
        if isinstance(type, IRBoolType):
            return IRBoolType().set_loc(type.loc)
        elif isinstance(type, IRIntegerType):
            return IRIntegerType(type.bits).set_loc(type.loc)
        elif isinstance(type, IRUnitType):
            return IRUnitType().set_loc(type.loc)
        elif isinstance(type, IRUnresolvedNameType):
            return self.substitute_type(type.decl.type).set_loc(type.loc)
        elif isinstance(type, IRUnresolvedUnknownType):
            return IRUnresolvedUnknownType().set_loc(type.loc)
        elif isinstance(type, IRTypeVarType):
            if type in self.substitutions:
                return self.substitutions[type]
            else:
                return type
        elif isinstance(type, IRUnresolvedFunctionType):
            return IRFunctionType([self.substitute_type(self.inferrer.resolve_type(param)) for param in type.parameters],
                                  self.substitute_type(self.inferrer.resolve_type(type.ret_type))).set_loc(type.loc)
        elif isinstance(type, IRUnresolvedGenericType):
            return self.inferrer.resolve_type(type)
        elif isinstance(type, IRFunctionType):
            return IRFunctionType([self.substitute_type(param) for param in type.param_types],
                                  self.substitute_type(type.ret_type)).set_loc(type.loc)
        elif isinstance(type, IRStructType):
            if any(type_var in self.substitutions for type_var in type.struct.get_type_vars()):
                resolved = type.struct.substitute({type_var: self.substitute_type(type_var) for type_var in type.struct.get_type_vars()}, type.loc)
                return cast(IRResolvedType, resolved.type_decl.type)
            else:
                return type
        else:
            raise ValueError(type.__class__)
