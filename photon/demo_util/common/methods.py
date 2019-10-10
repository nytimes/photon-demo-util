from queue import Queue
from threading import Barrier, Event

from photon.demo_util.common.timer import TimerDemo
from photon.demo_util.common.worker import WorkerDemo
from photon.demo_util.common.results import ResultsDemo
from photon.demo_util.common.failfast import FailFastDemo
from photon.demo_util.common.incoming import IncomingDemo
from photon.demo_util.common.context_base import ContextBase


def failfast(ctx: ContextBase) -> None:
    """
    Fail Fast if any other thread fails.

    Args:
        ctx: The Context object.
    """

    FailFastDemo(ctx).run()


def handle_results(ctx: ContextBase) -> None:
    """
    Handle the results of processing.

    Args:
        ctx: The Context object.
    """

    ResultsDemo(ctx).start()


def start_timer(ctx: ContextBase) -> None:
    """
    Create a timer thread to log on (re)start and log health checks.

    Args:
        ctx: The Context object.
    """

    TimerDemo(ctx).start()


def start_incoming(ctx: ContextBase) -> None:
    """
    Launch a background thread to periodically handle incoming files.

    Args:
        ctx: The Context object.
    """

    IncomingDemo(ctx).start()


def start_workers(ctx: ContextBase) -> None:
    """
    Start worker threads.

    Args:
        ctx: The Context object.
    """

    for worker in range(ctx.worker_count):
        WorkerDemo(ctx, worker).start()  # instantiate and start()


def update_ctx(ctx: ContextBase) -> None:
    """
    Init shared data structures.

    Args:
        ctx: The Context object.
    """

    # thread count for startfast:
    #     Number of Workers + Incoming + Timer + Results + FailFast
    ctx.startfast_br = Barrier(ctx.worker_count + 1 + 1 + 1 + 1, timeout=60)
    ctx.failfast_ev = Event()

    ctx.workq = Queue()
    ctx.resultq = Queue()

    # ensure existence of I/O directories
    ctx.INCOMING_DIRP.mkdir(parents=True, exist_ok=True)
    ctx.MODIFIED_DIRP.mkdir(parents=True, exist_ok=True)
    ctx.ORIGINAL_DIRP.mkdir(parents=True, exist_ok=True)
    ctx.REJECTED_DIRP.mkdir(parents=True, exist_ok=True)
