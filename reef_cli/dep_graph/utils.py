import os
import pathlib


def get_all_files(root_dir: pathlib.Path, ext: str) -> list[pathlib.Path]:
    all_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(ext):
                all_files.append(pathlib.Path(root, file))

    return all_files
