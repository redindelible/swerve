from __future__ import annotations

from swc_ir import *
from common import BuiltinLocation, CompilerMessage, ErrorType, Location, Path
from llvmlite import ir


def generate_llvm(program: IRProgram) -> ir.Module:
    gen = LLVMGen(program)
    gen.load_structs()
    gen.generate_functions()
    return gen.module


class LLVMGen:
    def __init__(self, program: IRProgram):
        self.program = program
        self.module = ir.Module()

        self.integer_types: dict[int, ir.IntType] = {}
        self.struct_types: dict[IRStructType, ir.IdentifiedStructType] = {}

        self.builder = ir.IRBuilder()
        self.decl_values: dict[IRValueDecl, ir.Value] = {}

    def load_structs(self):
        for struct in self.program.structs:
            struct_type = self.module.context.get_identified_type(struct.name)
            # noinspection PyTypeChecker
            self.struct_types[struct.type_decl.type] = ir.PointerType(struct_type)

        for struct in self.program.structs:
            # noinspection PyTypeChecker
            struct_p_type: ir.PointerType = self.struct_types[struct.type_decl.type]
            struct_type: ir.IdentifiedStructType = struct_p_type.pointee
            struct_type.set_body(*(self.generate_type(field) for field in struct.fields.values()))

            self.generate_constructor(struct, struct_p_type)

    def generate_constructor(self, struct: IRStruct, struct_type: ir.PointerType):
        constructor_type = ir.FunctionType(struct_type, [self.generate_type(field) for field in struct.fields.values()])
        constructor = self.decl_values[struct.constructor] = ir.Function(self.module, constructor_type, f"{struct.name}_constructor")

        self.builder = ir.IRBuilder(constructor.append_basic_block("entry"))
        obj = self.builder.alloca(struct_type.pointee)
        self.builder.ret(obj)

    def generate_functions(self):
        for function in self.program.functions:
            self.generate_function(function)

    def generate_function(self, function: IRFunction):
        ir_func_type = function.function_type
        func_type = ir.FunctionType(self.generate_type(ir_func_type.ret_type), [self.generate_type(param_type) for param_type in ir_func_type.param_types])
        func = ir.Function(self.module, func_type, function.name)   # TODO mangling

        self.builder = ir.IRBuilder(func.append_basic_block("entry"))
        for stmt in function.body.body:
            self.generate_stmt(stmt)

        self.builder = ir.IRBuilder()

    def generate_stmt(self, stmt: IRStmt):
        if isinstance(stmt, IRDeclStmt):
            self.generate_decl_stmt(stmt)
        elif isinstance(stmt, IRReturnStmt):
            self.generate_return_stmt(stmt)
        else:
            raise ValueError(type(stmt))

    def generate_decl_stmt(self, stmt: IRDeclStmt):
        value = self.decl_values[stmt.decl] = self.builder.alloca(self.generate_type(stmt.type))
        self.builder.store(self.generate_expr(stmt.init), value)

    def generate_return_stmt(self, stmt: IRReturnStmt):
        self.builder.ret(self.generate_expr(stmt.expr))

    def generate_expr(self, expr: IRExpr) -> ir.Value:
        if isinstance(expr, IRIntegerExpr):
            return self.generate_integer_expr(expr)
        elif isinstance(expr, IRNameExpr):
            return self.generate_name_expr(expr)
        elif isinstance(expr, IRCallExpr):
            return self.generate_call_expr(expr)
        elif isinstance(expr, IRAttrExpr):
            return self.generate_attr_expr(expr)
        else:
            raise ValueError(type(expr))

    def generate_integer_expr(self, expr: IRIntegerExpr) -> ir.Value:
        return ir.Constant(self.generate_type(expr.yield_type), expr.number)

    def generate_name_expr(self, expr: IRNameExpr) -> ir.Value:
        name = self.decl_values[expr.name]
        if isinstance(name.type, ir.PointerType) and not isinstance(name.type.pointee, ir.FunctionType):
            return self.builder.load(name)
        else:
            return name

    def generate_call_expr(self, expr: IRCallExpr) -> ir.Value:
        return self.builder.call(self.generate_expr(expr.callee), [self.generate_expr(arg) for arg in expr.arguments])

    def generate_attr_expr(self, expr: IRAttrExpr) -> ir.Value:
        object = self.generate_expr(expr.object)
        element_pointer = self.builder.gep(object, (ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), expr.index),))
        return self.builder.load(element_pointer)

    def generate_type(self, type: IRType) -> ir.Type:
        if not isinstance(type, IRResolvedType):
            raise ValueError()
        if isinstance(type, IRIntegerType):
            if type.bits in self.integer_types:
                return self.integer_types[type.bits]
            else:
                return self.integer_types.setdefault(type.bits, ir.IntType(type.bits))
        elif isinstance(type, IRStructType):
            return self.struct_types[type]
        else:
            raise ValueError(type)