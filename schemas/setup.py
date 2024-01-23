from pathlib import Path

import setuptools


def read_multiline_as_list(file_path: Path | str) -> list[str]:
    with open(file_path) as fh:
        contents = fh.read().split("\n")
        if contents[-1] == "":
            contents.pop()
        return contents


def get_optional_requirements() -> dict[str, list[str]]:
    """Get dict of suffix -> list of requirements."""
    name = lambda p: p.stem.split("-")[-1]

    requirements_files = Path(".").glob(r"requirements-*.txt")
    return {name(p): read_multiline_as_list(p) for p in requirements_files}


requirements = read_multiline_as_list("requirements.txt")
requirements_extras = get_optional_requirements()
requirements_extras["all"] = [
    req for extras in requirements_extras.values() for req in extras
]


setuptools.setup(
    name="memetrics_schemas",
    setuptools_git_versioning={
        "enabled": True,
        "tag_formatter": lambda t: t.replace("v", "").replace("p", ""),
        "dev_template": "{tag}.dev",
        "dirty_template": "{tag}.dev",
    },
    setup_requires=["setuptools-git-versioning<2"],
    author="TeiaLabs",
    author_email="contato@teialabs.com",
    description="Event schemas used by MeMetrics API and SDKs.",
    url="https://github.com/TeiaLabs/memetrics",
    packages=setuptools.find_packages(),
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require=requirements_extras,
)
