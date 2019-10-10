import time
from threading import Thread

from photon.demo_util.common.context_base import ContextBase


class TimerDemo(Thread):
    """
    Sleep, log a success msg, then log periodic health checks.

    NOTE: we use the health check logs as an alert metric for our applications.
    If the health check log hasn't been seen in a given amount of time, an alert
    will fire.

    """

    def __init__(self, ctx: ContextBase) -> None:
        """
        Args:
            ctx: The Context object.
        """
        super().__init__(daemon=True)
        self._logger = ctx._logger
        self._logger.info("Timer")
        self._sleep_time = ctx.timeout * 1.5
        self._failfast_ev = ctx.failfast_ev
        self._startfast_br = ctx.startfast_br

    def run(self) -> None:
        """
        Run the thread.

        """
        self._startfast_br.wait()  # blocks until all threads are ready
        self._logger.info("Timer running")

        try:
            time.sleep(self._sleep_time)
            msg = f"Successfully (re)started (up {self._sleep_time} secs)"
            self._logger.info(msg)

            while True:
                self._logger.info("health check: up")
                time.sleep(60)
        except Exception as e:
            msg = f"timer thread failed: {e}"
            self._logger.error(msg)
            self._failfast_ev.set()
