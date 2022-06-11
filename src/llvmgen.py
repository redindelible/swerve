from __future__ import annotations

from typing import cast

from swc_ir import *
from llvmlite import ir
from llvmlite import binding as llvm

from random import shuffle


def generate_llvm(program: IRProgram) -> ir.Module:
    llvm.initialize()
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()

    gen = LLVMGen(program)
    gen.load_external_functions()
    gen.load_structs()
    gen.generate_functions()
    gen.finalize()
    return gen.module


class Closure:
    def __init__(self, value: ir.Value, structure: ir.LiteralStructType, from_block: IRBlock):
        self.value = value
        self.structure = structure
        self.from_block = from_block


class LLVMGen:
    def __init__(self, program: IRProgram):
        self.program = program
        self.module = ir.Module()
        self.target_data = llvm.Target.from_default_triple().create_target_machine(codemodel="default").target_data

        self.void_type = ir.VoidType()
        self.void_p_type: ir.Type = ir.PointerType(ir.IntType(8))
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

        self.builder = ir.IRBuilder()

        self.closures: list[Closure] = []
        self.recent_closure: list[ir.Value] = []
        self.current_block: IRBlock | None = None
        self.function_ir: dict[IRFunction, ir.Function] = {}
        self.decl_values: dict[IRValueDecl, ir.Value] = {}
        self.struct_types: dict[IRStructType, ir.PointerType] = {}

        self.counter: list[int] = list(range(0, 1000000))
        shuffle(self.counter)

    def new_name(self, pattern: str) -> str:
        num = self.counter.pop()
        return f"{pattern}_{num:0>6}"

    def load_external_functions(self):
        self.external_functions["malloc"] = ir.Function(self.module, ir.FunctionType(self.void_p_type, [self.integer_types[64]]), "malloc")

    def size_of(self, type: ir.Type) -> int:
        return type.get_abi_size(self.target_data)

    def gep(self, pointer: ir.Value, indices: list[int]) -> ir.Value:
        return self.builder.gep(pointer, [ir.Constant(ir.IntType(32), index) for index in indices])

    def finalize(self):
        main = ir.Function(self.module, ir.FunctionType(self.integer_types[64], []), "main")
        self.builder = ir.IRBuilder(main.append_basic_block("entry"))

        fn_struct_p = self.decl_values[self.program.main_func.decl]
        fn_ptr = self.builder.load(self.gep(fn_struct_p, [0, 0]))
        closure_ptr = self.builder.load(self.gep(fn_struct_p, [0, 1]))
        self.builder.ret(self.builder.call(fn_ptr, [closure_ptr] + list(main.args)))

    def load_structs(self):
        for struct in self.program.structs:
            if not isinstance(struct, IRGenericStruct):
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
        constructor_type = ir.FunctionType(struct_type, [self.void_p_type] + [self.generate_type(field.type) for field in struct.fields])
        constructor = ir.Function(self.module, constructor_type, self.new_name(f"{struct.name}_constructor"))

        func_value = ir.GlobalVariable(self.module, cast(ir.PointerType, self.generate_type(struct.constructor.type)).pointee, f"obj_{constructor.name}")
        func_value.global_constant = True
        func_value.initializer = ir.Constant(func_value.type.pointee, [constructor, ir.Constant(self.void_p_type, None)])

        self.decl_values[struct.constructor] = func_value

        self.builder = ir.IRBuilder(constructor.append_basic_block("entry"))

        mem = self.builder.call(self.external_functions["malloc"], [ir.Constant(ir.IntType(64), self.size_of(struct_type.pointee))])
        obj = self.builder.bitcast(mem, struct_type)

        for index, arg in enumerate(constructor.args[1:]):
            field_ptr = self.builder.gep(obj, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), index)])
            self.builder.store(arg, field_ptr)

        self.builder.ret(obj)

    def generate_functions(self):
        for function in self.program.functions:
            if not isinstance(function, IRGenericFunction):
                self.generate_function_header(function)

        for function in self.program.functions:
            if not isinstance(function, IRGenericFunction):
                self.generate_function(function)

    def generate_function_header(self, function: IRFunction):
        ir_func_type = function.function_type
        func_type = ir.FunctionType(self.generate_type(ir_func_type.ret_type), [self.void_p_type] + [self.generate_type(param_type.type) for param_type in ir_func_type.param_types])
        func = ir.Function(self.module, func_type, self.new_name(function.name))

        func_value = ir.GlobalVariable(self.module, cast(ir.PointerType, self.generate_type(ir_func_type)).pointee, f"obj_{func.name}")
        func_value.global_constant = True
        func_value.initializer = ir.Constant(func_value.type.pointee, [func, ir.Constant(self.void_p_type, None)])
        self.decl_values[function.decl] = func_value
        self.function_ir[function] = func

    def generate_function(self, function: IRFunction):
        func = self.function_ir[function]

        entry_block = func.append_basic_block("entry")
        self.builder = ir.IRBuilder(entry_block)

        self.current_block = function.body
        count = 1
        closed: list[IRValueDecl] = []
        for decl in function.body.declared:
            if decl.put_in_closure:
                closed.append(decl)
                decl.closure_index = count
                count += 1
        # print(function.body.declared)
        if len(closed) > 0:
            closure_type = ir.LiteralStructType([self.void_p_type] + [self.generate_type(var.type) for var in closed])
            closure = self.builder.call(self.external_functions["malloc"], [ir.Constant(self.integer_types[64], self.size_of(closure_type))])
            closure = self.builder.bitcast(closure, ir.PointerType(closure_type))
            self.recent_closure.append(closure)
            self.builder.store(ir.Constant(self.void_p_type, None), self.gep(closure, [0, 0]))
            self.closures.append(Closure(closure, closure_type, function.body))

        for ir_arg, llvm_arg in zip(function.parameters, func.args[1:]):
            if ir_arg.decl.put_in_closure:
                closure_ptr = self.builder.gep(self.closures[-1].value, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), ir_arg.decl.closure_index)])
                self.builder.store(llvm_arg, closure_ptr)
            else:
                arg_slot = self.decl_values[ir_arg.decl] = self.builder.alloca(self.generate_type(ir_arg.type))
                self.builder.store(llvm_arg, arg_slot)

        for stmt in function.body.body:
            self.generate_stmt(stmt)

        self.current_block = None
        if len(closed) > 0:
            self.closures.pop()
            self.recent_closure.pop()

        if self.builder.block.terminator is None:
            if function.body.always_returns():
                self.builder.unreachable()
            else:
                self.builder.ret(self.unit)
        self.builder = ir.IRBuilder()

    def generate_stmt(self, stmt: IRStmt):
        if isinstance(stmt, IRDeclStmt):
            self.generate_decl_stmt(stmt)
        elif isinstance(stmt, IRReturnStmt):
            self.generate_return_stmt(stmt)
        elif isinstance(stmt, IRExprStmt):
            self.generate_expr(stmt.expr)
        elif isinstance(stmt, IRWhileStmt):
            self.generate_while_stmt(stmt)
        else:
            raise ValueError(type(stmt))

    def generate_decl_stmt(self, stmt: IRDeclStmt):
        if stmt.decl.put_in_closure:
            self.decl_values[stmt.decl] = self.builder.gep(self.closures[-1].value, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), stmt.decl.closure_index)])
        else:
            self.decl_values[stmt.decl] = self.builder.alloca(self.generate_type(stmt.type))
        self.builder.store(self.generate_expr(stmt.init), self.decl_values[stmt.decl])

    def generate_return_stmt(self, stmt: IRReturnStmt):
        self.builder.ret(self.generate_expr(stmt.expr))

    def generate_while_stmt(self, stmt: IRWhileStmt):
        if self.builder.block.terminator is not None:
            return
        cond_block = self.builder.append_basic_block()
        body_block = self.builder.append_basic_block()
        after_block = self.builder.append_basic_block()
        self.builder.branch(cond_block)
        self.builder.position_at_start(cond_block)
        cond = self.generate_expr(stmt.cond)
        self.builder.cbranch(cond, body_block, after_block)
        self.builder.position_at_start(body_block)
        self.generate_expr(stmt.body)
        if self.builder.block.terminator is None:
            self.builder.branch(cond_block)
        self.builder.position_at_start(after_block)

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
        elif isinstance(expr, IRAssign):
            return self.generate_assign(expr)
        elif isinstance(expr, IRAttrAssign):
            return self.generate_attr_assign(expr)
        elif isinstance(expr, IRLambda):
            return self.generate_lambda(expr)
        else:
            raise ValueError(type(expr))

    def generate_integer_expr(self, expr: IRIntegerExpr) -> ir.Value:
        return ir.Constant(self.generate_type(expr.yield_type), expr.number)

    def generate_name_expr(self, expr: IRNameExpr) -> ir.Value:
        name = self.decl_values[expr.name]
        if isinstance(name, ir.GlobalValue):
            return name
        elif expr.name.in_block is not None:
            if expr.name.put_in_closure:
                current_closure = self.recent_closure[-1]
                for closure in reversed(self.closures):
                    if expr.name.in_block == closure.from_block:
                        return self.builder.load(self.gep(self.builder.bitcast(current_closure, ir.PointerType(closure.structure)), [0, expr.name.closure_index]))
                    else:
                        current_closure = self.builder.load(self.builder.bitcast(current_closure, ir.PointerType(ir.PointerType(ir.IntType(8)))))
                else:
                    raise ValueError()
            else:
                # print(type(name), expr.name)
                return self.builder.load(name)
        else:
            raise ValueError(name, expr.name)

    def generate_call_expr(self, expr: IRCallExpr) -> ir.Value:
        if expr.as_method_call is not None:
            return self.generate_method_call_expr(expr.as_method_call)
        fn_struct_p = self.generate_expr(expr.callee)
        fn_ptr = self.builder.load(self.gep(fn_struct_p, [0, 0]))
        closure_ptr = self.builder.load(self.gep(fn_struct_p, [0, 1]))
        return self.builder.call(fn_ptr, [closure_ptr] + [self.generate_expr(arg) for arg in expr.arguments])

    def generate_attr_expr(self, expr: IRAttrExpr) -> ir.Value:
        object = self.generate_expr(expr.object)
        element_pointer = self.builder.gep(object, (ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), expr.index),))
        return self.builder.load(element_pointer)

    def generate_method_call_expr(self, expr: IRMethodCallExpr) -> ir.Value:
        if expr.method.is_static:
            obj = self.generate_expr(expr.obj)

            func = expr.method.function
            fn_struct_p = self.decl_values[func.decl]
            fn_ptr = self.builder.load(self.gep(fn_struct_p, [0, 0]))
            closure_ptr = self.builder.load(self.gep(fn_struct_p, [0, 1]))

            arguments = [closure_ptr]
            if expr.method.is_self:
                arguments.append(obj)
            arguments.extend(self.generate_expr(arg) for arg in expr.arguments)
            return self.builder.call(fn_ptr, arguments)
        else:
            raise ValueError()

    def generate_generic_expr(self, expr: IRGenericExpr) -> ir.Value:
        return self.generate_expr(expr.replacement_expr)

    def generate_binary_expr(self, expr: IRBinaryExpr) -> ir.Value:
        match expr.op:
            case "Add":
                return self.builder.add(self.generate_expr(expr.left), self.generate_expr(expr.right))
            case "Sub":
                return self.builder.sub(self.generate_expr(expr.left), self.generate_expr(expr.right))
            case "Mul":
                return self.builder.mul(self.generate_expr(expr.left), self.generate_expr(expr.right))
            case "Div":
                return self.builder.sdiv(self.generate_expr(expr.left), self.generate_expr(expr.right))
            case "Mod":
                return self.builder.srem(self.generate_expr(expr.left), self.generate_expr(expr.right))
            case "Less":
                return self.builder.icmp_signed("<", self.generate_expr(expr.left), self.generate_expr(expr.right))
            case "Greater":
                return self.builder.icmp_signed(">", self.generate_expr(expr.left), self.generate_expr(expr.right))
            case "LessEqual":
                return self.builder.icmp_signed("<=", self.generate_expr(expr.left), self.generate_expr(expr.right))
            case "GreaterEqual":
                return self.builder.icmp_signed(">=", self.generate_expr(expr.left), self.generate_expr(expr.right))
            case "Equal":
                return self.builder.icmp_signed("==", self.generate_expr(expr.left), self.generate_expr(expr.right))
            case "NotEqual":
                return self.builder.icmp_signed("!=", self.generate_expr(expr.left), self.generate_expr(expr.right))
            case _:
                raise ValueError(expr.op)

    def generate_if_expr(self, expr: IRIf) -> ir.Value:
        cond = self.generate_expr(expr.cond)
        if expr.else_do is None:
            before_block = self.builder.block
            with self.builder.if_then(cond) as then:
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
        old_block, self.current_block = self.current_block, expr

        count = 1
        closed: list[IRValueDecl] = []
        for decl in expr.declared:
            if decl.put_in_closure:
                closed.append(decl)
                decl.closure_index = count
                count += 1
        if len(closed) > 0:
            closure_type = ir.LiteralStructType([self.void_p_type] + [self.generate_type(var.type) for var in closed])
            closure = self.builder.call(self.external_functions["malloc"], [ir.Constant(self.integer_types[64], self.size_of(closure_type))])
            closure = self.builder.bitcast(closure, ir.PointerType(closure_type))
            self.builder.store(self.recent_closure, self.gep(closure, [0, 0]))
            self.recent_closure.append(closure)
            self.closures.append(Closure(closure, closure_type, expr))

        last_result = None
        for stmt in expr.body:
            if isinstance(stmt, IRExprStmt):
                last_result = self.generate_expr(stmt.expr)
            else:
                self.generate_stmt(stmt)

        self.current_block = old_block
        if len(closed) > 0:
            self.closures.pop()
            self.recent_closure.pop()

        if expr.return_unit:
            return self.unit
        else:
            return last_result

    def generate_attr_assign(self, expr: IRAttrAssign) -> ir.Value:
        object = self.generate_expr(expr.obj)
        element_pointer = self.builder.gep(object, (ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), expr.index),))
        value = self.generate_expr(expr.value)
        match expr.op:
            case "none":
                pass
            case "Add":
                value = self.builder.add(self.builder.load(element_pointer), value)
            case "Sub":
                value = self.builder.sub(self.builder.load(element_pointer), value)
            case "Mul":
                value = self.builder.mul(self.builder.load(element_pointer), value)
            case "Div":
                value = self.builder.sdiv(self.builder.load(element_pointer), value)
            case "Mod":
                value = self.builder.srem(self.builder.load(element_pointer), value)
        self.builder.store(value, element_pointer)
        return value

    def generate_assign(self, expr: IRAssign) -> ir.Value:
        name = self.decl_values[expr.name]
        value = self.generate_expr(expr.value)

        if isinstance(name, ir.GlobalValue):
            raise ValueError()   # TODO
        elif expr.name.in_block is not None:
            if expr.name.put_in_closure:
                current_closure = self.recent_closure[-1]
                for closure in reversed(self.closures):
                    if expr.name.in_block == closure.from_block:
                        slot_ptr = self.gep(self.builder.bitcast(current_closure, ir.PointerType(closure.structure)), [0, expr.name.closure_index])
                        break
                    else:
                        current_closure = self.builder.load(self.builder.bitcast(current_closure, ir.PointerType(ir.PointerType(ir.IntType(8)))))
                else:
                    raise ValueError()
                match expr.op:
                    case "none":
                        pass
                    case "Add":
                        value = self.builder.add(self.builder.load(slot_ptr), value)
                    case "Sub":
                        value = self.builder.sub(self.builder.load(slot_ptr), value)
                    case "Mul":
                        value = self.builder.mul(self.builder.load(slot_ptr), value)
                    case "Div":
                        value = self.builder.sdiv(self.builder.load(slot_ptr), value)
                    case "Mod":
                        value = self.builder.srem(self.builder.load(slot_ptr), value)
                self.builder.store(value, slot_ptr)
            else:
                self.builder.store(value, name)
        else:
            raise ValueError()

        return value

    def generate_lambda(self, expr: IRLambda) -> ir.Value:
        ir_func_type = cast(IRFunctionType, expr.yield_type)
        func_type = ir.FunctionType(self.generate_type(ir_func_type.ret_type), [self.void_p_type] + [self.generate_type(param_type.type) for param_type in ir_func_type.param_types])
        func = ir.Function(self.module, func_type, self.new_name("lambda"))

        entry_block = func.append_basic_block("entry")
        prev_builder, self.builder = self.builder, ir.IRBuilder(entry_block)

        self.recent_closure.append(func.args[0])

        ##############
        old_block, self.current_block = self.current_block, expr.body

        count = 1
        closed: list[IRValueDecl] = []
        for decl in expr.body.declared:
            if decl.put_in_closure:
                closed.append(decl)
                decl.closure_index = count
                count += 1
        if len(closed) > 0:
            closure_type = ir.LiteralStructType([self.void_p_type] + [self.generate_type(var.type) for var in closed])
            closure = self.builder.call(self.external_functions["malloc"], [ir.Constant(self.integer_types[64], self.size_of(closure_type))])
            closure = self.builder.bitcast(closure, ir.PointerType(closure_type))
            self.builder.store(self.recent_closure, self.gep(closure, [0, 0]))
            self.recent_closure.append(closure)
            self.closures.append(Closure(closure, closure_type, expr.body))

        for ir_arg, llvm_arg in zip(expr.parameters, func.args[1:]):
            if ir_arg.decl.put_in_closure:
                closure_ptr = self.builder.gep(self.closures[-1].value, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), ir_arg.decl.closure_index)])
                self.builder.store(llvm_arg, closure_ptr)
            else:
                arg_slot = self.decl_values[ir_arg.decl] = self.builder.alloca(self.generate_type(ir_arg.type))
                self.builder.store(llvm_arg, arg_slot)

        result = self.unit
        for stmt in expr.body.body:
            if isinstance(stmt, IRExprStmt):
                result = self.generate_expr(stmt.expr)
            else:
                self.generate_stmt(stmt)

        self.current_block = old_block
        if len(closed) > 0:
            self.closures.pop()
            self.recent_closure.pop()
        #####

        if self.builder.block.terminator is None:
            self.builder.ret(result)
        self.builder = prev_builder
        self.recent_closure.pop()

        lambda_obj_type = cast(ir.PointerType, self.generate_type(ir_func_type))
        lambda_obj = self.builder.call(self.external_functions["malloc"], [ir.Constant(ir.IntType(64), self.size_of(lambda_obj_type.pointee))])
        lambda_obj = self.builder.bitcast(lambda_obj, lambda_obj_type)

        self.builder.store(func, self.gep(lambda_obj, [0, 0]))
        self.builder.store(self.builder.bitcast(self.recent_closure[-1], self.void_p_type), self.gep(lambda_obj, [0, 1]))

        return lambda_obj

    def generate_type(self, type: IRType) -> ir.Type:
        if not isinstance(type, IRResolvedType):
            raise ValueError(type)
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
        elif isinstance(type, IRFunctionType):
            return ir.PointerType(ir.LiteralStructType([
                ir.PointerType(ir.FunctionType(self.generate_type(type.ret_type), [self.void_p_type] + [self.generate_type(param.type) for param in type.param_types])),
                self.void_p_type
            ]))
        else:
            raise ValueError(type.__class__)