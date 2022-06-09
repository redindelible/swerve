from __future__ import annotations

from typing import cast

from swc_ir import *
from common import CompilerMessage, ErrorType, Location


def infer_types(program: IRProgram):
    inferrer = BidirectionalTypeInference(program)
    inferrer.infer_types()


class BidirectionalTypeInference:
    def __init__(self, program: IRProgram):
        self.program = program

        self.expected_return_type: IRResolvedType | None = None
        self.expected_return_loc: Location | None = None

    def resolve_generic(self, generic: IRGenericStruct, arguments: list[IRResolvedType], loc: Location) -> IRStruct:
        if len(arguments) != len(generic.type_vars):
            raise CompilerMessage(ErrorType.COMPILATION, f"Mismatched number of arguments to generic (expected {len(generic.type_vars)}, got {len(arguments)}):", loc, [
                CompilerMessage(ErrorType.NOTE, f"Generic defined here:", generic.loc)
            ])

        if tuple(arguments) in generic.reifications:
            return generic.reifications[tuple(arguments)]

        if any(isinstance(arg, IRTypeVarType) for arg in arguments):
            raise ValueError()
        else:
            struct = IRStruct(
                IRTypeDecl(IRUnresolvedUnknownType(), generic.type_decl.location),
                IRValueDecl(IRUnresolvedUnknownType(), generic.constructor.location),
                f"{generic.name}[{', '.join(str(arg) for arg in arguments)}]",
                generic.supertraits,
                [IRField(field.name, field.type).set_loc(field.loc) for field in generic.fields],
                generic.methods
            ).set_loc(loc)

            type_var_replacements = dict(zip((type_var.type_decl.type for type_var in generic.type_vars), arguments))

            for field in struct.fields:
                if field.type in type_var_replacements:
                    field.type = type_var_replacements[field.type]
                    field.loc = loc

            struct.type_decl.type = IRStructType(struct).set_loc(loc)
            # noinspection PyTypeChecker
            struct.constructor.type = IRFunctionType([(field.type, field.loc) for field in struct.fields], struct.type_decl.type).set_loc(loc)

            self.program.structs.append(struct)
            generic.reifications[tuple(arguments)] = struct
            return struct

    def infer_types(self):
        for struct in self.program.structs:
            self.infer_struct_type(struct)

        for struct in self.program.structs:
            self.infer_struct_body(struct)

        for function in self.program.functions:
            self.infer_function_type(function)

        for function in self.program.functions:
            self.infer_function_body(function)

    def infer_struct_type(self, struct: IRStruct):
        if isinstance(struct, IRGenericStruct):
            struct.type_decl.type = IRGenericStructType(struct)
        else:
            struct.type_decl.type = IRStructType(struct)

    def infer_struct_body(self, struct: IRStruct):
        if isinstance(struct, IRGenericStruct):
            for type_var in struct.type_vars:
                type_var.type_decl.type = IRTypeVarType(type_var)
        field_types: list[tuple[IRResolvedType, Location]] = []
        for field in struct.fields:
            field.type = resolved_type = self.resolve_type(field.type)
            if resolved_type is None:
                raise ValueError()
            field_types.append((resolved_type, field.loc))

        if isinstance(struct, IRGenericStruct):
            def callback(type_args: list[IRResolvedType], loc: Location) -> tuple[IRFunctionType, IRExpr]:
                resultant = self.resolve_generic(cast(IRGenericStruct, struct), type_args, loc)
                return cast(IRFunctionType, resultant.constructor.type), IRNameExpr(resultant.constructor)

            # noinspection PyTypeChecker
            struct.constructor.type = IRGenericFunctionType(struct.type_vars, field_types, struct.type_decl.type, callback).set_loc(struct.loc)
        else:
            # noinspection PyTypeChecker
            struct.constructor.type = IRFunctionType(field_types, struct.type_decl.type).set_loc(struct.loc)

    def infer_function_type(self, function: IRFunction):
        param_types: list[tuple[IRResolvedType, Location]] = []
        for param in function.parameters:
            resolved = self.resolve_type(param.type)
            if resolved is None:
                raise ValueError()
            param_types.append((resolved, param.loc))
            param.type = resolved
            param.decl.type = resolved

        resolved = self.resolve_type(function.return_type)
        if resolved is None:
            raise ValueError()
        function.return_type = resolved

        function.function_type = function.decl.type = IRFunctionType(param_types, resolved).set_loc(function.loc)

    def infer_function_body(self, function: IRFunction):
        self.expected_return_type = function.return_type
        self.expected_return_loc = function.return_type

        for stmt in function.body.body:
            self.infer_stmt(stmt)

        self.expected_return_type = None
        self.expected_return_loc = None

    def infer_stmt(self, stmt: IRStmt):
        if isinstance(stmt, IRDeclStmt):
            self.infer_decl_stmt(stmt)
        elif isinstance(stmt, IRReturnStmt):
            self.infer_return_stmt(stmt)
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
        self.unify_expr(stmt.expr, self.expected_return_type, self.expected_return_loc)

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
        else:
            raise ValueError(type(expr))

    def unify_integer_expr(self, expr: IRIntegerExpr, bound: IRResolvedType | None, bound_loc: Location | None) -> IRResolvedType:
        expr.yield_type, _ = self.unify_type(IRIntegerType(64), bound, expr.loc, bound_loc)
        return expr.yield_type

    def unify_string_expr(self, expr: IRStringExpr, bound: IRResolvedType | None, bound_loc: Location | None) -> IRResolvedType:
        expr.yield_type, _ = self.unify_type(IRStringType(), bound, expr.loc, bound_loc)
        return expr.yield_type

    def unify_name_expr(self, expr: IRNameExpr, bound: IRResolvedType | None, bound_loc: Location | None) -> IRResolvedType:
        resolved_name = self.resolve_type(expr.name.type)
        if resolved_name is None:
            raise ValueError()
        expr.yield_type, _ = self.unify_type(resolved_name, bound, expr.loc, bound_loc)
        return expr.yield_type

    def unify_call_expr(self, expr: IRCallExpr, bound: IRResolvedType | None, bound_loc: Location | None) -> IRResolvedType:
        resolved_callee = self.unify_expr(expr.callee, None, None)
        if not isinstance(resolved_callee, IRFunctionType):
            raise CompilerMessage(ErrorType.COMPILATION, f"Callee must be a function, is instead a {resolved_callee}", expr.loc)
        if len(resolved_callee.param_types) != len(expr.arguments):
            raise CompilerMessage(ErrorType.COMPILATION, f"Mismatched argument counts (expected {len(resolved_callee.param_types)}, got {len(expr.arguments)}):", expr.loc, [
                CompilerMessage(ErrorType.NOTE, f"Function declared here:", resolved_callee.loc)
            ])
        for (param, param_loc), argument in zip(resolved_callee.param_types, expr.arguments):
            self.unify_expr(argument, param, param_loc)
        expr.yield_type, _ = self.unify_type(resolved_callee.ret_type, bound, expr.loc, bound_loc)
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
            case _:
                raise ValueError()

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
                    raise CompilerMessage(ErrorType.COMPILATION, f"Could not unify types. Expected {bound_type}, got {yield_type}", yield_loc)

    def resolve_type(self, type: IRType) -> IRResolvedType | None:
        if isinstance(type, IRResolvedType):
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
                resolved = self.resolve_generic(generic_type.generic, type_args, type.loc)
                # noinspection PyTypeChecker
                return resolved.type_decl.type
            else:
                raise ValueError(type)
