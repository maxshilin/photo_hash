import multiprocessing
import sys

from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import QThreadPool, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QMessageBox, QWidget

import hashing
import worker
from ui_form import Ui_PhotoHash


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
        self.path = ""
        self.copies = {}

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

    def print_output(self, out):
        self.progressBar.setValue(100)
        self.label_2.setText("")
        self.label_2.adjustSize()
        self.copies = out[4]
        QMessageBox.information(
            self,
            "Information",
            "Done for "
            + "%s seconds " % out[0]
            + ". Found "
            + str(out[1])
            + " copies.",
        )

        if out[3] == self.path:
            self.label_1.setText(self.path + "      Photos found: " + str(out[2]))
            self.label_1.adjustSize()
        self.pushButton_2.setEnabled(True)
        self.pushButton_3.setEnabled(True)
        self.pushButton_4.setEnabled(False)
        self.pushButton_6.setEnabled(True)

    def thread_complete(self, Len):
        self.pushButton_3.setEnabled(True)
        self.pushButton_6.setEnabled(True)
        QMessageBox.information(self, "Information", "Done!")
        self.label_1.setText(self.path + "      Photos found: " + str(Len))
        self.label_1.adjustSize()

    def num_files(self, Len):
        self.label_1.setText(self.path + "      Photos found: " + str(Len))
        self.label_1.adjustSize()

    def button_1_clicked(self):
        fileName = QtWidgets.QFileDialog.getExistingDirectory(self, "OpenFile")
        if fileName != "" and fileName != self.path:
            self.path = fileName
            self.label_1.setText(self.path + "      Looking for photos...")
            self.label_1.adjustSize()
            self.copies = {}

            self.pushButton_2.setEnabled(True)
            self.pushButton_3.setEnabled(True)
            self.pushButton_5.setEnabled(True)
            self.pushButton_6.setEnabled(True)

            Num = worker.Worker(hashing.dir_open, self.path)
            Num.signals.result.connect(self.num_files)
            self.threadpool.start(Num)

    def button_2_clicked(self):
        self.progressBar.setValue(0)
        self.label_2.setText("processing started")
        self.label_2.adjustSize()
        self.copies = {}

        self.work = worker.Worker(
            hashing.find_simular_images,
            [
                self.path,
                self.comboBox.currentIndex(),
                self.comboBox_2.currentIndex(),
            ],
        )
        self.work.signals.result.connect(self.print_output)
        self.work.signals.progress.connect(self.progress_fn)

        self.pushButton_4.setEnabled(True)
        self.pushButton_2.setEnabled(False)
        self.pushButton_3.setEnabled(False)
        self.pushButton_6.setEnabled(False)

        self.threadpool.start(self.work)

    def button_3_clicked(self):
        self.pushButton_3.setEnabled(False)
        self.pushButton_6.setEnabled(False)
        self.label_1.setText("processing started")
        self.label_1.adjustSize()
        copy = worker.Worker(hashing.uncopy, self.path)
        copy.signals.result.connect(self.thread_complete)
        self.copies = {}

        self.threadpool.start(copy)

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
            delete = worker.Worker(hashing.delete, [self.path, self.copies])
            delete.signals.result.connect(self.thread_complete)
            self.copies = {}
            self.threadpool.start(delete)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QtWidgets.QApplication(sys.argv)
    widget = Window()
    widget.show()
    sys.exit(app.exec())
