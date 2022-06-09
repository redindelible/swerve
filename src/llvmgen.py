from __future__ import annotations

from swc_ir import *
from llvmlite import ir
from llvmlite import binding as llvm


def generate_llvm(program: IRProgram) -> ir.Module:
    llvm.initialize()
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()

    gen = LLVMGen(program)
    gen.load_external_functions()
    gen.load_structs()
    gen.generate_functions()
    return gen.module


class LLVMGen:
    def __init__(self, program: IRProgram):
        self.program = program
        self.module = ir.Module()
        self.target_data = llvm.Target.from_default_triple().create_target_machine(codemodel="default").target_data

        self.void_type = ir.VoidType()
        self.void_p_type = ir.PointerType(ir.IntType(8))
        self.integer_types: dict[int, ir.IntType] = {
            32: ir.IntType(32),
            64: ir.IntType(64),
        }
        self.bool_type = ir.IntType(1)
        self.false = ir.Constant(self.bool_type, 0)
        self.true = ir.Constant(self.bool_type, 1)
        self.unit_type = ir.IntType(1)
        self.unit = ir.Constant(self.unit_type, 0)
        self.external_functions: dict[str, ir.Function] = {}

        self.struct_types: dict[IRStructType, ir.IdentifiedStructType] = {}

        self.builder = ir.IRBuilder()
        self.decl_values: dict[IRValueDecl, ir.Value] = {}

    def load_external_functions(self):
        self.external_functions["malloc"] = ir.Function(self.module, ir.FunctionType(self.void_p_type, [self.integer_types[64]]), "malloc")

    def size_of(self, type: ir.Type) -> int:
        return type.get_abi_size(self.target_data)

    def load_structs(self):
        for struct in self.program.structs:
            struct_type = self.module.context.get_identified_type(struct.name)
            # noinspection PyTypeChecker
            self.struct_types[struct.type_decl.type] = ir.PointerType(struct_type)

        for struct in self.program.structs:
            if not isinstance(struct, IRGenericStruct):
                # noinspection PyTypeChecker
                struct_p_type: ir.PointerType = self.struct_types[struct.type_decl.type]
                struct_type: ir.IdentifiedStructType = struct_p_type.pointee
                struct_type.set_body(*(self.generate_type(field.type) for field in struct.fields))

                self.generate_constructor(struct, struct_p_type)

    def generate_constructor(self, struct: IRStruct, struct_type: ir.PointerType):
        constructor_type = ir.FunctionType(struct_type, [self.generate_type(field.type) for field in struct.fields])
        constructor = self.decl_values[struct.constructor] = ir.Function(self.module, constructor_type, f"{struct.name}_constructor")

        self.builder = ir.IRBuilder(constructor.append_basic_block("entry"))

        mem = self.builder.call(self.external_functions["malloc"], [ir.Constant(ir.IntType(64), self.size_of(struct_type.pointee))])
        obj = self.builder.bitcast(mem, struct_type)

        for index, arg in enumerate(constructor.args):
            field_ptr = self.builder.gep(obj, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), index)])
            self.builder.store(arg, field_ptr)

        self.builder.ret(obj)

    def generate_functions(self):
        for function in self.program.functions:
            self.generate_function(function)

    def generate_function(self, function: IRFunction):
        ir_func_type = function.function_type
        func_type = ir.FunctionType(self.generate_type(ir_func_type.ret_type), [self.generate_type(param_type) for param_type, _ in ir_func_type.param_types])
        func = ir.Function(self.module, func_type, function.name)   # TODO mangling

        self.decl_values[function.decl] = func
        for ir_arg, llvm_arg in zip(function.parameters, func.args):
            self.decl_values[ir_arg.decl] = llvm_arg

        entry_block = func.append_basic_block("entry")
        self.builder = ir.IRBuilder(entry_block)
        for stmt in function.body.body:
            self.generate_stmt(stmt)

        if self.builder.block.terminator is None:
            self.builder.unreachable()
        self.builder = ir.IRBuilder()

    def generate_stmt(self, stmt: IRStmt):
        if isinstance(stmt, IRDeclStmt):
            self.generate_decl_stmt(stmt)
        elif isinstance(stmt, IRReturnStmt):
            self.generate_return_stmt(stmt)
        elif isinstance(stmt, IRExprStmt):
            self.generate_expr(stmt.expr)
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
        elif isinstance(expr, IRGenericExpr):
            return self.generate_generic_expr(expr)
        elif isinstance(expr, IRBinaryExpr):
            return self.generate_binary_expr(expr)
        elif isinstance(expr, IRIf):
            return self.generate_if_expr(expr)
        elif isinstance(expr, IRBlock):
            return self.generate_block_expr(expr)
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

    def generate_generic_expr(self, expr: IRGenericExpr) -> ir.Value:
        return self.generate_expr(expr.replacement_expr)

    def generate_binary_expr(self, expr: IRBinaryExpr) -> ir.Value:
        match expr.op:
            case "Add":
                return self.builder.add(self.generate_expr(expr.left), self.generate_expr(expr.right))
            case "Less":
                return self.builder.icmp_signed("<", self.generate_expr(expr.left), self.generate_expr(expr.right))
            case _:
                raise ValueError(expr.op)

    def generate_if_expr(self, expr: IRIf) -> ir.Value:
        cond = self.generate_expr(expr.cond)
        if expr.else_do is None:
            before_block = self.builder.block
            with self.builder.if_then(cond) as then:
                with then:
                    then_block = self.builder.block
                    then_result = self.generate_expr(expr.then_do)
            result = self.builder.phi(self.generate_type(expr.yield_type))
            result.add_incoming(then_result, then_block)
            result.add_incoming(self.unit, before_block)
        else:
            with self.builder.if_else(cond) as (then, else_):
                with then:
                    then_block = self.builder.block
                    then_result = self.generate_expr(expr.then_do)
                with else_:
                    else_block = self.builder.block
                    else_result = self.generate_expr(expr.else_do)
            result = self.builder.phi(self.generate_type(expr.yield_type))
            result.add_incoming(then_result, then_block)
            result.add_incoming(else_result, else_block)
        return result

    def generate_block_expr(self, expr: IRBlock) -> ir.Value:
        last_result = None
        for stmt in expr.body:
            if isinstance(stmt, IRExprStmt):
                last_result = self.generate_expr(stmt.expr)
            else:
                self.generate_stmt(stmt)
        if last_result is None:
            return self.unit
        else:
            return last_result

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
        elif isinstance(type, IRUnitType):
            return self.unit_type
        elif isinstance(type, IRBoolType):
            return self.bool_type
        else:
            raise ValueError(type)