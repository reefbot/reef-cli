import pathlib
from dataclasses import dataclass


@dataclass
class DependencyNode:
    name: str
    origin: str
    file_path: pathlib.Path
    qualified_name: str
    alias: str = ""
