from queue import Queue
from typing import List
from pathlib import Path
from threading import Barrier, Event

from photon.demo_util.common.messages import WorkNT, ResultNT
from photon.common.config_context_common import ConfigContextCommon


class ContextBase(ConfigContextCommon):
    """
    Set up utility-wide Context type definitions.

    Assign a value in __init__() as a workaround for would-be generics
    that are in typeshed but not yet generic in stdlib. This approach
    works both at runtime and when doing strict type-checking with mypy.
    """

    failfast_ev: Event
    startfast_br: Barrier
    check_interval_secs: int
    worker_count: int
    timeout: int
    execute: bool

    DEMO_DIRP: Path
    INCOMING_DIRP: Path
    MODIFIED_DIRP: Path
    ORIGINAL_DIRP: Path
    REJECTED_DIRP: Path
    VALID_EXTENSIONS: List[str]

    def __init__(self) -> None:  # TODO: Fix when stdlib is updated
        """
        Init not-yet-fully-generic generics.

        """
        self.workq: Queue[WorkNT] = Queue()
        self.resultq: Queue[ResultNT] = Queue()
