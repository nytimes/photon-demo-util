from pathlib import Path
from setuptools import setup

from setup_common import get_requires, setup_base

DESCRIPTION = "Photon Demo Utilities"

PACKAGE_FULLNAME = "photon-demo-util"
PACKAGE_NAME = PACKAGE_FULLNAME.replace("photon-", "", 1).replace("-", "_")
PACKAGE_NICKNAME = PACKAGE_NAME.split("_")[0]

filep = Path(__file__)
versionp = filep.with_name("version.txt")
PACKAGE_VERSION = versionp.read_text().strip()

requirementsp = filep.with_name("requirements.txt")
REQUIRES = get_requires(requirementsp)

README = filep.with_name("README.rst").read_text()

setup(
    name=PACKAGE_FULLNAME,
    url=f"https://github.com/nytimes/{PACKAGE_FULLNAME}",
    version=PACKAGE_VERSION,
    description=DESCRIPTION,
    long_description=README,
    entry_points={
        "console_scripts": [f"{PACKAGE_NICKNAME}_util = photon.{PACKAGE_NAME}.util:cli"]
    },
    packages=[
        f"photon.{PACKAGE_NAME}",
        f"photon.{PACKAGE_NAME}.commands",
        f"photon.{PACKAGE_NAME}.common",
        f"photon.{PACKAGE_NAME}.plugins",
        f"photon.{PACKAGE_NAME}.plugins.transformations",
    ],
    package_data={
        f"photon.{PACKAGE_NAME}": ["py.typed"],
        f"photon.{PACKAGE_NAME}.commands": ["py.typed"],
        f"photon.{PACKAGE_NAME}.common": ["py.typed"],
        f"photon.{PACKAGE_NAME}.plugins": ["py.typed"],
        f"photon.{PACKAGE_NAME}.plugins.transformations": ["py.typed"],
    },
    install_requires=REQUIRES,
    **setup_base,
)
