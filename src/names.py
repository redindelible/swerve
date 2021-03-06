from __future__ import annotations

from typing import cast

from .swc_ast import *
from .swc_ir import *
from .common import BuiltinLocation, CompilerMessage, ErrorType, Location, Path


def resolve_names(program: ASTProgram):
    resolver = ResolveNames(program)
    resolver.collect_names()
    resolver.resolve_imports()
    return resolver.resolve_names()


class ResolveNames:
    def __init__(self, program: ASTProgram):
        self.program = program
        self.ir_program = IRProgram([], [], [])

        self.program_namespace = Namespace()
        self.namespaces: list[Namespace] = []
        self.blocks: list[IRBlock] = []

        self.file_namespaces: dict[ASTFile, Namespace] = {}

        self.value_decls: dict[ASTNode, IRValueDecl] = {}

        self.struct_type_decls: dict[ASTStruct, IRTypeDecl] = {}
        self.trait_type_decls: dict[ASTTrait, IRTypeDecl] = {}

    def push(self, ns: Namespace) -> Namespace:
        self.namespaces.append(ns)
        return ns

    def pop(self) -> Namespace:
        return self.namespaces.pop()

    @property
    def curr_ns(self) -> Namespace:
        return self.namespaces[-1]

    @property
    def curr_block(self) -> IRBlock:
        return self.blocks[-1]

    def get_type(self, name: str, loc: Location) -> IRTypeDecl:
        for ns in reversed(self.namespaces):
            if ns.has_type(name):
                return ns.get_type(name, loc)
        else:
            raise CompilerMessage(ErrorType.COMPILATION, f"Name '{name}' does not exist for a type in this scope", loc)

    def get_namespace(self, name: str, loc: Location) -> Namespace:
        for ns in reversed(self.namespaces):
            if ns.has_namespace(name):
                return ns.get_namespace(name, loc)
        else:
            raise CompilerMessage(ErrorType.COMPILATION, f"Name '{name}' does not exist for a namespace in this scope", loc)

    def get_value(self, name: str, loc: Location) -> IRValueDecl:
        lambdas_to_add_to: list[Namespace] = []
        for ns in reversed(self.namespaces):
            if ns.has_value(name):
                value = ns.get_value(name, loc)
                if value.is_runtime:
                    for lambda_ in lambdas_to_add_to:
                        lambda_.exterior_names.append(value)
                return value
            if ns.is_lambda:
                lambdas_to_add_to.append(ns)
        else:
            raise CompilerMessage(ErrorType.COMPILATION, f"Name '{name}' does not exist for a value in this scope", loc)

    def collect_names(self):
        self.collect_program(self.program)

    def collect_program(self, program: ASTProgram):
        ns = self.push(self.program_namespace)
        ns.declare_type("int", IRTypeDecl(IRIntegerType(64), BuiltinLocation()))
        ns.declare_type("bool", IRTypeDecl(IRBoolType(), BuiltinLocation()))

        self.ir_program.array_decl = ns.declare_type("_array", IRTypeDecl(IRUnresolvedUnknownType(), BuiltinLocation()))
        self.ir_program.array_constructor_decl = ns.declare_value("_array", IRValueDecl(IRUnresolvedUnknownType(), BuiltinLocation(), False))

        ops_ns = Namespace()
        ns.declare_namespace("ops", ops_ns, BuiltinLocation())
        self.ir_program.ops["Index"] = ops_ns.declare_type("Index", IRTypeDecl(IRUnresolvedUnknownType(), BuiltinLocation()))
        self.ir_program.ops["Trace"] = ops_ns.declare_type("Trace", IRTypeDecl(IRUnresolvedUnknownType(), BuiltinLocation()))

        for file in program.files:
            self.collect_file(file)
        self.pop()

    def collect_file(self, file: ASTFile):
        self.push(Namespace())
        for top_level in file.top_levels:
            if isinstance(top_level, ASTFunction):
                self.collect_function(top_level)
            elif isinstance(top_level, ASTStruct):
                self.collect_struct(top_level)
            elif isinstance(top_level, ASTTrait):
                self.collect_trait(top_level)
            elif isinstance(top_level, ASTImport):
                pass
            else:
                raise ValueError(type(top_level))
        self.file_namespaces[file] = self.pop()

    def collect_function(self, function: ASTFunction):
        decl = self.curr_ns.declare_value(function.name, IRValueDecl(IRUnresolvedUnknownType(), function.loc, False))
        self.value_decls[function] = decl

    def collect_struct(self, struct: ASTStruct):
        type_decl = self.curr_ns.declare_type(struct.name, IRTypeDecl(IRUnresolvedUnknownType(), struct.loc))
        struct_ns = self.push(Namespace())
        for method in struct.methods:
            decl = self.curr_ns.declare_value(method.name, IRValueDecl(IRUnresolvedUnknownType(), method.loc, False))
            self.value_decls[method] = decl
        self.pop()
        self.struct_type_decls[struct] = type_decl

        # constructor
        decl = self.curr_ns.declare_value(struct.name, IRValueDecl(IRUnresolvedUnknownType(), struct.loc, False))
        self.value_decls[struct] = decl

    def collect_trait(self, trait: ASTTrait):
        type_decl = self.curr_ns.declare_type(trait.name, IRTypeDecl(IRUnresolvedUnknownType(), trait.loc))
        struct_ns = self.push(Namespace())
        for method in trait.methods:
            decl = self.curr_ns.declare_value(method.name, IRValueDecl(IRUnresolvedUnknownType(), method.loc, False))
            self.value_decls[method] = decl
        self.pop()
        self.trait_type_decls[trait] = type_decl

    def resolve_imports(self):
        file_paths: dict[Path, ASTFile] = {file.path.resolve(): file for file in self.program.files}
        self.push(self.program_namespace)
        all_imports: list[tuple[ASTImport, Namespace]] = []
        for file in self.program.files:
            ns = self.file_namespaces[file]
            for top_level in file.top_levels:
                if isinstance(top_level, ASTImport):
                    all_imports.append((top_level, ns))
                    ns.not_yet_imported.add(top_level.as_name)

        waiting_imports: list[tuple[ASTImport, Namespace]] = []
        while all_imports:
            ast_import: ASTImport
            import_ns: Namespace
            ast_import, import_ns = all_imports.pop()
            file_ns = self.file_namespaces[file_paths[ast_import.path.resolve()]]
            if len(ast_import.names) == 0:
                import_ns.declare_namespace(ast_import.path.stem, file_ns, ast_import.loc)
                all_imports.extend(waiting_imports)
                waiting_imports.clear()
            else:
                ns = file_ns
                for namespace_name in ast_import.names[:-1]:
                    if namespace_name in ns.not_yet_imported:
                        break
                    ns = ns.get_namespace(namespace_name, ast_import.loc)
                else:
                    name = ast_import.names[-1]
                    if name not in ns.not_yet_imported:
                        any_imported = False
                        if ns.has_namespace(name):
                            import_ns.declare_namespace(ast_import.as_name, ns.get_namespace(name, ast_import.loc), ast_import.loc)
                            any_imported = True
                        if ns.has_value(name):
                            import_ns.declare_value(ast_import.as_name, ns.get_value(name, ast_import.loc))
                            any_imported = True
                        if ns.has_type(name):
                            import_ns.declare_type(ast_import.as_name, ns.get_type(name, ast_import.loc))
                            any_imported = True
                        if not any_imported:
                            raise CompilerMessage(ErrorType.COMPILATION, f"No name '{name}' in '{ast_import.path}'", ast_import.loc)
                        # if we've imported something, break the for-loop and go through the while loop agan
                        all_imports.extend(waiting_imports)
                        waiting_imports.clear()
                    else:
                        waiting_imports.append((ast_import, import_ns))
        if len(waiting_imports) != 0:
            raise CompilerMessage(ErrorType.COMPILATION, f"Cyclic imports detected, one such shown below", waiting_imports[0][0].loc)

    def resolve_names(self) -> IRProgram:
        self.push(self.program_namespace)
        for file in self.program.files:
            self.resolve_file(file)
        self.pop()
        return self.ir_program

    def resolve_file(self, file: ASTFile):
        self.push(self.file_namespaces[file])
        for top_level in file.top_levels:
            if isinstance(top_level, ASTFunction):
                self.resolve_function(top_level, file.is_main)
            elif isinstance(top_level, ASTStruct):
                self.resolve_struct(top_level)
            elif isinstance(top_level, ASTImport):
                pass
            elif isinstance(top_level, ASTTrait):
                self.resolve_trait(top_level)
            else:
                raise ValueError(top_level.__class__)
        self.pop()

    def resolve_trait(self, trait: ASTTrait):
        trait_type_decl = self.trait_type_decls[trait]

        type_var_ns = self.push(Namespace())
        type_args: list[IRTypeVarType] = []
        for type_var in trait.type_variables:
            if type_var.bound is None:
                bound = None
            else:
                bound = self.resolve_type(type_var.bound)
            var = IRTypeVariable(type_var.name, bound, IRTypeDecl(IRUnresolvedUnknownType(), type_var.loc)).set_loc(
                type_var.loc)
            type_var_ns.declare_type(type_var.name, var.type_decl)
            var.type_decl.type = IRTypeVarType(var).set_loc(type_var.loc)
            type_args.append(var.type_decl.type)

        used_names: set[str] = set()

        methods: list[IRMethod] = []
        for method in trait.methods:
            if method.name in used_names:
                raise CompilerMessage(ErrorType.COMPILATION, f"Name {method.name} already used for a method on this trait", method.loc)
            else:
                used_names.add(method.name)

            ret_type = self.resolve_type(method.return_type)

            body_ns = self.push(Namespace())
            params: list[IRParameter] = []
            if method.self_name is not None:
                self_decl = self.curr_ns.declare_value(method.self_name.text, IRValueDecl(IRUnresolvedUnknownType(), BuiltinLocation(), True))
                param = IRParameter(self_decl, method.name, IRUnresolvedNameType(trait_type_decl)).set_loc(method.self_name.location)
                params.append(param)
            for param in method.parameters:
                param_decl = self.curr_ns.declare_value(param.name, IRValueDecl(IRUnresolvedUnknownType(), param.loc, True))
                param = IRParameter(param_decl, param.name, self.resolve_type(param.type)).set_loc(param.loc)
                params.append(param)

            body = self.resolve_body(method.body, self.pop())

            func = IRFunction(self.value_decls[method], method.name, tuple(type_args), params, ret_type, body, False, False, None).set_loc(method.loc)
            method = IRMethod(func.name, method.is_virtual, method.is_static, method.self_name is not None, func).set_loc(method.loc)
            methods.append(method)
        self.pop()

        type = IRTrait(trait_type_decl, trait.name, methods, tuple(type_args), {}, None).set_loc(trait.loc)
        trait_type_decl.type = type

        self.ir_program.traits.append(type)

    def resolve_struct(self, struct: ASTStruct):
        struct_type_decl = self.struct_type_decls[struct]

        type_var_ns = self.push(Namespace())
        type_args: list[IRTypeVarType] = []
        for type_var in struct.type_variables:
            if type_var.bound is None:
                bound = None
            else:
                bound = self.resolve_type(type_var.bound)
            var = IRTypeVariable(type_var.name, bound, IRTypeDecl(IRUnresolvedUnknownType(), type_var.loc)).set_loc(type_var.loc)
            type_var_ns.declare_type(type_var.name, var.type_decl)
            var.type_decl.type = IRTypeVarType(var).set_loc(type_var.loc)
            type_args.append(var.type_decl.type)

        supertraits = []
        for supertrait in struct.traits:
            supertraits.append(self.resolve_type(supertrait))

        used_names: set[str] = set()

        fields = []
        for field in struct.fields:
            if field.name in used_names:
                raise CompilerMessage(ErrorType.COMPILATION, f"Name {field.name} already used for an attribute on this struct", field.loc)
            else:
                used_names.add(field.name)
            fields.append(IRField(field.name, self.resolve_type(field.type)).set_loc(field.loc))

        methods: list[IRMethod] = []
        for method in struct.methods:
            if method.name in used_names:
                raise CompilerMessage(ErrorType.COMPILATION, f"Name {method.name} already used for an attribute on this struct", method.loc)
            else:
                used_names.add(method.name)

            ret_type = self.resolve_type(method.return_type)

            body_ns = self.push(Namespace())
            params: list[IRParameter] = []
            if method.self_name is not None:
                self_decl = self.curr_ns.declare_value(method.self_name.text, IRValueDecl(IRUnresolvedUnknownType(), BuiltinLocation(), True))
                param = IRParameter(self_decl, method.name, IRUnresolvedNameType(struct_type_decl)).set_loc(method.self_name.location)
                params.append(param)
            for param in method.parameters:
                param_decl = self.curr_ns.declare_value(param.name, IRValueDecl(IRUnresolvedUnknownType(), param.loc, True))
                param = IRParameter(param_decl, param.name, self.resolve_type(param.type)).set_loc(param.loc)
                params.append(param)

            body = self.resolve_body(method.body, self.pop())

            func = IRFunction(self.value_decls[method], method.name, tuple(type_args), params, ret_type, body, False, False, None).set_loc(method.loc)
            method = IRMethod(func.name, False, method.is_static, method.self_name is not None, func).set_loc(method.loc)
            methods.append(method)
        self.pop()

        type = IRStruct(struct_type_decl, self.value_decls[struct], struct.name, supertraits, fields, methods, tuple(type_args), {}, None).set_loc(struct.loc)
        struct_type_decl.type = type

        self.ir_program.structs.append(type)

    def resolve_function(self, function: ASTFunction, is_main_file: bool):
        body_ns = self.push(Namespace())
        type_vars: list[IRResolvedType] = []
        if isinstance(function, ASTGenericFunction):
            for type_var in function.type_vars:
                if type_var.bound is None:
                    bound = None
                else:
                    bound = self.resolve_type(type_var.bound)
                type_decl = body_ns.declare_type(type_var.name, IRTypeDecl(IRUnresolvedUnknownType(), type_var.loc))
                type_var = IRTypeVariable(type_var.name, bound, type_decl).set_loc(type_var.loc)
                type_decl.type = IRTypeVarType(type_var)
                type_vars.append(type_decl.type)

        ret_type = self.resolve_type(function.return_type)

        params = []
        for param in function.parameters:
            param_decl = self.curr_ns.declare_value(param.name, IRValueDecl(IRUnresolvedUnknownType(), param.loc, True))
            params.append(IRParameter(param_decl, param.name, self.resolve_type(param.type)).set_loc(param.loc))

        body = self.resolve_body(function.body, self.pop())
        func = IRFunction(self.value_decls[function], function.name, tuple(type_vars), params, ret_type, body, function.is_extern, False, None).set_loc(function.loc)

        if function.name == "main" and is_main_file:
            if len(type_vars) > 0:
                raise CompilerMessage(ErrorType.COMPILATION, "Main function cannot be generic", func.loc)
            self.ir_program.main_func = func
        self.ir_program.functions.append(func)

    def resolve_stmt(self, stmt: ASTStmt) -> IRStmt:
        if isinstance(stmt, ASTLetStmt) or isinstance(stmt, ASTVarStmt):
            decl = self.curr_ns.declare_value(stmt.name, IRValueDecl(IRUnresolvedUnknownType(), stmt.loc, True))
            if stmt.type is None:
                type = IRUnresolvedUnknownType()
            else:
                type = self.resolve_type(stmt.type)
            return IRDeclStmt(decl, type, self.resolve_expr(stmt.init)).set_loc(stmt.loc)
        elif isinstance(stmt, ASTExprStmt):
            return IRExprStmt(self.resolve_expr(stmt.expr)).set_loc(stmt.loc)
        elif isinstance(stmt, ASTWhileStmt):
            return IRWhileStmt(self.resolve_expr(stmt.cond), self.resolve_expr(stmt.body)).set_loc(stmt.loc)
        # elif isinstance(stmt, ASTForStmt):
        #     self.push(Namespace())
        #     decl = self.curr_ns.declare_value(stmt.iter_var, IRValueDecl(IRUnresolvedUnknownType(), stmt.iterator.loc, True))
        #     ir_stmt = IRForStmt(decl, self.resolve_expr(stmt.iterator), self.resolve_expr(stmt.body)).set_loc(stmt.loc)
        #     self.pop()
        #     return ir_stmt
        elif isinstance(stmt, ASTReturnStmt):
            return IRReturnStmt(self.resolve_expr(stmt.expr)).set_loc(stmt.loc)
        else:
            raise ValueError()

    def resolve_namespace(self, namespace: ASTNamespace) -> Namespace:
        if namespace.ns is None:
            return self.get_namespace(namespace.name, namespace.loc)
        else:
            ns = self.resolve_namespace(namespace.ns)
            return ns.get_namespace(namespace.name, namespace.loc)

    def resolve_expr(self, expr: ASTExpr) -> IRExpr:
        if isinstance(expr, ASTBlockExpr):
            return self.resolve_body(expr)
        elif isinstance(expr, ASTIfExpr):
            return IRIf(self.resolve_expr(expr.cond), self.resolve_expr(expr.then_do), None if expr.else_do is None else self.resolve_expr(expr.else_do)).set_loc(expr.loc)
        elif isinstance(expr, ASTBinaryExpr):
            return IRBinaryExpr(expr.NAME, self.resolve_expr(expr.left), self.resolve_expr(expr.right)).set_loc(expr.loc)
        elif isinstance(expr, ASTAttrExpr):
            return IRAttrExpr(self.resolve_expr(expr.object), expr.attr).set_loc(expr.loc)
        elif isinstance(expr, ASTCallExpr):
            return IRCallExpr(self.resolve_expr(expr.callee), [self.resolve_expr(arg) for arg in expr.arguments]).set_loc(expr.loc)
        elif isinstance(expr, ASTGenericExpr):
            return IRGenericExpr(cast(IRNameExpr, self.resolve_expr(expr.generic)), [self.resolve_type(arg) for arg in expr.arguments]).set_loc(expr.loc)
        elif isinstance(expr, ASTIntegerExpr):
            return IRIntegerExpr(expr.number).set_loc(expr.loc)
        elif isinstance(expr, ASTNegExpr):
            return IRNegExpr(self.resolve_expr(expr.right)).set_loc(expr.loc)
        elif isinstance(expr, ASTNotExpr):
            return IRNotExpr(self.resolve_expr(expr.right)).set_loc(expr.loc)
        elif isinstance(expr, ASTNameExpr):
            if expr.ns is None:
                return IRNameExpr(self.get_value(expr.ident, expr.loc)).set_loc(expr.loc)
            else:
                ns = self.resolve_namespace(expr.ns)
                return IRNameExpr(ns.get_value(expr.ident, expr.loc)).set_loc(expr.loc)
        elif isinstance(expr, ASTAssign):
            return IRAssign(self.get_value(expr.name, expr.loc), expr.op, self.resolve_expr(expr.value)).set_loc(expr.loc)
        elif isinstance(expr, ASTAttrAssign):
            return IRAttrAssign(self.resolve_expr(expr.obj), expr.attr, expr.op, self.resolve_expr(expr.value)).set_loc(expr.loc)
        elif isinstance(expr, ASTLambda):
            if expr.ret_type is not None:
                ret_type = self.resolve_type(expr.ret_type)
            else:
                ret_type = IRUnresolvedUnknownType()

            expr_ns = self.push(Namespace(is_lambda=True))
            params = []
            for param in expr.parameters:
                param_decl = self.curr_ns.declare_value(param.name, IRValueDecl(IRUnresolvedUnknownType(), param.loc, True))
                params.append(IRParameter(param_decl, param.name, self.resolve_type(param.type) if param.type is not None else IRUnresolvedUnknownType()).set_loc(param.loc))

            expr_expr = self.resolve_expr(expr.expr)

            self.pop()
            exterior_names = expr_ns.exterior_names
            for exterior_name in exterior_names:
                exterior_name.put_in_closure = True

            return IRLambda(exterior_names, params, ret_type, IRBlock([IRExprStmt(expr_expr).set_loc(expr.expr.loc)], list(expr_ns.value_names.values()), False).set_loc(expr.expr.loc)).set_loc(expr.loc)
        elif isinstance(expr, ASTIndexOrGenericExpr):
            obj = cast(IRNameExpr, self.resolve_expr(expr.obj))
            try:
                arg_as_type = self.resolve_type(expr.index_or_arg.as_type())
            except CompilerMessage:
                arg_as_type = None
            try:
                arg_as_expr = self.resolve_expr(expr.index_or_arg.as_expr())
            except CompilerMessage:
                if arg_as_type is None:
                    raise
                else:
                    arg_as_expr = None
            if arg_as_type is None:
                return IRIndexExpr(obj, arg_as_expr).set_loc(expr.loc)
            elif arg_as_expr is None:
                return IRGenericExpr(obj, [arg_as_type]).set_loc(expr.loc)
            else:
                return IRGenericOrIndexExpr(obj, arg_as_type, arg_as_expr).set_loc(expr.loc)
        elif isinstance(expr, ASTGenericAttrExpr):
            return IRGenericAttrExpr(self.resolve_type(expr.generic), expr.name).set_loc(expr.loc)
        elif isinstance(expr, ASTIndexExpr):
            return IRIndexExpr(self.resolve_expr(expr.obj), self.resolve_expr(expr.index)).set_loc(expr.loc)
        else:
            raise ValueError(expr.__class__)

    def resolve_body(self, body: ASTBlockExpr, ns: Namespace = None) -> IRBlock:
        if ns is None:
            ns = Namespace()

        self.push(ns)
        stmts = []
        for stmt in body.stmts:
            stmts.append(self.resolve_stmt(stmt))
        ns = self.pop()
        return IRBlock(stmts, list(ns.value_names.values()), body.return_unit).set_loc(body.loc)

    def resolve_type(self, type: ASTType) -> IRType:
        if isinstance(type, ASTNameType):
            if type.ns is None:
                return IRUnresolvedNameType(self.get_type(type.name, type.loc)).set_loc(type.loc)
            else:
                ns = self.resolve_namespace(type.ns)
                return IRUnresolvedNameType(ns.get_type(type.name, type.loc)).set_loc(type.loc)
        elif isinstance(type, ASTGenericType):
            return IRUnresolvedGenericType(self.resolve_type(type.generic), [self.resolve_type(arg) for arg in type.type_arguments]).set_loc(type.loc)
        elif isinstance(type, ASTUnitType):
            return IRUnitType().set_loc(type.loc)
        elif isinstance(type, ASTFunctionType):
            return IRUnresolvedFunctionType([self.resolve_type(param) for param in type.parameters], self.resolve_type(type.ret_type)).set_loc(type.loc)
        else:
            raise ValueError(type)