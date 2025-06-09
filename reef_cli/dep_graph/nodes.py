import pathlib

from dataclasses import dataclass
import typing as ty


@dataclass
class ImportNode:
    name: str
    origin: str
    file_path: pathlib.Path
    qualified_name: str
    alias: str = ""


@dataclass
class CandidateNode:
    name: str
    params: str
    body: str
    code: str
    line_number_start: int
    line_number_end: int
    qualified_name: (
        str  # (where in the project it exists) i.e. src.module.module.definition + name
    )
    file_path: pathlib.Path  # directory of definition
    CANDIDATE_TYPE: ty.ClassVar[str]
    # parents: list["Node"]
    # children: list["Node"]


@dataclass
class FuncNode(CandidateNode):
    CANDIDATE_TYPE: ty.ClassVar[str] = "FUNC"


@dataclass
class ClassNode(CandidateNode):
    CANDIDATE_TYPE: ty.ClassVar[str] = "CLASS"