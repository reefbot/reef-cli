import pathlib
import click

from reef_cli.llm_client import get_llm, refactor


def load_file(path: pathlib.Path) -> str:
    try:
        with open(path, "r") as file:
            return file.read()
    except:
        raise FileNotFoundError(f"File not found {path}")


def reef(file_path: pathlib.Path) -> None:
    code = load_file(file_path)

    llm = get_llm()

    result = refactor(code, llm)

    print(result)


@click.command("reef")
@click.version_option("0.0.1", prog_name="reef")
@click.argument("file_path")
def reef_cli(file_path) -> None:
    reef(file_path=file_path)

if __name__ == "__main__":
    reef_cli()
