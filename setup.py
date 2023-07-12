from __future__ import annotations

import shlex
import subprocess
from pathlib import Path

import setuptools


def read_multiline_as_list(file_path: Path | str) -> list[str]:
    with open(file_path) as fh:
        contents = fh.read().split("\n")
        if contents[-1] == "":
            contents.pop()
        return contents


def get_version() -> str:
    raw_git_cmd = "git describe --tags --abbrev=0"
    git_cmd = shlex.split(raw_git_cmd)
    git = subprocess.Popen(git_cmd, stdout=subprocess.PIPE)
    ret_code = git.wait()
    assert ret_code == 0, f"{raw_git_cmd!r} failed with exit code {ret_code}."
    assert git.stdout is not None
    return git.stdout.read().decode().strip()


with open("README.md", "r") as fh:
    long_description = fh.read()

requirements = read_multiline_as_list("requirements.txt")

setuptools.setup(
    name="memetrics",
    version=get_version(),
    author="TeiaLabs",
    author_email="contato@teialabs.com",
    description="Python client to save events to MongoDB.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TeiaLabs/memetrics",
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.11",
    install_requires=requirements,
)
