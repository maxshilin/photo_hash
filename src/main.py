import multiprocessing
import sys
from typing import Optional

from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import QRunnable, QThreadPool, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QMessageBox, QWidget

from image_processor import ImageProcessor
from models import ImageProcessorResult
from ui_form import Ui_PhotoHash
from worker_signals import WorkerSignals


class Worker(QRunnable):
    def __init__(self, fn, *args, use_signals=False, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        if use_signals:
            kwargs["signals"] = self.signals

    @QtCore.Slot()
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
        except Exception as e:
            print(e)
            self.signals.error.emit((e,))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()


class Window(QWidget, Ui_PhotoHash):
    def __init__(self):
        super(Window, self).__init__()

        self.setupUi(self)
        self.pushButton_1.clicked.connect(self.button_1_clicked)
        self.pushButton_2.clicked.connect(self.button_2_clicked)
        self.pushButton_3.clicked.connect(self.button_3_clicked)
        self.pushButton_4.clicked.connect(self.button_4_clicked)
        self.pushButton_5.clicked.connect(self.button_5_clicked)
        self.pushButton_6.clicked.connect(self.button_6_clicked)
        self.threadpool = QThreadPool()
        self.path: Optional[str] = None
        self.copies = {}
        self.image_processor: Optional[ImageProcessor] = None

    def progress_fn(self, k, t):
        if k == 0:
            self.label_2.setText("processing started")
        elif k < 100:
            self.progressBar.setValue(int(k))
            ETA = int(t / k * (100 - k))
            PRO = int(t)
            self.label_2.setText(
                f"ETA:  {PRO // 60}:{PRO % 60} \\ {ETA // 60}:{ETA % 60}  seconds"
            )
            self.label_2.adjustSize()
        elif k == 100:
            self.progressBar.setValue(100)
            self.label_2.setText("finishing up...")
            self.label_2.adjustSize()

    def print_output(self, out: ImageProcessorResult):
        self.progressBar.setValue(100)
        self.label_2.setText("")
        self.label_2.adjustSize()
        self.copies = out.hash_dict
        QMessageBox.information(
            self,
            "Information",
            f"Done for {out.elapsed_seconds} seconds. Found {out.num_copies} copies.",
        )

        if out.source_dir == self.path:
            self.label_1.setText(f"{self.path}      Photos found: {out.num_photos}")
            self.label_1.adjustSize()
        self.pushButton_2.setEnabled(True)
        self.pushButton_3.setEnabled(True)
        self.pushButton_4.setEnabled(False)
        self.pushButton_6.setEnabled(True)

    def thread_complete(self, num_photos):
        self.pushButton_3.setEnabled(True)
        self.pushButton_6.setEnabled(True)
        QMessageBox.information(self, "Information", "Done!")
        self.label_1.setText(f"{self.path}      Photos found: {num_photos}")
        self.label_1.adjustSize()

    def num_files(self, num_photos):
        self.label_1.setText(f"{self.path}      Photos found: {num_photos}")
        self.label_1.adjustSize()

    def button_1_clicked(self):
        fileName = QtWidgets.QFileDialog.getExistingDirectory(self, "OpenFile")
        if fileName != "" and fileName != self.path:
            self.path = fileName
            self.label_1.setText(f"{self.path}      Looking for photos...")
            self.label_1.adjustSize()
            self.copies = {}
            self.image_processor = ImageProcessor(self.path)

            self.pushButton_2.setEnabled(True)
            self.pushButton_3.setEnabled(True)
            self.pushButton_5.setEnabled(True)
            self.pushButton_6.setEnabled(True)

            num_worker = Worker(self.image_processor.dir_open)
            num_worker.signals.result.connect(self.num_files)
            self.threadpool.start(num_worker)

    def button_2_clicked(self):
        self.progressBar.setValue(0)
        self.label_2.setText("processing started")
        self.label_2.adjustSize()
        self.copies = {}

        work = Worker(
            self.image_processor.find_similar_images,
            self.comboBox.currentIndex(),
            self.comboBox_2.currentIndex(),
            use_signals=True,
        )
        work.signals.result.connect(self.print_output)
        work.signals.progress.connect(self.progress_fn)

        self.pushButton_4.setEnabled(True)
        self.pushButton_2.setEnabled(False)
        self.pushButton_3.setEnabled(False)
        self.pushButton_6.setEnabled(False)

        self.threadpool.start(work)

    def button_3_clicked(self):
        self.pushButton_3.setEnabled(False)
        self.pushButton_6.setEnabled(False)
        self.label_1.setText("processing started")
        self.label_1.adjustSize()
        uncopy_worker = Worker(self.image_processor.uncopy)
        uncopy_worker.signals.result.connect(self.thread_complete)
        self.copies = {}

        self.threadpool.start(uncopy_worker)

    def button_4_clicked(self):
        self.work.stop()

    def button_5_clicked(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(self.path))

    def button_6_clicked(self):
        qm = QMessageBox
        ret = qm.question(
            self,
            "Delete copies",
            "Are you sure you want to delete the copies automatically? It is"
            " recommended to delete manually.",
            qm.Yes | qm.No,
        )

        if ret == qm.Yes:
            self.pushButton_3.setEnabled(False)
            self.pushButton_6.setEnabled(False)
            self.label_1.setText("processing started")
            self.label_1.adjustSize()
            delete_worker = Worker(self.image_processor.delete, self.copies)
            delete_worker.signals.result.connect(self.thread_complete)
            self.copies = {}
            self.threadpool.start(delete_worker)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QtWidgets.QApplication(sys.argv)
    widget = Window()
    widget.show()
    sys.exit(app.exec())
