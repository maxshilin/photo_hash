import time

from PySide6.QtCore import QObject, Signal


class WorkerSignals(QObject):
    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)
    progress = Signal(object, object)

    def __init__(self) -> None:
        super().__init__()
        self.started = time.time()

    def emit_progress(self, num: int, total: int) -> None:
        self.progress.emit(
            100 * num // total,
            round(time.time() - self.started, 3),
        )
