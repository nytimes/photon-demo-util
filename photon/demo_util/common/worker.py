import traceback
from typing import List
from pathlib import Path
from threading import Thread, Timer

from wand.image import Image

from photon.common.tuuid_common import TUUIDCommon
from photon.demo_util.common.context_base import ContextBase
from photon.demo_util.common.transforms import TransformsDemo
from photon.demo_util.common.messages import WorkNT, ResultNT


class WorkerDemo(Thread):
    """
    Transform image and queue work results.

    NOTE: the Worker is where the bulk of the I/O- or CPU-related work occurs.
    In this example, the worker is primarily transforming images, but tasks such
    as API calls or heavy computations would fit well here.

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
        self._transforms = TransformsDemo(ctx)
        self._timeout = ctx.timeout
        self._modified_dirp = ctx.MODIFIED_DIRP
        self._original_dirp = ctx.ORIGINAL_DIRP
        self._rejected_dirp = ctx.REJECTED_DIRP
        self._failfast_ev = ctx.failfast_ev
        self._startfast_br = ctx.startfast_br

    def _save_original(self, filep: Path) -> None:
        with Image(filename=str(filep)) as img:
            copyp = self._original_dirp / filep.name
            img.save(filename=str(copyp))

    def _process_work(self, worknt: WorkNT) -> None:
        beginworktd = self._tuuid.get_tza_utcdt() - worknt.startdt
        filep = worknt.filep
        transforms: List[str] = []

        if filep.exists():
            if worknt.valid:
                self._save_original(filep)
                transforms = self._transforms.run_transforms(str(filep))
                destdirp = self._modified_dirp
            else:
                destdirp = self._rejected_dirp

            new_name = destdirp / filep.name
            filep.rename(new_name)  # move to destination directory
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
            "transforms": transforms,
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
