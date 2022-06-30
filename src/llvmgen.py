from __future__ import annotations

from typing import cast

from .swc_ir import *
from .common import ValueStack

from llvmlite import ir
from llvmlite import binding as llvm

from random import shuffle


i8 = ir.IntType(8)
i32 = ir.IntType(32)
i64 = ir.IntType(64)
boolean = ir.IntType(1)
unit_type = ir.IntType(1)
unit = unit_type(0)
void = i8
void_p = void.as_pointer()


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
    def __init__(self, value: ir.Value, structure: ManagedStructType, from_block: IRBlock):
        self.value = value
        self.struct_type = structure
        self.from_block = from_block


class StructType:
    def __init__(self, name: str, llvm_type: ir.BaseStructType):
        self._name = name
        self._llvm_type = llvm_type

        self._elems: list[ir.Type] = []
        self._elem_pos: dict[str, int] = {}

    @classmethod
    def construct(cls, name: str, fields: dict[str, ir.Type]) -> StructType:
        struct_type = StructType(name, ir.LiteralStructType([]))
        for name, typ in fields.items():
            struct_type.add_field(name, typ)
        return struct_type

    def add_field(self, name: str, type: ir.Type):
        self._elem_pos[name] = len(self._elems)
        self._elems.append(type)
        self._llvm_type.elements = tuple(self._elems)

    def index_of(self, name: str) -> int:
        return self._elem_pos[name]

    @property
    def name(self) -> str:
        return self._name

    @property
    def p_type(self) -> ir.PointerType:
        return self._llvm_type.as_pointer()

    @property
    def type(self) -> ir.BaseStructType:
        return self._llvm_type


class ManagedStructType(StructType):
    def __init__(self, name: str, llvm_type: ir.IdentifiedStructType):
        super().__init__(name, llvm_type)

        self.add_field("$next", void_p)
        self.add_field("$color", i8)
        self.add_field("$tag", void_p)


