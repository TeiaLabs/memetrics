from pathlib import Path

import setuptools


def read_multiline_as_list(file_path: Path | str) -> list[str]:
    with open(file_path) as fh:
        contents = fh.read().split("\n")
        if contents[-1] == "":
            contents.pop()
        return contents


with open("README.md", "r") as f:
    long_description = f.read()

# requirements = read_multiline_as_list("requirements.txt")

setuptools.setup(
    name="memetrics_sdk",
    setuptools_git_versioning={
        "enabled": True,
        "tag_formatter": lambda t: t.replace("v", ""),
        "dev_template": "{tag}.dev",
        "dirty_template": "{tag}.dev"
    },
    setup_requires=["setuptools-git-versioning<2", "wheel"],
    author="TeiaLabs",
    author_email="contato@teialabs.com",
    description="Python client to save events to MongoDB.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TeiaLabs/memetrics",
    packages=setuptools.find_packages(),
    python_requires=">=3.11",
    install_requires=["fastapi", "pydantic", "python-dotenv", "httpx"],
)
