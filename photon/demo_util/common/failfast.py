import sys

from photon.demo_util.common.context_base import ContextBase


class FailFastDemo:
    """
    Main thread waiting on the 'Fail Fast' event from any other thread.

    All other threads are 'daemons' and will exit when this thread exits.

    """

    def __init__(self, ctx: ContextBase) -> None:
        """
        Args:
            ctx: The Context object.
        """
        self._logger = ctx._logger
        self._logger.info("FailFast")
        self._failfast_ev = ctx.failfast_ev
        self._startfast_br = ctx.startfast_br

    def run(self) -> None:
        """
        Run in the main thread.

        """
        try:
            self._startfast_br.wait()  # blocks until all threads are ready
            self._logger.info("FailFast running")
            self._failfast_ev.wait()  # blocks until set by any thread
            self._logger.critical("Exiting on a Fail Fast Event")
        except KeyboardInterrupt:
            self._logger.info("Exiting on KeyboardInterrupt")
        finally:
            sys.exit(1)
