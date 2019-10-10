import logging
from pathlib import Path

PACKAGE_NAME = "demo_util"
PACKAGE_FAMILY = "photon"
PACKAGE_HIERARCHY = f"{PACKAGE_FAMILY}/{PACKAGE_NAME}"
PACKAGE_NICKNAME, PACKAGE_TYPE = PACKAGE_NAME.split("_")
PACKAGE_FULLNAME = f"{PACKAGE_FAMILY}-{PACKAGE_NICKNAME}-{PACKAGE_TYPE}"

LOG_LEVEL = logging.INFO

LOG_FORMAT = (  # new style
    "{levelname:<10} {asctime:<23} {name:<30} {process:>5} "
    "{funcName:<30} {lineno:>5}: {message}"
)

DEMO_DIRP = Path("~/Desktop/demo").expanduser()
INCOMING_DIRP = DEMO_DIRP / "incoming"  # input images
MODIFIED_DIRP = DEMO_DIRP / "modified"  # modified images
ORIGINAL_DIRP = DEMO_DIRP / "original"  # original images
REJECTED_DIRP = DEMO_DIRP / "rejected"  # rejected original images (ex: png filetype)
VALID_EXTENSIONS = [".JPEG", ".JPG"]
