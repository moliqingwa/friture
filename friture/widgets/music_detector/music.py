#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets

from friture.logger import PrintLogger


class Music_Widget(QtWidgets.QWidget):
    def __init__(self, parent, logger=PrintLogger()):
        super().__init__(parent)

        self.audiobuffer = None
        self.logger = logger

        self.setObjectName("Music_Widget")
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        # self.gridLayout.addWidget(self.PlotZoneUp, 0, 0, 1, 1)

        self.settings_dialog = Music_Settings_Dialog(self, self.logger)

    # method
    def set_buffer(self, buffer):
        self.audiobuffer = buffer

    def handle_new_data(self, floatdata):
        pass

    # method
    def canvasUpdate(self):
        return

    def pause(self):
        pass

    def restart(self):
        pass

    # slot
    def settings_called(self, checked):
        self.settings_dialog.show()

    # method
    def saveState(self, settings):
        self.settings_dialog.saveState(settings)

    # method
    def restoreState(self, settings):
        self.settings_dialog.restoreState(settings)


class Music_Settings_Dialog(QtWidgets.QDialog):
    def __init__(self, parent, logger):
        super().__init__(parent)

        self.logger = logger

        self.setWindowTitle("Music settings")

        self.formLayout = QtWidgets.QFormLayout(self)

        self.setLayout(self.formLayout)

    # method
    def saveState(self, settings):
        pass

    # method
    def restoreState(self, settings):
        pass
