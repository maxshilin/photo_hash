# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Ui_PhotoHash(object):
    def setupUi(self, PhotoHash):
        if not PhotoHash.objectName():
            PhotoHash.setObjectName("PhotoHash")
        PhotoHash.resize(1280, 720)
        PhotoHash.setMouseTracking(True)
        PhotoHash.setAutoFillBackground(True)
        self.pushButton_1 = QPushButton(PhotoHash)
        self.pushButton_1.setObjectName("pushButton_1")
        self.pushButton_1.setGeometry(QRect(110, 130, 141, 61))
        self.pushButton_1.setMouseTracking(True)
        self.pushButton_2 = QPushButton(PhotoHash)
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.setEnabled(False)
        self.pushButton_2.setGeometry(QRect(110, 210, 141, 61))
        self.pushButton_2.setMouseTracking(True)
        self.progressBar = QProgressBar(PhotoHash)
        self.progressBar.setObjectName("progressBar")
        self.progressBar.setGeometry(QRect(110, 580, 591, 23))
        self.progressBar.setValue(0)
        self.pushButton_3 = QPushButton(PhotoHash)
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.setEnabled(False)
        self.pushButton_3.setGeometry(QRect(110, 300, 141, 51))
        self.pushButton_3.setMouseTracking(True)
        self.pushButton_4 = QPushButton(PhotoHash)
        self.pushButton_4.setObjectName("pushButton_4")
        self.pushButton_4.setEnabled(False)
        self.pushButton_4.setGeometry(QRect(110, 380, 141, 51))
        self.pushButton_4.setMouseTracking(True)
        self.label_1 = QLabel(PhotoHash)
        self.label_1.setObjectName("label_1")
        self.label_1.setGeometry(QRect(350, 140, 201, 16))
        self.label_2 = QLabel(PhotoHash)
        self.label_2.setObjectName("label_2")
        self.label_2.setGeometry(QRect(750, 580, 41, 21))
        self.pushButton_5 = QPushButton(PhotoHash)
        self.pushButton_5.setObjectName("pushButton_5")
        self.pushButton_5.setEnabled(False)
        self.pushButton_5.setGeometry(QRect(350, 380, 141, 51))
        self.comboBox = QComboBox(PhotoHash)
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.setObjectName("comboBox")
        self.comboBox.setGeometry(QRect(350, 220, 241, 41))
        self.comboBox.setMouseTracking(True)
        self.label = QLabel(PhotoHash)
        self.label.setObjectName("label")
        self.label.setGeometry(QRect(280, 230, 55, 16))
        self.pushButton_6 = QPushButton(PhotoHash)
        self.pushButton_6.setObjectName("pushButton_6")
        self.pushButton_6.setEnabled(False)
        self.pushButton_6.setGeometry(QRect(110, 460, 141, 51))
        self.pushButton_6.setMouseTracking(True)
        self.comboBox_2 = QComboBox(PhotoHash)
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.setObjectName("comboBox_2")
        self.comboBox_2.setGeometry(QRect(350, 300, 241, 41))

        self.retranslateUi(PhotoHash)

        QMetaObject.connectSlotsByName(PhotoHash)

    # setupUi

    def retranslateUi(self, PhotoHash):
        PhotoHash.setWindowTitle(
            QCoreApplication.translate("PhotoHash", "window", None)
        )
        self.pushButton_1.setText(
            QCoreApplication.translate("PhotoHash", "Open folder", None)
        )
        self.pushButton_2.setText(
            QCoreApplication.translate("PhotoHash", "Find copies", None)
        )
        self.pushButton_3.setText(
            QCoreApplication.translate("PhotoHash", "Uncopy", None)
        )
        self.pushButton_4.setText(
            QCoreApplication.translate("PhotoHash", "Stop searching", None)
        )
        self.label_1.setText(
            QCoreApplication.translate(
                "PhotoHash", "You haven't opened any folder yet", None
            )
        )
        self.label_2.setText("")
        self.pushButton_5.setText(
            QCoreApplication.translate("PhotoHash", "Open folder in explorer", None)
        )
        self.comboBox.setItemText(
            0,
            QCoreApplication.translate(
                "PhotoHash", "Perceptual hashing (recommended)", None
            ),
        )
        self.comboBox.setItemText(
            1,
            QCoreApplication.translate("PhotoHash", "Difference hashing", None),
        )
        self.comboBox.setItemText(
            2, QCoreApplication.translate("PhotoHash", "Average hashing", None)
        )
        self.comboBox.setItemText(
            3, QCoreApplication.translate("PhotoHash", "Wavelet hashing", None)
        )
        self.comboBox.setItemText(
            4,
            QCoreApplication.translate(
                "PhotoHash", "Color hashing (not recommended)", None
            ),
        )
        self.comboBox.setItemText(
            5,
            QCoreApplication.translate(
                "PhotoHash", "Crop-resistant (not recommended)", None
            ),
        )

        self.label.setText(QCoreApplication.translate("PhotoHash", "using:", None))
        self.pushButton_6.setText(
            QCoreApplication.translate("PhotoHash", "Delete copies", None)
        )
        self.comboBox_2.setItemText(
            0, QCoreApplication.translate("PhotoHash", "auto", None)
        )
        self.comboBox_2.setItemText(
            1, QCoreApplication.translate("PhotoHash", "1 thread", None)
        )
        self.comboBox_2.setItemText(
            2, QCoreApplication.translate("PhotoHash", "2 threads", None)
        )
        self.comboBox_2.setItemText(
            3, QCoreApplication.translate("PhotoHash", "4 threads", None)
        )
        self.comboBox_2.setItemText(
            4, QCoreApplication.translate("PhotoHash", "8 threads", None)
        )

    # retranslateUi
