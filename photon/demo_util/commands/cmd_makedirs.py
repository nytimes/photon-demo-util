import logging
from pathlib import Path
from collections import namedtuple

import click

from photon.demo_util.util import pass_context
from photon.demo_util.common.context_base import ContextBase


def _doit(ctx: ContextBase) -> None:
    ctx.INCOMING_DIRP.mkdir(parents=True, exist_ok=True)
    ctx.MODIFIED_DIRP.mkdir(parents=True, exist_ok=True)
    ctx.ORIGINAL_DIRP.mkdir(parents=True, exist_ok=True)
    ctx.REJECTED_DIRP.mkdir(parents=True, exist_ok=True)


@click.command("createbuckets", short_help="Create the application I/O directories.")
@click.option(
    "-e",
    "--execute",
    is_flag=True,
    default=False,
    help="Execute the commands (default False)",
)
@pass_context
def cli(ctx: ContextBase, execute: bool) -> None:
    """
    Create the application I/O directories.

    """
    logname = Path(__file__).stem
    ctx.util_cmd = logname.replace("cmd_", "")
    application = f"{ctx.PACKAGE_NAME}.{logname}"
    ctx._logger = logging.getLogger(application)

    ctx._logger.info(f"Options:\nexecute: {execute}")

    CmdCtx = namedtuple("CmdCtx", "execute")
    cmdctx = CmdCtx(execute)

    for k, v in cmdctx._asdict().items():  # push cmdctx into ctx
        setattr(ctx, k, v)

    if ctx.execute:
        _doit(ctx)
    else:
        ctx._logger.info(f"{ctx.util_cmd}: Not executed")
