import logging
import pathlib
import typing as ty

from pprint import pformat
import libcst as cst
from libcst.metadata import MetadataWrapper

from reef_cli.candidates.candidate import CandidateNode
from reef_cli.dependencies.dependency import DependencyNode
from .extractor import Extractor
from .utils import get_all_files

logger = logging.getLogger(__name__)


def scan_file(
    file_path: pathlib.Path, project_root: pathlib.Path
) -> tuple[list[CandidateNode], list[DependencyNode]]:
    visitor = Extractor(file_path=file_path, project_root=project_root)
    with open(file_path, "rb") as f:
        syntax_tree = MetadataWrapper(cst.parse_module(f.read()))
        syntax_tree.visit(visitor)

    candidates = [*visitor.classes, *visitor.functions]
    imports = visitor.imports

    logger.debug(f"Found {len(candidates)} candidates and {len(imports)} imports")

    if len(candidates) > 0:
        logger.debug(
            f"Candidates:\n {'\n\n'.join([pformat(cd.__str__()) for cd in candidates])}\n\n"
        )
    if len(imports) > 0:
        logger.debug(
            f"Imports:\n {'\n\n'.join([pformat(cd.__str__()) for cd in imports])}"
        )

    return candidates, imports


def scan_project(
    project_root: pathlib.Path,
) -> tuple[list[CandidateNode], list[DependencyNode]]:
    cands = []
    imports = []
    for file in get_all_files(root_dir=project_root, ext=".py"):
        logger.info(f"Scanning {file}")
        file_cands, file_imports = scan_file(file_path=file, project_root=project_root)
        cands.extend(file_cands)
        imports.extend(file_imports)

    return cands, imports