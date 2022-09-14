from PySide2.QtCore import QRunnable, Signal, QObject, Slot
import traceback, sys

a = False


class WorkerSignals(QObject):
    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)
    progress = Signal(object, object)


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
        except:
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
