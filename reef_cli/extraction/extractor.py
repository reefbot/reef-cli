import logging
import pathlib
from dataclasses import dataclass, field
import typing as ty

import libcst as cst
from libcst.metadata import ParentNodeProvider, PositionProvider, QualifiedNameProvider

logger = logging.getLogger("reef")


# Base graph elements
@dataclass
class Node:
    name: str
    file_path: pathlib.Path
    qualified_name: str

@dataclass
class FileNode(Node):
    pass

@dataclass
class ModuleNode(Node):
    pass

@dataclass
class FuncNode(Node):
    body: str
    code: str
    line_number_start: int
    line_number_end: int

@dataclass
class ClassNode(Node):
    body: str
    code: str
    line_number_start: int
    line_number_end: int
    base_classes: list[str] = field(default_factory=list)

@dataclass
class ImportNode(Node):
    origin: str
    alias: str = ""

@dataclass
class Edge:
    source: str
    target: str
    kind: str  # 'defines', 'imports', 'calls', 'inherits'


class Extractor(cst.CSTVisitor):
    METADATA_DEPENDENCIES = (ParentNodeProvider, PositionProvider, QualifiedNameProvider)

    def __init__(self, file_path: pathlib.Path, project_root: pathlib.Path) -> None:
        self.file_path = file_path
        self.project_root = project_root

        self.functions: list[FuncNode] = []
        self.classes: list[ClassNode] = []
        self.imports: list[ImportNode] = []
        self.edges: list[Edge] = []
        self.calls: list[Edge] = []

        self.module_name = self._get_module_name()
        self.current_scope: list[str] = []  # For tracking nesting

    def _get_module_name(self):
        rel_path = pathlib.Path(self.file_path).relative_to(self.project_root)
        return ".".join(rel_path.with_suffix("").parts)

    @staticmethod
    def _get_qualified_name_from_call(node: cst.Call) -> ty.Optional[str]:
        """
        Given a libcst Call node, extract the fully qualified name
        of the function/class being called, if possible.
        Returns None if it cannot be resolved statically.
        """
        func_expr = node.func  # This is the expression being called

        def _recursively_get_name(expr) -> ty.Optional[str]:
            if isinstance(expr, cst.Name):
                return expr.value  # simple name
            elif isinstance(expr, cst.Attribute):
                parent = _recursively_get_name(expr.value)
                if parent is None:
                    return None
                return f"{parent}.{expr.attr.value}"
            else:
                # Could be a Subscript, Call, Lambda, or something else - too dynamic
                return None

        return _recursively_get_name(func_expr)

    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:
        parent = self.get_metadata(ParentNodeProvider, node)

        if not isinstance(parent, cst.ClassDef):
            pos = self.get_metadata(PositionProvider, node)
            qname = f"{self.module_name}.{node.name.value}"
            func_node = FuncNode(
                name=node.name.value,
                body=cst.Module([]).code_for_node(node.body),
                code=cst.Module([]).code_for_node(node),
                line_number_start=pos.start.line,
                line_number_end=pos.end.line,
                file_path=self.file_path,
                qualified_name=qname,
            )
            self.functions.append(func_node)
            self.edges.append(Edge(source=self.module_name, target=qname, kind="defines"))
            self.current_scope.append(qname)

    def leave_FunctionDef(self, node: cst.FunctionDef) -> None:
        self.current_scope.pop()

    def visit_ClassDef(self, node: cst.ClassDef) -> None:
        pos = self.get_metadata(PositionProvider, node)
        qname = f"{self.module_name}.{node.name.value}"

        bases = [b.value.attr.value if isinstance(b.value, cst.Attribute) else b.value.value for b in node.bases]
        class_node = ClassNode(
            name=node.name.value,
            body=cst.Module([]).code_for_node(node.body),
            code=cst.Module([]).code_for_node(node),
            line_number_start=pos.start.line,
            line_number_end=pos.end.line,
            file_path=self.file_path,
            qualified_name=qname,
            base_classes=bases,
        )

        self.classes.append(class_node)
        self.edges.append(Edge(source=self.module_name, target=qname, kind="defines"))

        for base in bases:
            self.edges.append(Edge(source=qname, target=base, kind="inherits"))

        self.current_scope.append(qname)

    def leave_ClassDef(self, node: cst.ClassDef) -> None:
        self.current_scope.pop()

    def visit_Call(self, node: cst.Call) -> None:
        func_name = self._get_callable_name(node.func)
        qualified = self._get_qualified_name_from_call(node)
        if not self._is_internal(qualified):
            return
        if func_name and self.current_scope:
            logger.info(f"Got Call {node}")
            logger.info(f"Appending Edge(source={self.current_scope[-1]}, target={qualified}, kind='calls')")
            self.calls.append(Edge(source=self.current_scope[-1], target=qualified, kind="calls"))

    def visit_Import(self, node: cst.Import) -> None:
        for alias in node.names:
            name = alias.name.value
            qualified = f"{self.module_name}.{name}"
            if not self._is_internal_import(qualified):
                return
            imported = ImportNode(
                name=name,
                origin=name,
                file_path=self.file_path,
                qualified_name=qualified,
            )
            if not self._is_internal_import(imported.origin):
                return
            self.imports.append(imported)
            self.edges.append(Edge(source=self.module_name, target=name, kind="imports"))

    def visit_ImportFrom(self, node: cst.ImportFrom) -> None:
        if node.module is None:
            return

        origin = self.get_origin(node.module)
        if isinstance(node.names, cst.ImportStar):
            self.edges.append(Edge(source=self.module_name, target=origin + ".*", kind="imports"))
            return

        for name in node.names:
            if isinstance(name, cst.ImportAlias):
                qualified = f"{origin}.{name.name.value}"
                if not self._is_internal(qualified):
                    return
                imported = ImportNode(
                    name=name.name.value,
                    origin=origin,
                    file_path=self.file_path,
                    qualified_name=qualified,
                    alias=(name.asname.name.value if name.asname else "")
                )
                self.imports.append(imported)
                self.edges.append(Edge(
                    source=self.module_name,
                    target=imported.qualified_name,
                    kind="imports"
                ))

    def _is_internal(self, qualified_name: str) -> bool:
        module_name = self._get_module_name()
        return qualified_name == module_name or qualified_name.startswith(module_name + ".")

    def _get_callable_name(self, expr: cst.BaseExpression) -> ty.Optional[str]:
        if isinstance(expr, cst.Name):
            return expr.value
        elif isinstance(expr, cst.Attribute):
            return expr.attr.value
        return None

    def get_origin(self, module: cst.BaseExpression) -> str:
        if isinstance(module, cst.Name):
            return module.value
        elif isinstance(module, cst.Attribute):
            return f"{self.get_origin(module.value)}.{module.attr.value}"
        return ""

    def finalize(self):
        # Optionally aggregate everything into one exportable structure
        all_nodes = (
            self.functions + self.classes + self.imports +
            [ModuleNode(name=self.module_name, file_path=self.file_path, qualified_name=self._get_module_name())]
        )
        all_edges = self.edges + self.calls
        return all_nodes, all_edges
