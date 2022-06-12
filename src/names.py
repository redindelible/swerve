from __future__ import annotations

from typing import cast

from swc_ast import *
from swc_ir import *
from common import BuiltinLocation, CompilerMessage, ErrorType, Location, Path


def resolve_names(program: ASTProgram):
    resolver = ResolveNames(program)
    resolver.collect_names()
    resolver.resolve_imports()
    return resolver.resolve_names()


class Namespace:
    def __init__(self, *, is_lambda: bool = False):
        self.value_names: dict[str, IRValueDecl] = {}
        self.type_names: dict[str, IRTypeDecl] = {}
        self.namespace_names: dict[str, Namespace] = {}

        self.is_lambda = is_lambda
        self.exterior_names: list[IRValueDecl] = []

        self.not_yet_imported: set[str] = set()

    def declare_namespace(self, name: str, namespace: Namespace, loc: Location) -> Namespace:
        validate_name(name, loc)
        if self.has_namespace(name):
            raise CompilerMessage(ErrorType.COMPILATION, f"Name '{name}' is already used as a namespace in this scope", loc)
        self.namespace_names[name] = namespace
        return namespace

    def has_namespace(self, name: str) -> bool:
        return name in self.namespace_names

    def get_namespace(self, name: str, loc: Location) -> Namespace:
        if self.has_namespace(name):
            return self.namespace_names[name]
        else:
            raise CompilerMessage(ErrorType.COMPILATION, f"Name '{name}' does not exist for a namespace in this scope", loc)

    def has_value(self, name: str) -> bool:
        return name in self.value_names

    def declare_value(self, name: str, decl: IRValueDecl) -> IRValueDecl:
        validate_name(name, decl.location)
        if self.has_value(name):
            raise CompilerMessage(ErrorType.COMPILATION, f"Name '{name}' is already used as a value in this scope", decl.location,
                                  [CompilerMessage(ErrorType.NOTE, "Previously declared here", self.get_value(name, decl.location).location)])
        self.value_names[name] = decl
        return decl

    def get_value(self, name: str, loc: Location) -> IRValueDecl:
        if self.has_value(name):
            return self.value_names[name]
        else:
            raise CompilerMessage(ErrorType.COMPILATION, f"Name '{name}' does not exist for a value in this scope", loc)

    def has_type(self, name: str) -> bool:
        return name in self.type_names

    def declare_type(self, name: str, decl: IRTypeDecl) -> IRTypeDecl:
        validate_name(name, decl.location)
        if self.has_type(name):
            raise CompilerMessage(ErrorType.COMPILATION, f"Name '{name}' is already used as a type in this scope", decl.location,
                                  [CompilerMessage(ErrorType.NOTE, "Previously declared here", self.get_type(name, decl.location).location)])
        self.type_names[name] = decl
        return decl

    def get_type(self, name: str, loc: Location) -> IRTypeDecl:
        if self.has_type(name):
            return self.type_names[name]
        else:
            raise CompilerMessage(ErrorType.COMPILATION, f"Name '{name}' does not exist for a type in this scope", loc)


def check_name(name: str) -> bool:
    if len(name) == 0:
        return False
    if not (name[0] == "_" or name[0].isalpha()):
        return False
    if not all(c == "_" or c.isalnum() for c in name[1:]):
        return False
    return True


