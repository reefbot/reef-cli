import logging
import pathlib
import random
import click

from dep_graph.nodes import ClassNode, FuncNode, ImportNode
from reef_cli.llm_client import get_llm, refactor

from reef_cli import __version__ as version
from reef_cli.dep_graph.scan import scan_project

logging.basicConfig(level=logging.DEBUG)

handler = logging.StreamHandler()
formatter = logging.Formatter('[%(levelname)s] %(message)s')
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(handler)


def select_candidate(candidates):
    return random.choice(candidates)


def get_dependencies(
    candidate, imports
) -> list[ImportNode]:

    dependencies = []
    for imp in imports:

        # special treatment for * imports
        # match the base of qualified name
        if imp.qualified_name[-1] == "*":
            if ".".join(imp.qualified_name.split(".")[-1]) == ".".join(candidate.qualified_name.split(".")[-1]):
                dependencies.append(imp)

        if imp.qualified_name == candidate.qualified_name:
            dependencies.append(imp)

    return dependencies


def reef(directory: pathlib.Path, log_level: str) -> None:
    logger.setLevel(log_level)

    candidates, imports = scan_project(directory)

    candidate = select_candidate(candidates)
    print("\n\nCandidate:")
    print(candidate)

    deps = get_dependencies(candidate, imports)
    print("\n\nDeps:")
    print(deps)

    #llm = get_llm()

    #result = refactor(str(candidates[0]), llm)

    #print(result)


@click.command("reef")
@click.version_option(version, prog_name="reef")
@click.argument("directory", nargs=1, type=pathlib.Path)
@click.option("--log-level", nargs=1, default=logging.INFO, type=str, help="Set the logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL).")
def reef_cli(directory, log_level) -> None:
    reef(directory=directory, log_level=log_level)


if __name__ == "__main__":
    reef_cli()
