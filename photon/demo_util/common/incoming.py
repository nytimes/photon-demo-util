import time
import traceback
from pathlib import Path
from typing import Any, Dict
from threading import Thread, Timer

from photon.common.json_common import JSONCommon
from photon.common.tuuid_common import TUUIDCommon
from photon.demo_util.common.messages import WorkNT
from photon.demo_util.common.context_base import ContextBase


class IncomingDemo(Thread):
    """
    Poll a directory and queue files to worker bkgd threads.

    NOTE: we often use this Incoming model with pulling a Pub/Sub subscription
    asynchronously. The polling of a directory that you see here can be swapped
    out with other queue, stream, and pub/sub mechanisms.

    """

    def __init__(self, ctx: ContextBase) -> None:
        """
         Args:
             ctx: The Context object.
         """
        super().__init__(daemon=True)  # terminate together w main thread
        self._logger = ctx._logger
        self._logger.info("Incoming")
        self._workq = ctx.workq
        self._util_cmd = ctx.util_cmd
        self._timeout = ctx.timeout
        self._json = JSONCommon(ctx)
        self._tuuid = TUUIDCommon(ctx)
        self._check_interval_secs = ctx.check_interval_secs
        self._lastcheck_time = float(0)  # init to zero
        self._incoming_dirp = ctx.INCOMING_DIRP
        self._valid_extensions = ctx.VALID_EXTENSIONS
        self._failfast_ev = ctx.failfast_ev
        self._startfast_br = ctx.startfast_br

    def _log_event(self, blobd: Dict[str, Any], event: str) -> None:
        tuuid = blobd["tuuid"]
        filep = blobd["filep"]
        msgd = blobd.copy()

        update = {
            "event_type": "detail",
            "event": event,
            "util_cmd": self._util_cmd,
            "message": (f"{self._util_cmd} {event}:: tuuid: {tuuid}; filep: {filep}",),
        }

        msgd.update(update)
        self._logger.info(self._json.jsonsafe(msgd))

    def _submit_work(self, filepd: Dict[str, Any]) -> None:
        startdt = filepd["startdt"]
        filepd["queuedtd"] = self._tuuid.get_tza_utcdt() - startdt
        self._workq.put(WorkNT(**filepd))

    def _valid_filep(self, filep: Path) -> bool:
        msgs = []
        extension = filep.suffix.upper()
        size = filep.stat().st_size

        if extension not in self._valid_extensions:
            msgs.append(f"invalid extension: {extension}")

        if size == 0:
            msgs.append("zero-length file")

        if msgs:
            msg = "; ".join(msgs)
            msg += f"; filep: {filep}; "
            self._logger.warning(msg)
            return False

        return True

    def _process_filep(self, filep: Path) -> None:
        tuuid = self._tuuid.get_tuuid()
        valid = self._valid_filep(filep)
        startdt = self._tuuid.extract_datetime(tuuid)

        filepd = {"tuuid": tuuid, "filep": filep, "valid": valid, "startdt": startdt}

        self._submit_work(filepd)
        self._log_event(filepd, "start")

    def _check_incoming(self) -> None:
        for filep in self._incoming_dirp.iterdir():  # does not handle nested dirs
            if filep.stat().st_ctime > self._lastcheck_time:
                self._process_filep(filep)

        self._lastcheck_time = time.time()

    def _kill_switch(self) -> None:
        msg = f"incoming hit {self._timeout} sec timeout"
        self._logger.critical(msg)
        self._failfast_ev.set()

    def run(self) -> None:
        """
        Run the thread.

        Background thread of parent process.

        """
        self._startfast_br.wait()  # blocks until all threads are ready
        self._logger.info("Incoming running")

        try:
            while True:
                ks = Timer(self._timeout, self._kill_switch)
                ks.start()
                self._check_incoming()
                ks.cancel()
                time.sleep(self._check_interval_secs)
        except Exception as e:
            t = traceback.format_exc()
            msg = f"incoming thread failed: {e}\n{t}"
            self._logger.error(msg)
            self._failfast_ev.set()
