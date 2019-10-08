import logging
from pathlib import Path
from typing import cast, Any, List
from importlib import import_module

import click

from photon.demo_util import config
from photon.common.logging_common import LoggingCommon
from photon.demo_util.common.context_base import ContextBase

ROOTP = Path.cwd()
DEPLOYP = Path(__file__).parent
CMD_DIR_PATH = DEPLOYP / "commands"
CONTEXT_SETTINGS = {"auto_envvar_prefix": "UTIL"}
_logging_common = LoggingCommon(cast(ContextBase, config))
_root_logger = _logging_common.get_root_logger()
_root_logger.debug("")
_logger = logging.getLogger(f"{config.PACKAGE_NAME}")
_logger.debug("")


class Context(object):
    """
    Set up utility-wide constants and methods.

    """

    def __init__(self) -> None:
        """
        Initialize the Context.

        """
        _logger.debug("")

        for k, v in vars(config).items():  # propagate config into ctx
            if k.isupper() and not k.startswith("_"):
                setattr(self, k, v)

        self.ROOTP = ROOTP
        self.DEPLOYP = DEPLOYP


# decorator imported by each command
pass_context = click.make_pass_decorator(Context, ensure=True)


class DemoUtil(click.MultiCommand):
    """
    Support dynamic cmd listing, selection and importation.

    """

    def list_commands(self, ctx: Any) -> List[str]:
        """
        List commands.

        Args:
            ctx: The Context.

        Returns:
            The command list.
        """
        _logger.debug("")

        cmds_all = [
            path.stem.replace("cmd_", "") for path in CMD_DIR_PATH.glob("cmd_*.py")
        ]

        return sorted(cmds_all)

    def get_command(self, ctx: Any, cmd: str) -> Any:
        """
        Get a command.

        Args:
            ctx: The Context.
            cmd: The cmd.

        Returns:
            The imported cmd cli().

        Raises:
            ImportError if the cmd cannot be imported.
        """
        _logger.debug("")

        try:
            cmd_module = import_module(f"photon.demo_util.commands.cmd_{cmd}")
        except ImportError as e:
            print(f"ImportError: {e}")
            raise

        return cmd_module.cli  # type:ignore


@click.command(cls=DemoUtil, context_settings=CONTEXT_SETTINGS)
@pass_context
def cli(ctx: ContextBase) -> None:
    """
    The demo command line utility.

    """
    _logger.debug("")
    pass
