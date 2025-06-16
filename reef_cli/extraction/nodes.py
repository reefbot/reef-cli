import pathlib
from dataclasses import dataclass


@dataclass
class Node:
    name: str
    file_path: pathlib.Path
    qualified_name: str


@dataclass
class ImportEdge:
    origin: str
    name: str
    file_path: pathlib.Path
    qualified_name: str
    alias: str = ""


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
