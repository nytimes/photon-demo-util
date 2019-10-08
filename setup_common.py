from typing import List
from pathlib import Path


def get_requires(requirementsp: Path) -> List[str]:
    """
    Transform a requirements file into a requires list for setup.

    Args:
        filep: Path to the requirements.txt file.

    Returns:
        A list of lines without comments or directives
        and with leading and trailing whitespace removed.
        Lines only containing whitespace after comments
        are removed are discarded as well.
    """
    if requirementsp.is_file():
        lines = requirementsp.read_text().split("\n")
        bare_lines = [l.split("#")[0].strip() for l in lines]

        return [
            require_line
            for require_line in bare_lines
            if require_line and not require_line.startswith("--")
        ]
    else:
        return []


setup_base = {
    "author": "NYTimes Photo Team",
    "zip_safe": False,
    "classifiers": [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.7",
        "Topic :: Internet",
    ],
}
