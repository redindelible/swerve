from __future__ import annotations

from typing import cast

from swc_ir import *
from common import CompilerMessage, ErrorType, Location, ValueStack, NamedTuple


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

    def resolve_generic_struct(self, generic: IRGenericStruct, arguments: dict[IRTypeVarType, IRResolvedType], loc: Location) -> IRStruct:
        if len(arguments) != len(generic.type_vars):
            raise CompilerMessage(ErrorType.COMPILATION, f"Mismatched number of arguments to generic (expected {len(generic.type_vars)}, got {len(arguments)}):", loc, [
                CompilerMessage(ErrorType.NOTE, f"Generic defined here:", generic.loc)
            ])

        if tuple(arguments.values()) in generic.reifications:
            return generic.reifications[tuple(arguments.values())]

        if any(isinstance(arg, IRTypeVarType) for arg in arguments.values()):
            new_type_vars: list[IRTypeVariable] = []
            for type_var in generic.type_vars:
                new_type = arguments[cast(IRTypeVarType, type_var.type_decl.type)]
                if isinstance(new_type, IRTypeVarType):
                    new_type_vars.append(new_type.type_var)

            struct = IRGenericStruct(
                IRTypeDecl(IRUnresolvedUnknownType(), generic.type_decl.location),
                IRValueDecl(IRUnresolvedUnknownType(), generic.constructor.location, False),
                generic.name,
                new_type_vars,
                generic.supertraits,
                [IRField(field.name, field.type).set_loc(field.loc) for field in generic.fields],
                [IRMethod(method.name, method.is_static, method.is_self, method.function).set_loc(method.loc) for method in generic.methods],
                generic.reifications
            ).set_loc(loc)
            struct.type_decl.type = IRGenericStructType(struct, list(arguments.values())).set_loc(loc)

            is_concrete = False
        else:
            struct = IRStruct(
                IRTypeDecl(IRUnresolvedUnknownType(), generic.type_decl.location),
                IRValueDecl(IRUnresolvedUnknownType(), generic.constructor.location, False),
                f"{generic.name}[{', '.join(str(arg) for arg in arguments.values())}]",
                generic.supertraits,
                [IRField(field.name, field.type).set_loc(field.loc) for field in generic.fields],
                [IRMethod(method.name, method.is_static, method.is_self, method.function).set_loc(method.loc) for method in generic.methods]
            ).set_loc(loc)
            struct.type_decl.type = IRStructType(struct).set_loc(loc)

            is_concrete = True
        generic.reifications[tuple(arguments.values())] = struct

        with self.substitutions.replace(arguments):
            for method in struct.methods:
                func = IRFunction(
                    IRValueDecl(IRUnresolvedUnknownType(), method.function.loc, False),
                    f"{struct.name}::{method.name}",
                    [IRParameter(IRValueDecl(param.decl.type, param.loc, True), param.name, param.type) for param in method.function.parameters],
                    method.function.return_type,
                    method.function.body
                ).set_loc(generic.loc)
                func.body = SubstituteNodes(self.substitutions.value,
                                            {old_param.decl: new_param.decl for new_param, old_param in zip(func.parameters, method.function.parameters)},
                                            self).perform_substitutions(func.body)
                method.function = func

            self.infer_struct_body(struct)
            self.infer_struct_methods(struct)

        self.program.structs.append(struct)
        return struct

    def resolve_generic_function(self, generic: IRGenericFunction, arguments: list[IRResolvedType], loc: Location) -> IRFunction:
        if len(arguments) != len(generic.type_vars):
            raise CompilerMessage(ErrorType.COMPILATION, f"Mismatched number of arguments to generic (expected {len(generic.type_vars)}, got {len(arguments)}):", loc, [
                CompilerMessage(ErrorType.NOTE, f"Generic defined here:", generic.loc)
            ])

        if tuple(arguments) in generic.reifications:
            return generic.reifications[tuple(arguments)]

        if any(isinstance(arg, IRTypeVarType) for arg in arguments):
            raise ValueError()
        else:
            func = IRFunction(
                IRValueDecl(IRUnresolvedUnknownType(), generic.decl.location, False),
                f"{generic.name}[{', '.join(str(arg) for arg in arguments)}]",
                [IRParameter(IRValueDecl(param.decl.type, param.loc, True), param.name, param.type) for param in generic.parameters],
                generic.return_type,
                generic.body
            ).set_loc(generic.loc)
            generic.reifications[tuple(arguments)] = func

            substitutions: dict[IRTypeVarType, IRResolvedType] = dict(zip((cast(IRTypeVarType, type_var.type_decl.type) for type_var in generic.type_vars), arguments))
            func.body = SubstituteNodes(substitutions, {old_param.decl: new_param.decl for new_param, old_param in zip(func.parameters, generic.parameters)}, self).perform_substitutions(func.body)

            with self.substitutions.replace(substitutions):
                self.infer_function_type(func)
                self.infer_function_body(func)

            self.program.functions.append(func)
            return func

    def infer_types(self):
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
        if isinstance(struct, IRGenericStruct):
            type_vars = []
            for type_var in struct.type_vars:
                type = IRTypeVarType(type_var).set_loc(type_var.loc)
                type_var.type_decl.type = type
                type_vars.append(type)
            struct.type_decl.type = IRGenericStructType(struct, type_vars).set_loc(struct.loc)
        else:
            struct.type_decl.type = IRStructType(struct).set_loc(struct.loc)

    def infer_struct_body(self, struct: IRStruct):
        field_types: list[IRParameterType] = []
        for field in struct.fields:
            field.type = self.resolve_type(field.type)
            if field.type is None:
                raise ValueError()
            field_types.append(IRParameterType(field.type, field.loc))

        for method in struct.methods:
            function = method.function
            param_types: list[IRParameterType] = []
            for param in function.parameters:
                if len(param_types) == 0 and method.is_self:
                    param.decl.type = param.type = struct.type_decl.type
                else:
                    param.decl.type = param.type = self.resolve_type(param.type)
                    if param.type is None:
                        raise ValueError()
                param_types.append(IRParameterType(param.type, param.loc))

            function.return_type = self.resolve_type(function.return_type)
            if function.return_type is None:
                raise ValueError()

            function.function_type = function.decl.type = IRFunctionType(param_types, function.return_type).set_loc(method.loc)

            if not function.body.always_returns():
                if function.return_type != IRUnitType():
                    raise CompilerMessage(ErrorType.COMPILATION, f"Cannot prove that function always has a return value:", method.loc)

        if isinstance(struct, IRGenericStruct):
            def callback(type_args: list[IRResolvedType], loc: Location) -> tuple[IRFunctionType, IRExpr]:
                nonlocal struct
                struct = cast(IRGenericStruct, struct)
                # TODO length check
                resultant = self.resolve_generic_struct(struct, {type_var.type_decl.type: arg for type_var, arg in zip(struct.type_vars, type_args)}, loc)
                return cast(IRFunctionType, resultant.constructor.type), IRNameExpr(resultant.constructor)

            # noinspection PyTypeChecker
            struct.constructor.type = IRGenericFunctionType(struct.type_vars, field_types, struct.type_decl.type, callback).set_loc(struct.loc)
        else:
            # noinspection PyTypeChecker
            struct.constructor.type = IRFunctionType(field_types, struct.type_decl.type).set_loc(struct.loc)

    def infer_struct_methods(self, struct: IRStruct):
        for method in struct.methods:
            self.infer_function_body(method.function)

        if not isinstance(struct, IRGenericStruct):
            for method in struct.methods:
                self.program.functions.append(method.function)

    def infer_function_type(self, function: IRFunction):
        if isinstance(function, IRGenericFunction):
            for type_var in function.type_vars:
                type_var.type_decl.type = IRTypeVarType(type_var).set_loc(type_var.loc)
        param_types: list[IRParameterType] = []
        for param in function.parameters:
            param.type = param.decl.type = self.resolve_type(param.type)
            if param.type is None:
                raise ValueError()
            param_types.append(IRParameterType(param.type, param.loc))

        function.return_type = self.resolve_type(function.return_type)
        if function.return_type is None:
            raise ValueError()

        if isinstance(function, IRGenericFunction):
            def callback(type_args: list[IRResolvedType], loc: Location) -> tuple[IRFunctionType, IRExpr]:
                resultant = self.resolve_generic_function(cast(IRGenericFunction, function), type_args, loc)
                return cast(IRFunctionType, resultant.decl.type), IRNameExpr(resultant.decl)

            f_type = IRGenericFunctionType(function.type_vars, param_types, function.return_type, callback).set_loc(function.loc)
        else:
            f_type = IRFunctionType(param_types, function.return_type).set_loc(function.loc)
        function.function_type = function.decl.type = f_type

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
        type = self.unify_expr(stmt.init, resolved_decl, stmt.type.loc)
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

    def unify_expr(self, expr: IRExpr, bound: IRResolvedType | None, bound_loc: Location | None) -> IRResolvedType:
        if isinstance(expr, IRIntegerExpr):
            return self.unify_integer_expr(expr, bound, bound_loc)
        elif isinstance(expr, IRStringExpr):
            return self.unify_string_expr(expr, bound, bound_loc)
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

    def unify_integer_expr(self, expr: IRIntegerExpr, bound: IRResolvedType | None, bound_loc: Location | None) -> IRResolvedType:
        expr.yield_type, _ = self.unify_type(IRIntegerType(64).set_loc(expr.loc), bound, expr.loc, bound_loc)
        return expr.yield_type

    def unify_string_expr(self, expr: IRStringExpr, bound: IRResolvedType | None, bound_loc: Location | None) -> IRResolvedType:
        expr.yield_type, _ = self.unify_type(IRStringType().set_loc(expr.loc), bound, expr.loc, bound_loc)
        return expr.yield_type

    def unify_name_expr(self, expr: IRNameExpr, bound: IRResolvedType | None, bound_loc: Location | None) -> IRResolvedType:
        resolved_name = self.resolve_type(expr.name.type)
        if resolved_name is None:
            raise ValueError()
        expr.yield_type, _ = self.unify_type(resolved_name, bound, expr.loc, bound_loc)
        return expr.yield_type

    def unify_generic_expr(self, expr: IRGenericExpr, bound: IRResolvedType | None, bound_loc: Location | None) -> IRResolvedType:
        resolved_generic = self.unify_expr(expr.generic, None, None)
        if not isinstance(resolved_generic, IRGenericFunctionType):
            raise CompilerMessage(ErrorType.COMPILATION, f"Expression must be a generic function, is instead a {resolved_generic}", expr.loc)

        if len(resolved_generic.type_vars) != len(expr.arguments):
            raise CompilerMessage(ErrorType.COMPILATION, f"Mismatched type argument counts (expected {len(resolved_generic.type_vars)}, got {len(expr.arguments)}):", expr.loc, [
                CompilerMessage(ErrorType.NOTE, f"Generic declared here:", resolved_generic.loc)
            ])

        expr.yield_type, replacement_name = resolved_generic.callback([self.resolve_type(type) for type in expr.arguments], expr.loc)
        expr.replacement_expr = replacement_name
        return expr.yield_type

    def unify_call_expr(self, expr: IRCallExpr, bound: IRResolvedType | None, bound_loc: Location | None) -> IRResolvedType:
        if isinstance(expr.callee, IRAttrExpr):
            resolved_object = self.unify_expr(expr.callee.object, None, None)
            if not isinstance(resolved_object, IRStructType):
                raise CompilerMessage(ErrorType.COMPILATION, f"Object must be a struct, is instead a {resolved_object}:", expr.callee.loc)
            if (method_index := resolved_object.struct.has_method(expr.callee.attr)) is not None:
                method = resolved_object.struct.methods[method_index]
                resolved_callee = method.function.function_type

                if len(resolved_callee.param_types) != len(expr.arguments) + (1 if method.is_self else 0):
                    raise CompilerMessage(ErrorType.COMPILATION, f"Mismatched argument counts (expected {len(resolved_callee.param_types)}, got {len(expr.arguments) + (1 if method.is_self else 0)}):", expr.loc, [
                        CompilerMessage(ErrorType.NOTE, f"Function declared here:", resolved_callee.loc)
                    ])
                for param, argument in zip(resolved_callee.param_types[1:], expr.arguments):
                    self.unify_expr(argument, param.type, param.loc)

                expr.as_method_call = IRMethodCallExpr(expr.callee.object, method, expr.arguments[:])
                expr.yield_type, _ = self.unify_type(resolved_callee.ret_type, bound, expr.loc, bound_loc)
                return expr.yield_type

        resolved_callee = self.unify_expr(expr.callee, None, None)
        if not isinstance(resolved_callee, IRFunctionType):
            raise CompilerMessage(ErrorType.COMPILATION, f"Callee must be a function, is instead a {resolved_callee}", expr.loc)
        if len(resolved_callee.param_types) != len(expr.arguments):
            raise CompilerMessage(ErrorType.COMPILATION, f"Mismatched argument counts (expected {len(resolved_callee.param_types)}, got {len(expr.arguments)}):", expr.loc, [
                CompilerMessage(ErrorType.NOTE, f"Function declared here:", resolved_callee.loc)
            ])
        for param, argument in zip(resolved_callee.param_types, expr.arguments):
            self.unify_expr(argument, param.type, param.loc)
        expr.yield_type, _ = self.unify_type(resolved_callee.ret_type, bound, expr.loc, bound_loc)
        return expr.yield_type

    def unify_attr_expr(self, expr: IRAttrExpr, bound: IRResolvedType | None, bound_loc: Location | None) -> IRResolvedType:
        resolved_object = self.unify_expr(expr.object, None, None)
        if not isinstance(resolved_object, IRStructType):
            raise CompilerMessage(ErrorType.COMPILATION, f"Object must be a struct, is instead a {resolved_object}:", expr.loc)
        try:
            expr.index, field = next((index, field) for index, field in enumerate(resolved_object.struct.fields) if field.name == expr.attr)
        except StopIteration:
            raise CompilerMessage(ErrorType.COMPILATION, f"Object of type {resolved_object.struct.name} does not have a field named {expr.attr}:", expr.loc, [
                                      CompilerMessage(ErrorType.NOTE, f"{resolved_object.struct.name} defined here:", resolved_object.struct.loc)
                                  ]) from None

        expr.yield_type, _ = self.unify_type(cast(IRResolvedType, field.type), bound, expr.loc, bound_loc)
        return expr.yield_type

    def unify_binary_expr(self, expr: IRBinaryExpr, bound: IRResolvedType | None, bound_loc: Location | None) -> IRResolvedType:
        match expr.op:
            case "Add":
                left_type = self.unify_expr(expr.left, None, None)
                right_type = self.unify_expr(expr.right, None, None)
                if isinstance(left_type, IRIntegerType) and isinstance(right_type, IRIntegerType):
                    expr.yield_type, _ = self.unify_type(IRIntegerType(max(left_type.bits, right_type.bits)), bound, expr.loc, bound_loc)
                    return expr.yield_type
                else:
                    raise CompilerMessage(ErrorType.COMPILATION, f"Mismatched arguments to addition (left is {left_type}, right is {right_type}):", expr.loc)
            case "Sub":
                left_type = self.unify_expr(expr.left, None, None)
                right_type = self.unify_expr(expr.right, None, None)
                if isinstance(left_type, IRIntegerType) and isinstance(right_type, IRIntegerType):
                    expr.yield_type, _ = self.unify_type(IRIntegerType(max(left_type.bits, right_type.bits)), bound,
                                                         expr.loc, bound_loc)
                    return expr.yield_type
                else:
                    raise CompilerMessage(ErrorType.COMPILATION,
                                          f"Mismatched arguments to subtraction (left is {left_type}, right is {right_type}):",
                                          expr.loc)
            case "Mul":
                left_type = self.unify_expr(expr.left, None, None)
                right_type = self.unify_expr(expr.right, None, None)
                if isinstance(left_type, IRIntegerType) and isinstance(right_type, IRIntegerType):
                    expr.yield_type, _ = self.unify_type(IRIntegerType(max(left_type.bits, right_type.bits)), bound,
                                                         expr.loc, bound_loc)
                    return expr.yield_type
                else:
                    raise CompilerMessage(ErrorType.COMPILATION,
                                          f"Mismatched arguments to multiplication (left is {left_type}, right is {right_type}):",
                                          expr.loc)
            case "Div":
                left_type = self.unify_expr(expr.left, None, None)
                right_type = self.unify_expr(expr.right, None, None)
                if isinstance(left_type, IRIntegerType) and isinstance(right_type, IRIntegerType):
                    expr.yield_type, _ = self.unify_type(IRIntegerType(max(left_type.bits, right_type.bits)), bound,
                                                         expr.loc, bound_loc)
                    return expr.yield_type
                else:
                    raise CompilerMessage(ErrorType.COMPILATION,
                                          f"Mismatched arguments to division (left is {left_type}, right is {right_type}):",
                                          expr.loc)
            case "Mod":
                left_type = self.unify_expr(expr.left, None, None)
                right_type = self.unify_expr(expr.right, None, None)
                if isinstance(left_type, IRIntegerType) and isinstance(right_type, IRIntegerType):
                    expr.yield_type, _ = self.unify_type(IRIntegerType(max(left_type.bits, right_type.bits)), bound,
                                                         expr.loc, bound_loc)
                    return expr.yield_type
                else:
                    raise CompilerMessage(ErrorType.COMPILATION,
                                          f"Mismatched arguments to modulus (left is {left_type}, right is {right_type}):",
                                          expr.loc)
            case "Less" | "Greater" | "LessEqual" | "GreaterEqual" | "Equal" | "NotEqual":
                left_type = self.unify_expr(expr.left, None, None)
                right_type = self.unify_expr(expr.right, None, None)
                if isinstance(left_type, IRIntegerType) and isinstance(right_type, IRIntegerType):
                    expr.yield_type = IRBoolType()
                    return expr.yield_type
                else:
                    raise CompilerMessage(ErrorType.COMPILATION, f"Mismatched arguments to comparison (left is {left_type}, right is {right_type}):", expr.loc)
            case _:
                raise ValueError(expr.op)

    def unify_if_expr(self, expr: IRIf, bound: IRResolvedType | None, bound_loc: Location | None) -> IRResolvedType:
        self.unify_expr(expr.cond, IRBoolType(), None)
        result_type = self.unify_expr(expr.then_do, bound, bound_loc)
        if expr.else_do is not None:
            else_result = self.unify_expr(expr.else_do, bound, bound_loc)
        else:
            else_result = IRUnitType()
        if else_result.is_subtype(result_type):
            pass
        elif result_type.is_subtype(else_result):
            result_type = else_result
        else:
            raise CompilerMessage(ErrorType.COMPILATION, f"The if expression's branches do not have reconcilable result types (then's is {result_type}, else's is {result_type}):", expr.loc)
        expr.yield_type = result_type
        return expr.yield_type

    def unify_block_expr(self, expr: IRBlock, bound: IRResolvedType | None, bound_loc: Location | None) -> IRResolvedType:
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
        return expr.yield_type

    def unify_assign(self, expr: IRAssign, bound: IRResolvedType | None, bound_loc: Location | None) -> IRResolvedType:
        resolved_name = self.resolve_type(expr.name.type)
        if resolved_name is None:
            raise ValueError()
        expr.yield_type = self.unify_expr(expr.value, bound, bound_loc)
        self.unify_type(expr.yield_type, resolved_name, expr.value.loc, expr.name.location)
        return expr.yield_type

    def unify_attr_assign(self, expr: IRAttrAssign, bound: IRResolvedType | None, bound_loc: Location | None) -> IRResolvedType:
        resolved_object = self.unify_expr(expr.obj, None, None)
        if not isinstance(resolved_object, IRStructType):
            raise CompilerMessage(ErrorType.COMPILATION, f"Object must be a struct, is instead a {resolved_object}:", expr.loc)
        try:
            expr.index, field = next((index, field) for index, field in enumerate(resolved_object.struct.fields) if field.name == expr.attr)
        except StopIteration:
            raise CompilerMessage(ErrorType.COMPILATION, f"Object of type {resolved_object.struct.name} does not have a field named {expr.attr}:", expr.loc, [
                                      CompilerMessage(ErrorType.NOTE, f"{resolved_object.struct.name} defined here:", resolved_object.struct.loc)
                                  ]) from None

        expr.yield_type = self.unify_expr(expr.value, bound, bound_loc)

        self.unify_type(expr.yield_type, cast(IRResolvedType, field.type), expr.value.loc, field.loc)
        return expr.yield_type

    def unify_lambda(self, expr: IRLambda, bound: IRResolvedType | None, bound_loc: Location | None) -> IRResolvedType:
        if isinstance(bound, IRFunctionType):
            if len(expr.parameters) != len(bound.param_types):
                raise CompilerMessage(ErrorType.COMPILATION, f"Mismatched argument counts (expected {len(bound.param_types)}, got {len(expr.parameters)}):", expr.loc, [
                    CompilerMessage(ErrorType.NOTE, f"Expectation is derived from here:", bound_loc)
                ])
            for param, expected_param in zip(expr.parameters, bound.param_types):
                param.type, _ = self.unify_type(self.resolve_type(param.type), expected_param.type, param.loc, expected_param.loc)
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

        expr.yield_type = IRFunctionType([IRParameterType(param.type, param.loc) for param in expr.parameters], expr.ret_type).set_loc(expr.loc)
        self.unify_type(expr.yield_type, bound, expr.loc, bound_loc)
        return expr.yield_type

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
        if isinstance(type, IRTypeVarType):
            if type in self.substitutions.value:
                return self.substitutions.value[type]
            else:
                return type
        elif isinstance(type, IRResolvedType):
            return type
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
                if not isinstance(generic_type, IRGenericStructType):
                    raise ValueError()
                type_args = [self.resolve_type(type_arg) for type_arg in type.type_args]
                resolved = self.resolve_generic_struct(generic_type.generic, {type_var.type_decl.type: arg for type_var, arg in zip(generic_type.generic.type_vars, type_args)}, type.loc)
                # noinspection PyTypeChecker
                return resolved.type_decl.type
            elif isinstance(type, IRUnresolvedFunctionType):
                return IRFunctionType([IRParameterType(self.resolve_type(param), param.loc) for param in type.parameters], self.resolve_type(type.ret_type)).set_loc(type.loc)
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
            return IRFunctionType([IRParameterType(self.substitute_type(self.inferrer.resolve_type(param)), param.loc) for param in type.parameters],
                                  self.substitute_type(self.inferrer.resolve_type(type.ret_type))).set_loc(type.loc)
        elif isinstance(type, IRUnresolvedGenericType):
            return self.inferrer.resolve_type(type)
        elif isinstance(type, IRFunctionType):
            return IRFunctionType([IRParameterType(self.substitute_type(param.type), param.loc) for param in type.param_types],
                                  self.substitute_type(type.ret_type)).set_loc(type.loc)
        elif isinstance(type, IRGenericFunctionType):
            raise ValueError()
        elif isinstance(type, IRStructType):
            return type
        elif isinstance(type, IRGenericStructType):
            if any(type_var.type_decl.type in self.substitutions for type_var in type.generic.type_vars):
                resolved = self.inferrer.resolve_generic_struct(type.generic, {type_var.type_decl.type: self.substitute_type(arg.type_decl.type) for type_var, arg in zip(type.generic.type_vars, type.generic.type_vars)}, type.loc)
                return cast(IRResolvedType, resolved.type_decl.type)
            else:
                return type
        else:
            raise ValueError(type.__class__)
