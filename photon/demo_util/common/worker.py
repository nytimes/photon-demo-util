import traceback
from threading import Thread, Timer

from photon.common.tuuid_common import TUUIDCommon
from photon.demo_util.common.context_base import ContextBase
from photon.demo_util.common.messages import WorkNT, ResultNT


class WorkerDemo(Thread):
    """
    Transform image and report results.

    """

    def __init__(self, ctx: ContextBase, worker: int) -> None:
        """
        Args:
            ctx: The Context object.
            worker: The worker index.
        """
        super().__init__(daemon=True)  # worker terminates if parent does
        self._logger = ctx._logger
        self._logger.info(f"worker: {worker}")
        self._worker = worker
        self._workq = ctx.workq
        self._resultq = ctx.resultq
        self._tuuid = TUUIDCommon(ctx)
        self._timeout = ctx.timeout
        self._outgoing_dirp = ctx.OUTGOING_DIRP
        self._reject_dirp = ctx.REJECT_DIRP
        self._failfast_ev = ctx.failfast_ev
        self._startfast_br = ctx.startfast_br

    def _process_work(self, worknt: WorkNT) -> None:
        beginworktd = self._tuuid.get_tza_utcdt() - worknt.startdt
        filep = worknt.filep

        if filep.exists():
            if worknt.valid:
                destdirp = self._outgoing_dirp
                # TODO: transformations
            else:
                destdirp = self._reject_dirp

            new_name = destdirp / filep.name
            filep.rename(new_name)  # move to destdirp
        else:
            msg = (
                "filepath does not currently exist; "
                f"worker: {self._worker}; worknt: {worknt}"
            )

            self._logger.warning(msg)

        updated = {
            "worker": self._worker,
            "beginworktd": beginworktd,
            "endworktd": self._tuuid.get_tza_utcdt() - worknt.startdt,
            "destdirp": destdirp,
        }

        resultd = worknt._asdict()
        resultd.update(updated)
        resultnt = ResultNT(**resultd)
        self._resultq.put(resultnt)

    def _kill_switch(self, worknt: WorkNT) -> None:
        msg = f"worker hit {self._timeout} sec timeout processing worknt: {worknt}"
        self._logger.error(msg)
        self._failfast_ev.set()

    def run(self) -> None:
        """
        Start the thread.

        """
        self._startfast_br.wait()  # blocks until all threads are ready
        self._logger.info(f"Worker: {self._worker} running")

        try:
            while True:
                worknt = None  # make sure it is defined for use in except
                worknt = self._workq.get()  # blocks
                ks = Timer(self._timeout, self._kill_switch, args=[worknt])
                ks.start()
                self._process_work(worknt)
                ks.cancel()
        except Exception as e:
            t = traceback.format_exc()
            msg = f"worker run failed: {e}\nworknt: {worknt}\n{t}"
            self._logger.error(msg)
            self._failfast_ev.set()
