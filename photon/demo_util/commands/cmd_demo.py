import sys
import logging
import pathlib
import traceback
from collections import namedtuple
from multiprocessing import cpu_count

import click

from photon.demo_util.util import pass_context
from photon.demo_util.common.context_base import ContextBase

from photon.demo_util.common.methods import (
    update_ctx,
    start_workers,
    start_incoming,
    start_timer,
    handle_results,
    failfast,
)

# defaults - config overrides defaults; commandline options override config
CHECK_INTERVAL_SECS: int = 5
CPU_FACTOR: int = 2
WORKER_COUNT: int = 0


@click.command("demo", short_help="Transform incoming images.")
@click.option(
    "--check-interval-secs",
    type=click.IntRange(3, 300),
    help=(
        "Interval in seconds between checks for new files "
        f"(default {CHECK_INTERVAL_SECS}, range 3-300)"
    ),
)
@click.option(
    "-c",
    "--cpu-factor",
    type=click.IntRange(0, 15),
    help=(
        "Set worker-count = `multiprocessing.cpu_count() * cpu-factor + 1` "
        f"(default {CPU_FACTOR}, range 0-15) "
        "(overridden by explicit worker-count)"
    ),
)
@click.option(
    "-w",
    "--worker-count",
    type=click.IntRange(0, 127),
    help=(
        "Number of workers - if non-zero overrides the use of "
        f'option "cpu-factor" above (default {WORKER_COUNT}, range 0-127)'
    ),
)
@click.option(
    "-t",
    "--timeout",
    type=click.IntRange(10, 600),
    default=60,
    help=("Worker timeout in seconds (default 60, range 10-600)"),
)
@click.option(
    "-e",
    "--execute",
    is_flag=True,
    default=False,
    help="Execute the commands (default False)",
)
@pass_context
def cli(
    ctx: ContextBase,
    check_interval_secs: int,
    cpu_factor: int,
    worker_count: int,
    timeout: int,
    execute: bool,
) -> None:
    """
    Transform incoming images.

    """
    logname = pathlib.Path(__file__).stem
    ctx.util_cmd = logname.replace("cmd_", "")
    application = f"{ctx.PACKAGE_NAME}.{logname}"
    ctx._logger = logging.getLogger(application)

    if not check_interval_secs:
        check_interval_secs = getattr(ctx, "CHECK_INTERVAL_SECS", CHECK_INTERVAL_SECS)

    if not cpu_factor:
        cpu_factor = getattr(ctx, "CPU_FACTOR", CPU_FACTOR)

    if not worker_count:
        worker_count = getattr(ctx, "WORKER_COUNT", WORKER_COUNT)

    # override cpu_factor calc w explicit worker_count
    worker_count = worker_count or cpu_count() * cpu_factor + 1

    ctx._logger.info(
        "Effective Options (commandline overrides config.py):"
        f"\n  check_interval_secs: {check_interval_secs}"
        f"\n  cpu_factor: {cpu_factor}"
        f"\n  worker_count: {worker_count}"
        f"\n  timeout: {timeout}"
        f"\n  execute: {execute}"
    )

    CmdCtx = namedtuple(
        "CmdCtx", "check_interval_secs cpu_factor worker_count timeout execute"
    )

    cmdctx = CmdCtx(
        check_interval_secs, cpu_factor, worker_count, timeout, execute
    )  # immutable

    for k, v in cmdctx._asdict().items():  # push cmdctx into ctx
        setattr(ctx, k, v)

    if cmdctx.execute:
        try:
            update_ctx(ctx)  # create shared data structures
            start_workers(ctx)  # bkgd threads: each blocks on the workq
            start_incoming(ctx)  # periodic bkgd thrd: block on time.sleep()
            start_timer(ctx)  # bkgd thread: block on timer
            handle_results(ctx)  # bkgd thread: block on resultq
            failfast(ctx)  # main thread
        except KeyboardInterrupt:
            pass
        except Exception as e:
            t = traceback.format_exc()
            ctx._logger.error(f"Exception: {e}\n{t}")
            sys.exit(1)
    else:
        ctx._logger.info(f"{ctx.util_cmd}: Not executed")
