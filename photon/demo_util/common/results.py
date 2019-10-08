import traceback
from threading import Thread

from photon.common.tuuid_common import TUUIDCommon
from photon.demo_util.common.messages import ResultNT
from photon.demo_util.common.context_base import ContextBase


class ResultsDemo(Thread):
    """
    Handle ResultNT messages from Workers.

    """

    def __init__(self, ctx: ContextBase) -> None:
        """
        Args:
            ctx: The Context object.
        """
        super().__init__(daemon=True)  # terminate together w main thread
        self._logger = ctx._logger
        self._logger.info("Results")
        self._util_cmd = ctx.util_cmd
        self._resultq = ctx.resultq
        self._tuuid = TUUIDCommon(ctx)
        self._failfast_ev = ctx.failfast_ev
        self._startfast_br = ctx.startfast_br

    def _log_finish_event(self, resultnt: ResultNT) -> None:
        nowdt = self._tuuid.get_tza_utcdt()
        finishtd = nowdt - resultnt.startdt

        message = (
            f"{self._util_cmd} finish:: tuuid: {resultnt.tuuid}; "
            f"finishtd: {finishtd}; destdirp: {resultnt.destdirp}; "
            f"worker: {resultnt.worker}"
        )

        updated = {
            "event_type": "detail",
            "event": "finish",
            "util_cmd": self._util_cmd,
            "finishtd": finishtd,
            "message": message,
        }

        msgd = resultnt._asdict()
        msgd.update(updated)
        self._logger.info(msgd)

    def run(self) -> None:
        """
        Run in a background thread.

        """
        self._startfast_br.wait()  # blocks until all threads are ready
        self._logger.info("Results running")

        try:
            while True:
                resultnt = self._resultq.get()  # blocks

                if isinstance(resultnt, ResultNT):
                    self._log_finish_event(resultnt)
                else:  # shouldn't happen
                    self._logger.error("Invalid resultq object")
                    self._failfast_ev.set()
        except Exception as e:
            t = traceback.format_exc()
            msg = f"results thread failed: {e}\n{t}"
            self._logger.error(msg)
            self._failfast_ev.set()
