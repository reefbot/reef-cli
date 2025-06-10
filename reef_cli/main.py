import logging
import pathlib
import random
import click

from reef_cli import __version__ as version
from reef_cli.extraction.scan import scan_project
from reef_cli.candidates.manager import CandidateManager
from reef_cli.dependencies.linker import get_linked_dependencies

logging.basicConfig(level=logging.DEBUG)

handler = logging.StreamHandler()
formatter = logging.Formatter('[%(levelname)s] %(message)s')
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(handler)


def select_candidate(candidates):
    return random.choice(candidates)


def reef(directory: pathlib.Path, log_level: str) -> None:
    logger.setLevel(log_level)

    candidates, imports = scan_project(directory)

    candidate_manager = CandidateManager.from_nothing(candidates)
    candidate = candidate_manager.filter().score().normalise().sample_one()

    print("\n\nCand:")
    print(candidate)


    deps = get_linked_dependencies(candidate, imports)
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
