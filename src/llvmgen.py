from __future__ import annotations

from typing import cast

from .swc_ir import *

from llvmlite import ir
from llvmlite import binding as llvm

from random import shuffle


i32 = ir.IntType(32)
i64 = ir.IntType(64)
boolean = ir.IntType(1)
unit = ir.IntType(1)


def generate_llvm(program: IRProgram) -> ir.Module:
    llvm.initialize()
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()

    gen = LLVMGen(program)
    gen.load_external_functions()
    gen.load_traits()
    gen.load_structs()
    gen.generate_functions()
    gen.generate_vtables()
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
        self.recent_closure: list[ir.Value] = [ir.Constant(self.void_p_type, None)]
        self.current_block: IRBlock | None = None
        self.function_ir: dict[IRFunction, ir.Function] = {}
        self.decl_values: dict[IRValueDecl, ir.Value] = {}
        self.struct_types: dict[IRStructType, ir.PointerType] = {}

        self.trait_vtable_types: dict[IRTraitType, ir.LiteralStructType] = {}
        self.trait_types: dict[IRTraitType, ir.LiteralStructType] = {}

        self.vtables: dict[tuple[IRTraitType, IRStructType], ir.GlobalVariable] = {}

        self.counter: list[int] = list(range(0, 1000000))
        shuffle(self.counter)

    def new_name(self, pattern: str) -> str:
        num = self.counter.pop()
        return f"{pattern}_{num:0>6}"

    def load_external_functions(self):
        self.external_functions["malloc"] = ir.Function(self.module, ir.FunctionType(self.void_p_type, [self.integer_types[64]]), "malloc")
        self.external_functions["calloc"] = ir.Function(self.module, ir.FunctionType(self.void_p_type, [self.integer_types[64], self.integer_types[64]]), "calloc")
        self.external_functions["exit"] = ir.Function(self.module, ir.FunctionType(ir.VoidType(), [self.integer_types[64]]), "exit")

    def size_of(self, type: ir.Type) -> int:
        return type.get_abi_size(self.target_data)

    def get_base_function_type(self, f_type: IRFunctionType) -> ir.FunctionType:
        return ir.FunctionType(self.generate_type(f_type.ret_type), [self.void_p_type] + [self.generate_type(param) for param in f_type.param_types])

    def gep(self, pointer: ir.Value, indices: list[int]) -> ir.Value:
        return self.builder.gep(pointer, [ir.Constant(ir.IntType(32), index) for index in indices])

    def finalize(self):
        main = ir.Function(self.module, ir.FunctionType(self.integer_types[64], []), "main")
        self.builder = ir.IRBuilder(main.append_basic_block("entry"))

        fn_struct_p = self.decl_values[self.program.main_func.decl]
        fn_ptr = self.builder.load(self.gep(fn_struct_p, [0, 0]))
        closure_ptr = self.builder.load(self.gep(fn_struct_p, [0, 1]))
        self.builder.ret(self.builder.call(fn_ptr, [closure_ptr] + list(main.args)))

    def load_traits(self):
        for trait in self.program.traits:
            if len(trait.get_type_vars()) == 0:
                v_table_type = self.module.context.get_identified_type(self.new_name(f"{trait.name}_vtable"))
                trait_type = self.module.context.get_identified_type(self.new_name(f"{trait.name}"))
                self.trait_vtable_types[cast(IRTraitType, trait.type_decl.type)] = v_table_type
                self.trait_types[cast(IRTraitType, trait.type_decl.type)] = trait_type

                trait_members: list[ir.Type] = []
                for virtual_method in trait.get_virtual_methods():
                    f_type = self.get_base_function_type(virtual_method.function.function_type)
                    if virtual_method.is_self:
                        f_type = ir.FunctionType(f_type.return_type, [self.void_p_type, self.void_p_type] + list(f_type.args[2:]))
                    trait_members.append(f_type.as_pointer())
                v_table_type.set_body(*trait_members)
                trait_type.set_body(self.void_p_type, v_table_type.as_pointer())

    def load_structs(self):
        for struct in self.program.structs:
            if len(struct.get_type_vars()) == 0:
                struct_type = self.module.context.get_identified_type(self.new_name(struct.name))
                # noinspection PyTypeChecker
                self.struct_types[struct.type_decl.type] = ir.PointerType(struct_type)

                for trait in struct.supertraits:
                    trait = cast(IRTraitType, trait)
                    vtable = self.vtables[(trait, cast(IRStructType, struct.type_decl.type))] = ir.GlobalVariable(
                        self.module, self.trait_vtable_types[trait], self.new_name(f"{struct.name}-as-{trait.trait.name}_vtable")
                    )
                    vtable.global_constant = True

        for type, array_variant in self.program.array_variants.items():
            if type.is_concrete():
                struct_type = self.module.context.get_identified_type(self.new_name(array_variant.array.name))
                self.struct_types[cast(IRStructType, array_variant.array.type_decl.type)] = ir.PointerType(struct_type)

        for struct in self.program.structs:
            if len(struct.get_type_vars()) == 0:
                # noinspection PyTypeChecker
                struct_p_type: ir.PointerType = self.struct_types[struct.type_decl.type]
                struct_type: ir.IdentifiedStructType = struct_p_type.pointee
                struct_type.set_body(*(self.generate_type(field.type) for field in struct.fields))

                self.generate_constructor(struct, struct_p_type)

        for type, array_variant in self.program.array_variants.items():
            if type.is_concrete():
                self.generate_array_variant(array_variant)

    def generate_vtables(self):
        for struct in self.program.structs:
            if len(struct.get_type_vars()) == 0:
                for trait in struct.supertraits:
                    trait = cast(IRTraitType, trait)
                    vtable_type = self.trait_vtable_types[trait]

                    vtable = self.vtables[(trait, cast(IRStructType, struct.type_decl.type))]
                    functions: list[ir.Value] = []
                    for vtable_f_type, (i, v_method) in zip(vtable_type.elements, enumerate(trait.trait.get_virtual_methods())):
                        method = struct.methods[struct.has_method(v_method.name)]
                        functions.append(self.function_ir[method.function].bitcast(vtable_f_type))
                    vtable.initializer = ir.Constant(vtable_type, functions)

    def generate_array_variant(self, variant: ArrayVariant):
        # noinspection PyTypeChecker
        struct_p_type: ir.PointerType = self.struct_types[variant.array.type_decl.type]
        struct_type: ir.IdentifiedStructType = struct_p_type.pointee
        struct_type.set_body(self.generate_type(variant.type).as_pointer(), ir.IntType(64))

        self.generate_array_constructor(variant, struct_type)

        self.generate_array_get(variant, struct_type)
        self.generate_array_set(variant, struct_type)

    def generate_array_set(self, variant: ArrayVariant, struct_type: ir.IdentifiedStructType):
        set_value_type = self.generate_type(variant.set.type)
        # noinspection PyUnresolvedReferences
        set_type: ir.FunctionType = set_value_type.pointee.elements[0].pointee
        # noinspection PyShadowingBuiltins
        set = ir.Function(self.module, set_type, self.new_name(f"{struct_type.name}::set"))

        # noinspection PyUnresolvedReferences
        set_value = ir.GlobalVariable(self.module, set_value_type.pointee, f"obj_{set.name}")
        set_value.global_constant = True
        set_value.initializer = ir.Constant(set_value.type.pointee, [set, ir.Constant(self.void_p_type, None)])
        self.decl_values[variant.set] = set_value

        entry_block = set.append_basic_block("entry")
        err_block = set.append_basic_block("err")
        closure, arr, index, value = set.args
        with self.builder.goto_block(entry_block):
            with self.builder.if_then(self.builder.icmp_signed("<", index, ir.Constant(ir.IntType(64), 0))):
                self.builder.branch(err_block)
            arr_size = self.builder.load(self.gep(arr, [0, 1]))
            with self.builder.if_then(self.builder.icmp_signed(">=", index, arr_size)):
                self.builder.branch(err_block)
            field_ptr = self.builder.gep(arr, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)])
            array = self.builder.load(field_ptr)
            element_ptr = self.builder.gep(array, [index])
            self.builder.store(value, element_ptr)
            self.builder.ret(self.unit)
        with self.builder.goto_block(err_block):
            self.builder.call(self.external_functions["exit"], [i64(-1)])
            self.builder.unreachable()

    def generate_array_get(self, variant: ArrayVariant, struct_type: ir.IdentifiedStructType):
        get_value_type = self.generate_type(variant.get.type)
        # noinspection PyUnresolvedReferences
        get_type: ir.FunctionType = get_value_type.pointee.elements[0].pointee
        get = ir.Function(self.module, get_type, self.new_name(f"{struct_type.name}::get"))

        # noinspection PyUnresolvedReferences
        get_value = ir.GlobalVariable(self.module, get_value_type.pointee, f"obj_{get.name}")
        get_value.global_constant = True
        get_value.initializer = ir.Constant(get_value.type.pointee, [get, ir.Constant(self.void_p_type, None)])
        self.decl_values[variant.get] = get_value

        entry_block = get.append_basic_block("entry")
        err_block = get.append_basic_block("err")
        closure, arr, index = get.args
        with self.builder.goto_block(entry_block):
            with self.builder.if_then(self.builder.icmp_signed("<", index, ir.Constant(ir.IntType(64), 0))):
                self.builder.branch(err_block)
            arr_size = self.builder.load(self.gep(arr, [0, 1]))
            with self.builder.if_then(self.builder.icmp_signed(">=", index, arr_size)):
                self.builder.branch(err_block)
            field_ptr = self.builder.gep(arr, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)])
            array = self.builder.load(field_ptr)
            element_ptr = self.builder.gep(array, [index])
            self.builder.ret(self.builder.load(element_ptr))
        with self.builder.goto_block(err_block):
            self.builder.call(self.external_functions["exit"], [i64(-1)])
            self.builder.unreachable()

    def generate_array_constructor(self, variant: ArrayVariant, struct_type: ir.IdentifiedStructType):
        constructor_value_type = self.generate_type(variant.constructor.type)
        value_type: ir.Type = struct_type.elements[0].pointee
        # noinspection PyUnresolvedReferences
        constructor_type: ir.FunctionType = constructor_value_type.pointee.elements[0].pointee
        constructor = ir.Function(self.module, constructor_type, self.new_name(f"{struct_type.name}_constructor"))

        # noinspection PyUnresolvedReferences
        constructor_value = ir.GlobalVariable(self.module, constructor_value_type.pointee, f"obj_{constructor.name}")
        constructor_value.global_constant = True
        constructor_value.initializer = ir.Constant(constructor_value.type.pointee, [constructor, ir.Constant(self.void_p_type, None)])
        self.decl_values[variant.constructor] = constructor_value

        self.builder = ir.IRBuilder(constructor.append_basic_block("entry"))
        mem = self.builder.call(self.external_functions["malloc"], [ir.Constant(ir.IntType(64), self.size_of(struct_type))])
        obj = self.builder.bitcast(mem, struct_type.as_pointer())

        closure, size = constructor.args

        memory = self.builder.call(self.external_functions["calloc"], [size, i64(self.size_of(value_type))])
        memory = self.builder.bitcast(memory, value_type.as_pointer())
        self.builder.store(memory, self.gep(obj, [0, 0]))
        self.builder.store(size, self.gep(obj, [0, 1]))
        self.builder.ret(obj)

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
            if len(function.get_type_vars()) == 0:
                self.generate_function_header(function)

        for function in self.program.functions:
            if len(function.get_type_vars()) == 0:
                self.generate_function(function)

    def generate_function_header(self, function: IRFunction):
        ir_func_type = function.function_type
        func_type = ir.FunctionType(self.generate_type(ir_func_type.ret_type), [self.void_p_type] + [self.generate_type(param_type) for param_type in ir_func_type.param_types])
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

        if function.is_extern:
            f_type = func.function_type
            if isinstance(function.function_type.ret_type, IRUnitType):
                ret_type = ir.VoidType()
                is_void_ret = True
            else:
                ret_type = f_type.return_type
                is_void_ret = False
            c_func_type = ir.FunctionType(ret_type, f_type.args[1:])
            c_func = ir.Function(self.module, c_func_type, function.name)
            value = self.builder.call(c_func, func.args[1:])
            if is_void_ret:
                self.builder.ret(self.unit)
            else:
                self.builder.ret(value)
        else:
            self.current_block = function.body
            count = 1
            closed: list[IRValueDecl] = []
            for decl in function.body.declared:
                if decl.put_in_closure:
                    closed.append(decl)
                    decl.closure_index = count
                    count += 1
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
            val = self.generate_integer_expr(expr)
        elif isinstance(expr, IRNameExpr):
            val = self.generate_name_expr(expr)
        elif isinstance(expr, IRCallExpr):
            val = self.generate_call_expr(expr)
        elif isinstance(expr, IRAttrExpr):
            val = self.generate_attr_expr(expr)
        elif isinstance(expr, IRGenericExpr):
            val = self.generate_generic_expr(expr)
        elif isinstance(expr, IRBinaryExpr):
            val = self.generate_binary_expr(expr)
        elif isinstance(expr, IRIf):
            val = self.generate_if_expr(expr)
        elif isinstance(expr, IRBlock):
            val = self.generate_block_expr(expr)
        elif isinstance(expr, IRAssign):
            val = self.generate_assign(expr)
        elif isinstance(expr, IRAttrAssign):
            val = self.generate_attr_assign(expr)
        elif isinstance(expr, IRLambda):
            val = self.generate_lambda(expr)
        elif isinstance(expr, IRGenericOrIndexExpr):
            if expr.as_index:
                return self.generate_index_expr(expr.as_index)
            else:
                return self.generate_generic_expr(expr.as_generic)
        elif isinstance(expr, IRGenericAttrExpr):
            val = self.generate_generic_attr_expr(expr)
        else:
            raise ValueError(type(expr))
        if expr.cast:
            return self.generate_cast(val, expr.yield_type, expr.cast)
        else:
            return val

    def generate_cast(self, val: ir.Value, from_type: IRResolvedType, to_type: IRResolvedType) -> ir.Value:
        if isinstance(from_type, IRStructType) and isinstance(to_type, IRTraitType):
            trait_type = self.trait_types[to_type]
            trait_obj = ir.Constant(trait_type, [None, None])
            trait_obj = self.builder.insert_value(trait_obj, self.builder.bitcast(val, self.void_p_type), 0)
            trait_obj = self.builder.insert_value(trait_obj, self.vtables[(to_type, from_type)], 1)
            return trait_obj
        else:
            raise ValueError(from_type.__class__, to_type.__class__)

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
                return self.builder.load(name)
        else:
            raise ValueError(name, expr.name)

    def generate_generic_attr_expr(self, expr: IRGenericAttrExpr) -> ir.Value:
        return self.decl_values[expr.resolved]

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
        elif isinstance(expr.from_type, IRTraitType):
            trait = cast(IRTraitType, expr.from_type).trait
            trait_obj = self.generate_expr(expr.obj)
            obj = self.builder.extract_value(trait_obj, 0)
            vtable_ptr = self.builder.extract_value(trait_obj, 1)
            method_ptr = self.builder.load(self.gep(vtable_ptr, [0, trait.has_method(expr.method.name)]))
            arguments = [self.void_p_type(None)]
            if expr.method.is_self:
                arguments.append(obj)
            arguments.extend(self.generate_expr(arg) for arg in expr.arguments)
            return self.builder.call(method_ptr, arguments)
        else:
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

    def generate_generic_expr(self, expr: IRGenericExpr) -> ir.Value:
        return self.generate_expr(expr.replacement_expr)

    def generate_index_expr(self, expr: IRIndexExpr) -> ir.Value:
        raise ValueError()

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
        func_type = ir.FunctionType(self.generate_type(ir_func_type.ret_type), [self.void_p_type] + [self.generate_type(param_type) for param_type in ir_func_type.param_types])
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
        elif isinstance(type, IRTraitType):
            return self.trait_types[type]
        elif isinstance(type, IRUnitType):
            return self.unit_type
        elif isinstance(type, IRBoolType):
            return self.bool_type
        elif isinstance(type, IRFunctionType):
            return ir.PointerType(ir.LiteralStructType([self.get_base_function_type(type).as_pointer(), self.void_p_type]))
        else:
            raise ValueError(type.__class__)