class LLVMGen:
    def __init__(self, program: IRProgram):
        self.program = program
        self.module = ir.Module()
        self.target_data = llvm.Target.from_default_triple().create_target_machine(codemodel="default").target_data

        self.external_functions: dict[str, ir.Function] = {}

        self.builder = ir.IRBuilder()

        self.closures: ValueStack[Closure] = ValueStack()

        self.function_ir: dict[IRFunction, ir.Function] = {}
        self.decl_values: dict[IRValueDecl, ir.Value] = {}

        self.vtables: dict[tuple[IRTraitType, IRStructType], ir.GlobalVariable] = {}
        self.trait_vtable_types: dict[IRTraitType, ir.LiteralStructType] = {}
        self.trait_types: dict[IRTraitType, ir.LiteralStructType] = {}
        self.struct_types: dict[IRStructType, ManagedStructType] = {}

        self.gc_state_type = StructType.construct("GCState", {
            "gc_lock": void_p,
            "white": void_p,
            "gray": void_p,
            "black": void_p,
        })
        self.gc_state = ir.GlobalVariable(self.module, self.gc_state_type.type, "swerve_gc_state")
        self.gc_state.initializer = self.gc_state_type.type(None)

        self.counter: list[int] = list(range(0, 1000000))
        shuffle(self.counter)

    def new_name(self, pattern: str) -> str:
        num = self.counter.pop()
        return f"{pattern}_{num:0>6}"

    def size_of(self, type: ir.Type) -> int:
        return type.get_abi_size(self.target_data)

    def get_base_function_type(self, f_type: IRFunctionType) -> ir.FunctionType:
        return ir.FunctionType(self.generate_type(f_type.ret_type), [void_p] + [self.generate_type(param) for param in f_type.param_types])

    def gep(self, pointer: ir.Value, indices: list[int]) -> ir.Value:
        return self.builder.gep(pointer, [ir.Constant(i32, index) for index in indices])

    def get_field_ptr(self, val: ir.Value, struct_type: StructType, field: str) -> ir.Value:
        return self.gep(val, [0, struct_type.index_of(field)])

    def new_managed_struct_type(self, *, name: str = None) -> ManagedStructType:
        if name is None:
            name = self.new_name("struct")
        struct_type = ManagedStructType(name, self.module.context.get_identified_type(name))
        return struct_type

    def allocate_struct_type(self, struct_type: ManagedStructType) -> ir.Value:
        closure = self.builder.call(self.external_functions["SWERVE_gc_allocate"], [
            self.gc_state.bitcast(void_p),
            i64(self.size_of(struct_type.type)),
            void_p(None)
        ])
        closure = self.builder.bitcast(closure, struct_type.p_type)
        return closure

    def load_external_functions(self):
        self.external_functions["malloc"] = ir.Function(self.module, ir.FunctionType(void_p, [i64]), "malloc")
        self.external_functions["SWERVE_gc_allocate"] = ir.Function(self.module, ir.FunctionType(void_p, [void_p, i64, void_p]), "SWERVE_gc_allocate")
        self.external_functions["SWERVE_gc_init"] = ir.Function(self.module, ir.FunctionType(void, [void_p]), "SWERVE_gc_init")
        self.external_functions["calloc"] = ir.Function(self.module, ir.FunctionType(void_p, [i64, i64]), "calloc")
        self.external_functions["exit"] = ir.Function(self.module, ir.FunctionType(ir.VoidType(), [i64]), "exit")

    def finalize(self):
        main = ir.Function(self.module, ir.FunctionType(i64, []), "main")
        self.builder = ir.IRBuilder(main.append_basic_block("entry"))

        self.builder.call(self.external_functions["SWERVE_gc_init"], [self.gc_state.bitcast(void_p)])

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
                        f_type = ir.FunctionType(f_type.return_type, [void_p, void_p] + list(f_type.args[2:]))
                    trait_members.append(f_type.as_pointer())
                v_table_type.set_body(*trait_members)
                trait_type.set_body(void_p, v_table_type.as_pointer())

    def load_structs(self):
        for struct in self.program.structs:
            if len(struct.get_type_vars()) == 0:
                struct_type = self.module.context.get_identified_type(self.new_name(struct.name))
                self.struct_types[cast(IRStructType, struct.type_decl.type)] = ManagedStructType(struct_type.name, struct_type)

                for trait in struct.supertraits:
                    trait = cast(IRTraitType, trait)
                    vtable = self.vtables[(trait, cast(IRStructType, struct.type_decl.type))] = ir.GlobalVariable(
                        self.module, self.trait_vtable_types[trait], self.new_name(f"{struct.name}-as-{trait.trait.name}_vtable")
                    )
                    vtable.global_constant = True

        for type, array_variant in self.program.array_variants.items():
            if type.is_concrete():
                struct_type = self.module.context.get_identified_type(self.new_name(array_variant.array.name))
                self.struct_types[cast(IRStructType, array_variant.array.type_decl.type)] = ManagedStructType(struct_type.name, struct_type)

        for struct in self.program.structs:
            if len(struct.get_type_vars()) == 0:
                struct_type = self.struct_types[cast(IRStructType, struct.type_decl.type)]
                for field in struct.fields:
                    struct_type.add_field(field.name, self.generate_type(field.type))

                self.generate_constructor(struct, struct_type)

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
        struct_type = self.struct_types[cast(IRStructType, variant.array.type_decl.type)]
        struct_type.add_field("$mem", self.generate_type(variant.type).as_pointer())
        struct_type.add_field("$len", i64)

        self.generate_array_constructor(variant, struct_type, self.generate_type(variant.type))

        self.generate_array_get(variant, struct_type)
        self.generate_array_set(variant, struct_type)

    def generate_array_set(self, variant: ArrayVariant, struct_type: ManagedStructType):
        set_value_type = cast(ir.LiteralStructType, self.generate_type(variant.set.type))
        set_type: ir.FunctionType = set_value_type.elements[0].pointee
        set_ = ir.Function(self.module, set_type, self.new_name(f"{struct_type.name}::set"))

        set_value = ir.GlobalVariable(self.module, set_value_type, f"obj_{set_.name}")
        set_value.global_constant = True
        set_value.initializer = ir.Constant(set_value_type, [set_, ir.Constant(void_p, None)])
        self.decl_values[variant.set] = set_value

        entry_block = set_.append_basic_block("entry")
        err_block = set_.append_basic_block("err")
        closure, arr, index, value = set_.args
        with self.builder.goto_block(entry_block):
            with self.builder.if_then(self.builder.icmp_signed("<", index, i64(0))):
                self.builder.branch(err_block)

            arr_size = self.builder.load(self.get_field_ptr(arr, struct_type, "$len"))
            with self.builder.if_then(self.builder.icmp_signed(">=", index, arr_size)):
                self.builder.branch(err_block)
            array = self.builder.load(self.get_field_ptr(arr, struct_type, "$mem"))
            element_ptr = self.builder.gep(array, [index])
            self.builder.store(value, element_ptr)
            self.builder.ret(unit)
        with self.builder.goto_block(err_block):
            self.builder.call(self.external_functions["exit"], [i64(-1)])
            self.builder.unreachable()

    def generate_array_get(self, variant: ArrayVariant, struct_type: ManagedStructType):
        get_value_type = cast(ir.LiteralStructType, self.generate_type(variant.get.type))
        get_type: ir.FunctionType = get_value_type.elements[0].pointee
        get = ir.Function(self.module, get_type, self.new_name(f"{struct_type.name}::get"))

        get_value = ir.GlobalVariable(self.module, get_value_type, f"obj_{get.name}")
        get_value.global_constant = True
        get_value.initializer = ir.Constant(get_value_type, [get, ir.Constant(void_p, None)])
        self.decl_values[variant.get] = get_value

        entry_block = get.append_basic_block("entry")
        err_block = get.append_basic_block("err")
        closure, arr, index = get.args
        with self.builder.goto_block(entry_block):
            with self.builder.if_then(self.builder.icmp_signed("<", index, i64(0))):
                self.builder.branch(err_block)
            arr_size = self.builder.load(self.get_field_ptr(arr, struct_type, f"$len"))
            with self.builder.if_then(self.builder.icmp_signed(">=", index, arr_size)):
                self.builder.branch(err_block)
            array = self.builder.load(self.get_field_ptr(arr, struct_type, f"$mem"))
            element_ptr = self.builder.gep(array, [index])
            self.builder.ret(self.builder.load(element_ptr))
        with self.builder.goto_block(err_block):
            self.builder.call(self.external_functions["exit"], [i64(-1)])
            self.builder.unreachable()

    def generate_array_constructor(self, variant: ArrayVariant, struct_type: ManagedStructType, value_type: ir.Type):
        constructor_value_type = cast(ir.LiteralStructType, self.generate_type(variant.constructor.type))
        constructor_type: ir.FunctionType = constructor_value_type.elements[0].pointee
        constructor = ir.Function(self.module, constructor_type, self.new_name(f"{struct_type.name}_constructor"))

        constructor_value = ir.GlobalVariable(self.module, constructor_value_type, f"obj_{constructor.name}")
        constructor_value.global_constant = True
        constructor_value.initializer = ir.Constant(constructor_value_type, [constructor, ir.Constant(void_p, None)])
        self.decl_values[variant.constructor] = constructor_value

        self.builder = ir.IRBuilder(constructor.append_basic_block("entry"))
        mem = self.builder.call(self.external_functions["malloc"], [i64(self.size_of(struct_type.type))])
        obj = self.builder.bitcast(mem, struct_type.p_type)

        closure, size = constructor.args

        memory = self.builder.call(self.external_functions["calloc"], [size, i64(self.size_of(value_type))])
        memory = self.builder.bitcast(memory, value_type.as_pointer())
        self.builder.store(memory, self.get_field_ptr(obj, struct_type, f"$mem"))
        self.builder.store(size, self.get_field_ptr(obj, struct_type, f"$len"))
        self.builder.ret(obj)

    def generate_constructor(self, struct: IRStruct, struct_type: ManagedStructType):
        constructor_type = ir.FunctionType(struct_type.p_type, [void_p] + [self.generate_type(field.type) for field in struct.fields])
        constructor = ir.Function(self.module, constructor_type, self.new_name(f"{struct.name}_constructor"))

        func_value_type = self.generate_type(struct.constructor.type)
        func_value = ir.GlobalVariable(self.module, func_value_type, f"obj_{constructor.name}")
        func_value.global_constant = True
        func_value.initializer = ir.Constant(func_value_type, [constructor, void_p(None)])

        self.decl_values[struct.constructor] = func_value

        self.builder = ir.IRBuilder(constructor.append_basic_block("entry"))

        _, *args = constructor.args

        mem = self.builder.call(self.external_functions["malloc"], [i64(self.size_of(struct_type.type))])
        obj = self.builder.bitcast(mem, struct_type.p_type)

        for field, value in zip(struct.fields, args):
            self.builder.store(value, self.get_field_ptr(obj, struct_type, field.name))

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
        func_type = ir.FunctionType(self.generate_type(ir_func_type.ret_type), [void_p] + [self.generate_type(param_type) for param_type in ir_func_type.param_types])
        func = ir.Function(self.module, func_type, self.new_name(function.name))

        func_value_type = self.generate_type(ir_func_type)
        func_value = ir.GlobalVariable(self.module, func_value_type, f"obj_{func.name}")
        func_value.global_constant = True
        func_value.initializer = ir.Constant(func_value_type, [func, void_p(None)])
        self.decl_values[function.decl] = func_value
        self.function_ir[function] = func

    def generate_scope(self, block: IRBlock, closure_ptr: ir.Value = None, parameters: tuple[list[IRParameter], list[ir.Argument]] = None) -> ir.Value | None:
        if parameters is None:
            ir_parameters = []
            llvm_parameters = []
        else:
            ir_parameters, llvm_parameters = parameters

        closed: list[IRValueDecl] = []
        for decl in block.declared:
            if decl.put_in_closure:
                decl.closure_index = len(closed)
                closed.append(decl)
        if len(closed) > 0 or closure_ptr is not None:
            closure_type = self.new_managed_struct_type()
            closure_type.add_field("$enclosing", void_p)
            for var in closed:
                closure_type.add_field(f"${var.closure_index}", self.generate_type(var.type))

            closure = self.allocate_struct_type(closure_type)

            if closure_ptr is None:
                self.builder.store(self.closures.recent.value, self.get_field_ptr(closure, closure_type, "$enclosing"))
            else:
                self.builder.store(closure_ptr, self.get_field_ptr(closure, closure_type, "$enclosing"))
            self.closures.push(Closure(closure, closure_type, block))

            for ir_arg, llvm_arg in zip(ir_parameters, llvm_parameters):
                if ir_arg.decl.put_in_closure:
                    self.builder.store(llvm_arg, self.get_field_ptr(self.closures.recent.value, closure_type, f"${ir_arg.decl.closure_index}"))
                else:
                    arg_slot = self.decl_values[ir_arg.decl] = self.builder.alloca(self.generate_type(ir_arg.type))
                    self.builder.store(llvm_arg, arg_slot)

            last_result = None
            for stmt in block.body:
                if isinstance(stmt, IRExprStmt):
                    last_result = self.generate_expr(stmt.expr)
                else:
                    self.generate_stmt(stmt)

            self.closures.pop()
        else:
            for ir_arg, llvm_arg in zip(ir_parameters, llvm_parameters):
                arg_slot = self.decl_values[ir_arg.decl] = self.builder.alloca(self.generate_type(ir_arg.type))
                self.builder.store(llvm_arg, arg_slot)

            last_result = None
            for stmt in block.body:
                if isinstance(stmt, IRExprStmt):
                    last_result = self.generate_expr(stmt.expr)
                else:
                    self.generate_stmt(stmt)

        return last_result

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
                self.builder.ret(unit)
            else:
                self.builder.ret(value)
        else:
            self.generate_scope(function.body, void_p(None), (function.parameters, func.args[1:]))

            if self.builder.block.terminator is None:
                if function.body.always_returns():
                    self.builder.unreachable()
                else:
                    self.builder.ret(unit)
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
            self.decl_values[stmt.decl] = self.builder.gep(self.closures.recent.value, [i32(0), i32(stmt.decl.closure_index)])
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
        elif isinstance(expr, IRIndexExpr):
            val = self.generate_index_expr(expr)
        elif isinstance(expr, IRMethodCallExpr):
            val = self.generate_method_call_expr(expr)
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
            trait_obj = self.builder.insert_value(trait_obj, self.builder.bitcast(val, void_p), 0)
            trait_obj = self.builder.insert_value(trait_obj, self.vtables[(to_type, from_type)], 1)
            return trait_obj
        else:
            raise ValueError(from_type.__class__, to_type.__class__)

    def generate_integer_expr(self, expr: IRIntegerExpr) -> ir.Value:
        return ir.Constant(self.generate_type(expr.yield_type), expr.number)

    def generate_name_expr(self, expr: IRNameExpr) -> ir.Value:
        name = self.decl_values[expr.name]
        if expr.name.in_block is not None:
            if expr.name.put_in_closure:
                current_closure = self.closures.recent.value
                for closure in reversed(self.closures.all):
                    if expr.name.in_block == closure.from_block:
                        return self.builder.load(self.gep(self.builder.bitcast(current_closure, closure.struct_type.p_type),
                                                          [0, closure.struct_type.index_of(f"${expr.name.closure_index}")]))
                    else:
                        current_closure = self.builder.load(self.builder.bitcast(current_closure, void_p.as_pointer()))
                else:
                    raise ValueError()
            else:
                return self.builder.load(name)
        else:
            return self.builder.load(name)

    def generate_generic_attr_expr(self, expr: IRGenericAttrExpr) -> ir.Value:
        return self.builder.load(self.decl_values[expr.resolved])

    def generate_call_expr(self, expr: IRCallExpr) -> ir.Value:
        if expr.as_method_call is not None:
            return self.generate_method_call_expr(expr.as_method_call)
        fn_struct_p = self.generate_expr(expr.callee)
        fn_ptr = self.builder.extract_value(fn_struct_p, 0)
        closure_ptr = self.builder.extract_value(fn_struct_p, 1)
        return self.builder.call(fn_ptr, [closure_ptr] + [self.generate_expr(arg) for arg in expr.arguments])

    def generate_attr_expr(self, expr: IRAttrExpr) -> ir.Value:
        object = self.generate_expr(expr.object)
        index = self.struct_types[expr.struct].index_of(expr.attr)
        element_pointer = self.builder.gep(object, (i32(0), i32(index)))
        return self.builder.load(element_pointer)

    def generate_index_expr(self, expr: IRIndexExpr) -> ir.Value:
        return self.generate_expr(expr.replacement_expr)

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
            arguments = [void_p(None)]
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
            result.add_incoming(unit, before_block)
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
        last_result = self.generate_scope(expr)

        if expr.return_unit:
            return unit
        else:
            return last_result

    def generate_attr_assign(self, expr: IRAttrAssign) -> ir.Value:
        object = self.generate_expr(expr.obj)
        index = self.struct_types[expr.struct].index_of(expr.attr)
        element_pointer = self.builder.gep(object, (i32(0), i32(index)))
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
                current_closure = self.closures.recent
                for closure in reversed(self.closures.all):
                    if expr.name.in_block == closure.from_block:
                        slot_ptr = self.gep(self.builder.bitcast(current_closure, closure.struct_type.p_type),
                                            [0, closure.struct_type.index_of(f"${expr.name.closure_index}")])
                        break
                    else:
                        current_closure = self.builder.load(self.builder.bitcast(current_closure, void_p.as_pointer()))
                else:
                    raise ValueError()
                var_loc = slot_ptr
            else:
                var_loc = name
            match expr.op:
                case "none":
                    pass
                case "Add":
                    value = self.builder.add(self.builder.load(var_loc), value)
                case "Sub":
                    value = self.builder.sub(self.builder.load(var_loc), value)
                case "Mul":
                    value = self.builder.mul(self.builder.load(var_loc), value)
                case "Div":
                    value = self.builder.sdiv(self.builder.load(var_loc), value)
                case "Mod":
                    value = self.builder.srem(self.builder.load(var_loc), value)
            self.builder.store(value, var_loc)
        else:
            raise ValueError()

        return value

    def generate_lambda(self, expr: IRLambda) -> ir.Value:
        ir_func_type = cast(IRFunctionType, expr.yield_type)
        func_type = ir.FunctionType(self.generate_type(ir_func_type.ret_type), [void_p] + [self.generate_type(param_type) for param_type in ir_func_type.param_types])
        func = ir.Function(self.module, func_type, self.new_name("lambda"))

        entry_block = func.append_basic_block("entry")
        prev_builder, self.builder = self.builder, ir.IRBuilder(entry_block)

        last_result = self.generate_scope(expr.body, func.args[0], (expr.parameters, func.args[1:]))

        if self.builder.block.terminator is None:
            self.builder.ret(last_result)
        self.builder = prev_builder

        lambda_obj_type = cast(ir.LiteralStructType, self.generate_type(ir_func_type))
        lambda_obj = self.builder.insert_value(lambda_obj_type(None), func, 0)
        lambda_obj = self.builder.insert_value(lambda_obj, self.builder.bitcast(self.closures.recent.value, void_p), 1)

        return lambda_obj

    def generate_type(self, type: IRType) -> ir.Type:
        if not isinstance(type, IRResolvedType):
            raise ValueError(type)
        if isinstance(type, IRIntegerType):
            return ir.IntType(type.bits)
        elif isinstance(type, IRStructType):
            return self.struct_types[type].p_type
        elif isinstance(type, IRTraitType):
            return self.trait_types[type]
        elif isinstance(type, IRUnitType):
            return unit_type
        elif isinstance(type, IRBoolType):
            return boolean
        elif isinstance(type, IRFunctionType):
            return ir.LiteralStructType([self.get_base_function_type(type).as_pointer(), void_p])
        else:
            raise ValueError(type.__class__)