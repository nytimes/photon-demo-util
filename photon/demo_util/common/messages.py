from pathlib import Path
from typing import NamedTuple, List
from datetime import datetime, timedelta

from time_uuid import TimeUUID


class WorkNT(NamedTuple):
    """
    Work info sent from Incoming to Worker.

    """

    tuuid: TimeUUID
    filep: Path
    valid: bool

    startdt: datetime
    queuedtd: timedelta


WorkNT.tuuid.__doc__ = "TimeUUID (field 0): Unique ID for each unit of work."
WorkNT.filep.__doc__ = "Path (field 1): Filepath."
WorkNT.valid.__doc__ = "bool (field 2): File valid T/F."

WorkNT.startdt.__doc__ = "datetime (field 3): Start dt for this file."
WorkNT.queuedtd.__doc__ = "timedelta (field 4): Queued dt for this file."


class ResultNT(NamedTuple):
    """
    Result info sent from Worker to Results.

    """

    tuuid: TimeUUID
    filep: Path
    valid: bool

    startdt: datetime
    queuedtd: timedelta

    worker: int
    beginworktd: timedelta
    endworktd: timedelta
    destdirp: Path
    transforms: List[str]


ResultNT.tuuid.__doc__ = "TimeUUID (field 0): Unique ID for each unit of work."
ResultNT.filep.__doc__ = "Path (field 1): Filepath."
ResultNT.valid.__doc__ = "bool (field 2): File valid T/F."

ResultNT.startdt.__doc__ = "datetime (field 3): Start dt for this file."
ResultNT.queuedtd.__doc__ = "timedelta (field 4): Queued dt for this file."

ResultNT.worker.__doc__ = "int (field 5): Worker index number."
ResultNT.beginworktd.__doc__ = "timedelta (field 6): Timedelta for this file."
ResultNT.endworktd.__doc__ = "timedelta (field 7): Timedelta for this file."
ResultNT.destdirp.__doc__ = "Path (field 8): Destination directory path for this file."
ResultNT.transforms.__doc__ = "List (field 9): List of completed file transforms."
