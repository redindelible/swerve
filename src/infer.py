from __future__ import annotations

from ir import *
from common import BuiltinLocation, CompilerMessage, ErrorType, Location, Path


def infer_types(program: IRProgram):
    inferrer = BidirectionalTypeInference(program)
    inferrer.infer_types()


class BidirectionalTypeInference:
    def __init__(self, program: IRProgram):
        self.program = program

        self.expected_return_type: IRResolvedType | None = None

    def infer_types(self):
        for function in self.program.functions:
            self.infer_function_types(function)

        for function in self.program.functions:
            self.infer_function_bodies(function)

    def infer_function_types(self, function: IRFunction):
        param_types = []
        for param in function.parameters:
            resolved = self.resolve_type(param.type)
            if resolved is None:
                raise ValueError()
            param_types.append(resolved)
            param.type = resolved
            param.decl.type = resolved

        resolved = self.resolve_type(function.return_type)
        if resolved is None:
            raise ValueError()
        function.return_type = resolved

        function.function_type = function.decl.type = IRFunctionType(param_types, resolved)

    def infer_function_bodies(self, function: IRFunction):
        self.expected_return_type = function.return_type

        for stmt in function.body.body:
            self.infer_stmt(stmt)

        self.expected_return_type = None

    def infer_stmt(self, stmt: IRStmt):
        if isinstance(stmt, IRDeclStmt):
            self.infer_decl_stmt(stmt)
        elif isinstance(stmt, IRReturnStmt):
            self.infer_return_stmt(stmt)
        else:
            raise ValueError(type(stmt))

    def infer_decl_stmt(self, stmt: IRDeclStmt):
        resolved_decl = self.resolve_type(stmt.type)
        type = self.unify_expr(stmt.init, resolved_decl)
        if resolved_decl is None:
            resolved_decl = type
        stmt.type = resolved_decl
        stmt.decl.type = resolved_decl

    def infer_return_stmt(self, stmt: IRReturnStmt):
        self.unify_expr(stmt.expr, self.expected_return_type)

    def unify_expr(self, expr: IRExpr, bound: IRResolvedType | None) -> IRResolvedType:
        if isinstance(expr, IRIntegerExpr):
            return self.unify_integer_expr(expr, bound)
        elif isinstance(expr, IRStringExpr):
            return self.unify_string_expr(expr, bound)
        elif isinstance(expr, IRNameExpr):
            return self.unify_name_expr(expr, bound)
        else:
            raise ValueError(type(expr))

    def unify_integer_expr(self, expr: IRIntegerExpr, bound: IRResolvedType | None) -> IRResolvedType:
        expr.yield_type, _ = self.unify_type(IRIntegerType(64), bound)
        return expr.yield_type

    def unify_string_expr(self, expr: IRStringExpr, bound: IRResolvedType | None) -> IRResolvedType:
        expr.yield_type, _ = self.unify_type(IRStringType(), bound)
        return expr.yield_type

    def unify_name_expr(self, expr: IRNameExpr, bound: IRResolvedType | None) -> IRResolvedType:
        resolved_name = self.resolve_type(expr.name.type)
        if resolved_name is None:
            raise ValueError()
        expr.yield_type, _ = self.unify_type(resolved_name, bound)
        return expr.yield_type

    def unify_type(self, yield_type: IRResolvedType | None, bound_type: IRResolvedType | None) -> tuple[IRResolvedType, IRResolvedType]:
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
                raise CompilerMessage(ErrorType.COMPILATION, "Could not unify types")

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
