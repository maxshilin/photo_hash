import sys
import traceback

from PySide6.QtCore import QRunnable, Slot

from hashing import WorkerSignals

a = False


class Worker(QRunnable):
    def __init__(self, fn, arg):
        super(Worker, self).__init__()
        self.fn = fn
        self.arg = arg
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        global a
        a = False
        try:
            result = self.fn(self.arg, self.signals)
        except Exception:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()

    def stop(self):
        global a
        a = True
