from __future__ import annotations

from ast import *
from ir import IRValueDecl, IRTypeDecl
from common import BuiltinLocation, CompilerMessage


class Namespace:
    def __init__(self):
        self.value_names: dict[str, IRValueDecl] = {}
        self.type_names: dict[str, IRTypeDecl] = {}
        self.namespace_names: dict[str, Namespace] = {}


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

    def declare_namespace(self, name: str, namespace: Namespace) -> Namespace:
        self.namespaces[-1].namespace_names[name] = namespace
        return namespace

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
            else:
                raise Exception()
        self.file_namespaces[file] = self.pop()

    def collect_function(self, function: ASTFunction):
        decl = self.declare_value(function.name, IRValueDecl(None, function.location))
        self.value_decls[function] = decl

    def collect_struct(self, struct: ASTStruct):
        type_decl = self.declare_type(struct.name, IRTypeDecl(None, struct.location))

    # def resolve_names(self):
    #     self.push(self.program_namespace)
    #     for file in self.program.files:
    #         self.resolve_file()
    #
    # def resolve_file(self):