def validate_name(name: str, loc: Location):
    if not check_name(name):
        raise CompilerMessage(ErrorType.COMPILATION, f"'{name}' is not a valid name", loc)


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

    def create_array_type(self) -> IRGenericStruct:
        array_loc = BuiltinLocation()
        array_type_var = IRTypeVariable("Item", None, IRTypeDecl(IRUnresolvedUnknownType(), array_loc))
        type_var = array_type_var.type_decl.type = IRTypeVarType(array_type_var)
        array = IRGenericStruct(
            IRTypeDecl(IRUnresolvedUnknownType(), array_loc),
            IRValueDecl(IRUnresolvedUnknownType(), array_loc, False),
            "array", [array_type_var], [], [], [], {}
        )
        array_type = array.type_decl.type = IRGenericStructType(array, [type_var])

        array.constructor.type = IRGenericFunctionType(
            [array_type_var],
            [IRParameterType(IRIntegerType(64), array_loc), IRParameterType(IRFunctionType(
                [IRParameterType(IRIntegerType(64), array_loc)], type_var
            ), array_loc)], array_type,
            self.array_callback
        )
        return array

    def array_callback(self, arguments: list[IRResolvedType], loc: Location) -> tuple[IRFunctionType, IRExpr]:
        if len(arguments) != 1:
            raise CompilerMessage(ErrorType.COMPILATION, f"Mismatched number of arguments to generic (expected 1, got {len(arguments)}):", loc)
        type = arguments[0]
        if type not in self.ir_program.array_variants:
            if type.is_concrete():
                self.create_specific_array_type(type)
            else:
                raise ValueError()
        variant = self.ir_program.array_variants[type]
        constructor = variant.constructor
        return cast(IRFunctionType, constructor.type), IRNameExpr(constructor).set_loc(loc)

    def create_specific_array_type(self, type: IRResolvedType):
        array_loc = BuiltinLocation()
        array_constructor = IRValueDecl(IRUnresolvedUnknownType(), array_loc, False)
        array = IRStruct(
            IRTypeDecl(IRUnresolvedUnknownType(), array_loc),
            array_constructor,
            f"array[{type}]", [], [], []
        )
        array_type = array.type_decl.type = IRStructType(array)

        array.constructor.type = IRFunctionType(
            [IRParameterType(IRIntegerType(64), array_loc), IRParameterType(IRFunctionType(
                [IRParameterType(IRIntegerType(64), array_loc)], type
            ), array_loc)], array_type,
        )

        get_type = IRFunctionType([IRParameterType(array_type, array_loc), IRParameterType(IRIntegerType(64), array_loc)], type)
        get_decl = IRValueDecl(get_type, array_loc, False)
        get_method = IRMethod(
            "get", True, True,
            IRFunction(False, get_decl, f"array[{type}]::get", [
                IRParameter(IRValueDecl(array_type, array_loc, True), "self", array_type),
                IRParameter(IRValueDecl(IRIntegerType(64), array_loc, True), "index", IRIntegerType(64))
            ], type, IRBlock([], [], False))
        )
        get_method.function.function_type = get_type
        array.methods.append(get_method)

        set_type = IRFunctionType([IRParameterType(array_type, array_loc), IRParameterType(IRIntegerType(64), array_loc), IRParameterType(type, array_loc)], IRUnitType())
        set_decl = IRValueDecl(set_type, array_loc, False)
        set_method = IRMethod(
            "set", True, True,
            IRFunction(False, set_decl, f"array[{type}]::set", [
                IRParameter(IRValueDecl(array_type, array_loc, True), "self", array_type),
                IRParameter(IRValueDecl(IRIntegerType(64), array_loc, True), "index", IRIntegerType(64)),
                IRParameter(IRValueDecl(type, array_loc, True), "value", type)
            ], IRUnitType(), IRBlock([], [], True))
        )
        set_method.function.function_type = set_type
        array.methods.append(set_method)

        self.ir_program.array_variants[type] = ArrayVariant(type, array, array_constructor, get_decl, set_decl)

    def collect_program(self, program: ASTProgram):
        ns = self.push(self.program_namespace)
        ns.declare_type("int", IRTypeDecl(IRIntegerType(64), BuiltinLocation()))
        ns.declare_type("str", IRTypeDecl(IRStringType(), BuiltinLocation()))
        ns.declare_type("bool", IRTypeDecl(IRBoolType(), BuiltinLocation()))

        array = self.create_array_type()

        ns.declare_type("array", array.type_decl)
        ns.declare_value("array", array.constructor)

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
        self.pop()

    def resolve_struct(self, struct: ASTStruct):
        struct_type_decl = self.struct_type_decls[struct]

        type_var_ns = self.push(Namespace())
        type_vars: list[IRTypeVariable] = []
        for type_var in struct.type_variables:
            if type_var.bound is None:
                bound = None
            else:
                bound = self.resolve_type(type_var.bound)
            type_decl = type_var_ns.declare_type(type_var.name, IRTypeDecl(IRUnresolvedUnknownType(), type_var.loc))
            type_vars.append(IRTypeVariable(type_var.name, bound, type_decl).set_loc(type_var.loc))

        supertraits = []
        for supertrait in struct.supertraits:
            supertraits.append(self.resolve_type(supertrait))

        fields = []
        for field in struct.fields:
            fields.append(IRField(field.name, self.resolve_type(field.type)).set_loc(field.loc))

        methods: list[IRMethod] = []
        for method in struct.methods:
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

            func = IRFunction(False, self.value_decls[method], method.name, params, ret_type, body).set_loc(method.loc)
            method = IRMethod(func.name, method.is_static, method.self_name is not None, func).set_loc(method.loc)
            methods.append(method)
        self.pop()

        if len(type_vars) > 0:
            type = IRGenericStruct(struct_type_decl, self.value_decls[struct], struct.name, type_vars, supertraits, fields, methods, {})
        else:
            type = IRStruct(struct_type_decl, self.value_decls[struct], struct.name, supertraits, fields, methods)
        struct_type_decl.type = type

        self.ir_program.structs.append(type)

    def resolve_function(self, function: ASTFunction, is_main_file: bool):
        body_ns = self.push(Namespace())
        type_vars = []
        if isinstance(function, ASTGenericFunction):
            for type_var in function.type_vars:
                if type_var.bound is None:
                    bound = None
                else:
                    bound = self.resolve_type(type_var.bound)
                type_decl = body_ns.declare_type(type_var.name, IRTypeDecl(IRUnresolvedUnknownType(), type_var.loc))
                type_vars.append(IRTypeVariable(type_var.name, bound, type_decl).set_loc(type_var.loc))

        ret_type = self.resolve_type(function.return_type)

        params = []
        for param in function.parameters:
            param_decl = self.curr_ns.declare_value(param.name, IRValueDecl(IRUnresolvedUnknownType(), param.loc, True))
            params.append(IRParameter(param_decl, param.name, self.resolve_type(param.type)).set_loc(param.loc))

        body = self.resolve_body(function.body, self.pop())
        if len(type_vars) > 0:
            func = IRGenericFunction(self.value_decls[function], function.name, type_vars, params, ret_type, body).set_loc(function.loc)
        else:
            func = IRFunction(function.is_extern, self.value_decls[function], function.name, params, ret_type, body).set_loc(function.loc)

        if function.name == "main" and is_main_file:
            if len(type_vars) > 0:
                raise CompilerMessage(ErrorType.COMPILATION, "Main function cannot be generic", func.loc)
            self.ir_program.main_func = func
        self.ir_program.functions.append(func)

    def resolve_stmt(self, stmt: ASTStmt) -> IRStmt:
        if isinstance(stmt, ASTLetStmt) or isinstance(stmt, ASTVarStmt):
            decl = self.curr_ns.declare_value(stmt.name, IRValueDecl(IRUnresolvedUnknownType(), stmt.loc, True))
            # print("when made", decl, "in", self.curr_ns)
            if stmt.type is None:
                type = IRUnresolvedUnknownType()
            else:
                type = self.resolve_type(stmt.type)
            return IRDeclStmt(decl, type, self.resolve_expr(stmt.init)).set_loc(stmt.loc)
        elif isinstance(stmt, ASTExprStmt):
            return IRExprStmt(self.resolve_expr(stmt.expr)).set_loc(stmt.loc)
        elif isinstance(stmt, ASTWhileStmt):
            return IRWhileStmt(self.resolve_expr(stmt.cond), self.resolve_expr(stmt.body)).set_loc(stmt.loc)
        elif isinstance(stmt, ASTForStmt):
            self.push(Namespace())
            decl = self.curr_ns.declare_value(stmt.iter_var, IRValueDecl(IRUnresolvedUnknownType(), stmt.iterator.loc, True))
            ir_stmt = IRForStmt(decl, self.resolve_expr(stmt.iterator), self.resolve_expr(stmt.body)).set_loc(stmt.loc)
            self.pop()
            return ir_stmt
        elif isinstance(stmt, ASTReturnStmt):
            return IRReturnStmt(self.resolve_expr(stmt.expr)).set_loc(stmt.loc)
        else:
            raise ValueError()

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
            return IRGenericExpr(self.resolve_expr(expr.generic), [self.resolve_type(arg) for arg in expr.arguments]).set_loc(expr.loc)
        elif isinstance(expr, ASTIntegerExpr):
            return IRIntegerExpr(expr.number).set_loc(expr.loc)
        elif isinstance(expr, ASTStringExpr):
            return IRStringExpr(expr.string).set_loc(expr.loc)
        elif isinstance(expr, ASTGroupExpr):
            return self.resolve_expr(expr.expr).set_loc(expr.loc)
        elif isinstance(expr, ASTNegExpr):
            return IRNegExpr(self.resolve_expr(expr.right)).set_loc(expr.loc)
        elif isinstance(expr, ASTNotExpr):
            return IRNotExpr(self.resolve_expr(expr.right)).set_loc(expr.loc)
        elif isinstance(expr, ASTIdentExpr):
            return IRNameExpr(self.get_value(expr.ident, expr.loc)).set_loc(expr.loc)
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
                params.append(IRParameter(param_decl, param.name, self.resolve_type(param.type) if param.type is not None else IRUnresolvedUnknownType()))

            expr_expr = self.resolve_expr(expr.expr)

            self.pop()
            exterior_names = expr_ns.exterior_names
            for exterior_name in exterior_names:
                exterior_name.put_in_closure = True

            return IRLambda(exterior_names, params, ret_type, IRBlock([IRExprStmt(expr_expr).set_loc(expr.expr.loc)], list(expr_ns.value_names.values()), False).set_loc(expr.expr.loc)).set_loc(expr.loc)
        else:
            raise ValueError()

    def resolve_body(self, body: ASTBlockExpr, ns: Namespace = None) -> IRBlock:
        if ns is None:
            ns = Namespace()

        self.push(ns)
        stmts = []
        for stmt in body.stmts:
            stmts.append(self.resolve_stmt(stmt))
        ns = self.pop()
        # print(ns.value_names)
        return IRBlock(stmts, list(ns.value_names.values()), body.return_unit).set_loc(body.loc)

    def resolve_type(self, type: ASTType) -> IRType:
        if isinstance(type, ASTTypeIdent):
            return IRUnresolvedNameType(self.get_type(type.name, type.loc)).set_loc(type.loc)
        elif isinstance(type, ASTTypeGeneric):
            return IRUnresolvedGenericType(self.resolve_type(type.generic), [self.resolve_type(arg) for arg in type.type_arguments]).set_loc(type.loc)
        elif isinstance(type, ASTTypeUnit):
            return IRUnitType().set_loc(type.loc)
        elif isinstance(type, ASTTypeFunction):
            return IRUnresolvedFunctionType([self.resolve_type(param) for param in type.parameters], self.resolve_type(type.ret_type)).set_loc(type.loc)
        else:
            raise ValueError(type)