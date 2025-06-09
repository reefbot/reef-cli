import pathlib

import libcst as cst
from libcst.metadata import ParentNodeProvider, PositionProvider

import typing as ty

from .nodes import ImportNode, FuncNode, ClassNode

CSTImportNode: type = ty.Union[cst.Import, cst.ImportFrom]


class NodeExtractor(cst.CSTVisitor):
    METADATA_DEPENDENCIES = (ParentNodeProvider, PositionProvider)

    def __init__(self, file_path: pathlib.Path, project_root: pathlib.Path) -> None:
        self.file_path = file_path
        self.project_root = project_root
        self.imports: list[ImportNode] = []
        self.functions: list[FuncNode] = []
        self.classes: list[ClassNode] = []

    def _get_module_name(self):
        rel_path = pathlib.Path(self.file_path).relative_to(self.project_root)
        parts = rel_path.with_suffix("").parts
        return ".".join(parts)

    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:
        parent = self.get_metadata(ParentNodeProvider, node)

        if not isinstance(parent, cst.ClassDef):
            position = self.get_metadata(PositionProvider, node)
            self.functions.append(
                self.extract_function_node(node=node, position=position)
            )

    def visit_ClassDef(self, node: cst.ClassDef) -> None:
        position = self.get_metadata(PositionProvider, node)
        self.classes.append(self.extract_class_node(node=node, position=position))

    def visit_Import(self, node: cst.Import) -> None:
        self.imports.append(
            ImportNode(
                name=node.names[0].name.value,
                origin=node.names[0].name.value,
                file_path=self.file_path,
                qualified_name=str(node.names[0].name.value),
            )
        )

    def visit_ImportFrom(self, node: cst.ImportFrom) -> None:
        self.imports.extend(
            [import_node for import_node in self.extract_importfrom_node(node)]
        )

    def extract_function_node(
        self, node: cst.FunctionDef, position: PositionProvider
    ) -> FuncNode:
        return FuncNode(
            name=node.name.value,
            params=cst.Module([]).code_for_node(node.params),
            body=cst.Module([]).code_for_node(node.body),
            code=cst.Module([]).code_for_node(node),
            line_number_start=position.start.line,
            line_number_end=position.end.line,
            file_path=self.file_path,
            qualified_name=".".join([self._get_module_name(), node.name.value]),
        )

    def extract_class_node(
        self, node: cst.ClassDef, position: PositionProvider
    ) -> ClassNode:
        return ClassNode(
            name=node.name.value,
            body=cst.Module([]).code_for_node(node.body),
            code=cst.Module([]).code_for_node(node),
            line_number_start=position.start.line,
            line_number_end=position.end.line,
            file_path=self.file_path,
            qualified_name=".".join([self._get_module_name(), node.name.value]),
        )

    def _get_import_qualified_name(self, cst_node: CSTImportNode, import_idx: int = 0) -> str:

        dot_count = len(cst_node.relative) if hasattr(cst_node, "relative") else 0

        cur_module = self._get_module_name()

        if dot_count > 1:
            directed_module = ".".join(cur_module.split(".")[: dot_count * -1])
            if directed_module is not "":
                return ".".join(
                    [
                        directed_module,
                        self.get_origin(cst_node.module),
                        cst_node.names[0].name.value,
                    ]
                )
            return ".".join(
                [self.get_origin(cst_node.module), cst_node.names[import_idx].name.value]
            )

        return".".join([self.get_origin(cst_node.module), cst_node.names[import_idx].name.value])

    def extract_importfrom_node(
        self, cst_node: CSTImportNode
    ) -> ty.Iterator[ImportNode]:
        """Extract ImportNode objects from a CST import node."""

        origin = self.get_origin(cst_node.module)

        if isinstance(cst_node.names, cst.ImportStar):
            yield ImportNode(name="*", origin=origin, file_path=self.file_path, qualified_name=origin + ".*")
            return

        for i, name in enumerate(cst_node.names):
            name_value = str(name.name.value)
            qualified_name = self._get_import_qualified_name(cst_node, import_idx=i)

            if (
                isinstance(name, cst.ImportAlias)
                and getattr(name, "asname") is not None
            ):
                yield ImportNode(
                    name=name_value,
                    origin=origin,
                    file_path=self.file_path,
                    qualified_name=qualified_name,
                    alias=name.asname.name.value,
                )

            else:
                yield ImportNode(
                    name=name_value,
                    origin=origin,
                    file_path=self.file_path,
                    qualified_name=qualified_name,
                )

        return

    def get_origin(self, module: ty.Union[cst.Module, cst.Name, str]) -> str:
        """Extract the origin string from a CST module node."""
        if not hasattr(module, "value"):
            return ""

        # Base case: if value is a string, return it
        if isinstance(module.value, str):
            return module.value

        # Recurse into node.value
        base = self.get_origin(module.value)

        # Append current attribute if it exists
        if hasattr(module, "attr"):
            return f"{base}.{module.attr.value}"

        return base
