from __future__ import annotations

from ast import *
from ir import IRValueDecl, IRTypeDecl
from common import BuiltinLocation, CompilerMessage, ErrorType, Location, Path


def resolve_names(program: ASTProgram):
    resolver = ResolveNames(program)
    resolver.collect_names()
    resolver.resolve_imports()


class Namespace:
    def __init__(self):
        self.value_names: dict[str, IRValueDecl] = {}
        self.type_names: dict[str, IRTypeDecl] = {}
        self.namespace_names: dict[str, Namespace] = {}

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

        self.program_namespace = Namespace()
        self.namespaces: list[Namespace] = []

        self.file_namespaces: dict[ASTFile, Namespace] = {}

        self.value_decls: dict[ASTNode, IRValueDecl] = {}

    def push(self, ns: Namespace):
        self.namespaces.append(ns)

    def pop(self) -> Namespace:
        return self.namespaces.pop()

    @property
    def curr_ns(self) -> Namespace:
        return self.namespaces[-1]

    def declare_value(self, name: str, decl: IRValueDecl) -> IRValueDecl:
        self.namespaces[-1].value_names[name] = decl
        return decl

    def declare_type(self, name: str, decl: IRTypeDecl) -> IRTypeDecl:
        self.namespaces[-1].type_names[name] = decl
        return decl

    def collect_names(self):
        self.collect_program(self.program)

    def collect_program(self, program: ASTProgram):
        self.push(self.program_namespace)
        self.declare_type("int", IRTypeDecl(None, BuiltinLocation()))
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
        decl = self.declare_value(function.name, IRValueDecl(None, function.location))
        self.value_decls[function] = decl

    def collect_struct(self, struct: ASTStruct):
        type_decl = self.declare_type(struct.name, IRTypeDecl(None, struct.location))

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
                import_ns.declare_namespace(ast_import.path.stem, file_ns, ast_import.location)
                all_imports.extend(waiting_imports)
                waiting_imports.clear()
            else:
                ns = file_ns
                for namespace_name in ast_import.names[:-1]:
                    if namespace_name in ns.not_yet_imported:
                        break
                    ns = ns.get_namespace(namespace_name, ast_import.location)
                else:
                    name = ast_import.names[-1]
                    if name not in ns.not_yet_imported:
                        any_imported = False
                        if ns.has_namespace(name):
                            import_ns.declare_namespace(ast_import.as_name, ns.get_namespace(name, ast_import.location), ast_import.location)
                            any_imported = True
                        if ns.has_value(name):
                            import_ns.declare_value(ast_import.as_name, ns.get_value(name, ast_import.location))
                            any_imported = True
                        if ns.has_type(name):
                            import_ns.declare_type(ast_import.as_name, ns.get_type(name, ast_import.location))
                            any_imported = True
                        if not any_imported:
                            raise CompilerMessage(ErrorType.COMPILATION, f"No name '{name}' in '{ast_import.path}'", ast_import.location)
                        # if we've imported something, break the for-loop and go through the while loop agan
                        all_imports.extend(waiting_imports)
                        waiting_imports.clear()
                    else:
                        waiting_imports.append((ast_import, import_ns))
        if len(waiting_imports) != 0:
            raise CompilerMessage(ErrorType.COMPILATION, f"Cyclic imports, one such shown below", waiting_imports[0][0].location)

    def resolve_names(self):
        self.push(self.program_namespace)
        for file in self.program.files:
            self.resolve_file(file)

    def resolve_file(self, file: ASTFile):
        self.push(self.file_namespaces[file])
        for top_level in file.top_levels:
            if isinstance(top_level, ASTFunction):
                pass