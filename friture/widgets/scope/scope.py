#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2009 Timoth?Lecomte

# This file is part of Friture.
#
# Friture is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as published by
# the Free Software Foundation.
#
# Friture is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Friture.  If not, see <http://www.gnu.org/licenses/>.

from PyQt5 import QtWidgets
from numpy import log10, sign, arange, zeros

from friture.audiobackend import SAMPLING_RATE
from friture.logger import PrintLogger
from friture.widgets.scope.timeplot import TimePlot

SMOOTH_DISPLAY_TIMER_PERIOD_MS = 25
DEFAULT_TIMERANGE = 2 * SMOOTH_DISPLAY_TIMER_PERIOD_MS
DEFAULT_DB_SCOPE = False
DEFAULT_Y_VALUE_MIN = -1.0
DEFAULT_Y_VALUE_MAX = 1.0


class Scope_Widget(QtWidgets.QWidget):

    def __init__(self, parent, logger=PrintLogger()):
        super().__init__(parent)

        self.audiobuffer = None
        self.logger = logger

        self.setObjectName("Scope_Widget")
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.PlotZoneUp = TimePlot(self, self.logger)
        self.PlotZoneUp.setObjectName("PlotZoneUp")
        self.gridLayout.addWidget(self.PlotZoneUp, 0, 0, 1, 1)

        self.settings_dialog = Scope_Settings_Dialog(self, self.logger)

        self.timerange = DEFAULT_TIMERANGE
        self.dBscope = DEFAULT_DB_SCOPE

        self.y_range_min = DEFAULT_Y_VALUE_MIN
        self.y_range_max = DEFAULT_Y_VALUE_MAX

        self.time = zeros(10)
        self.y = zeros(10)
        self.y2 = zeros(10)

    # method
    def set_buffer(self, buffer):
        self.audiobuffer = buffer

    def handle_new_data(self, floatdata):
        time = self.timerange * 1e-3
        width = int(time * SAMPLING_RATE)
        # basic trigger capability on leading edge
        floatdata = self.audiobuffer.data(2 * width)

        twoChannels = False
        if floatdata.shape[0] > 1:
            twoChannels = True

        datarange = width
        floatdata = floatdata[:, 0: datarange]

        self.y = floatdata[0, :]
        if twoChannels:
            self.y2 = floatdata[1, :]
        else:
            self.y2 = None

        if self.dBscope:
            epsilon = 1e-30
            dBmin = -50.
            self.y = sign(self.y) * (20 * log10(abs(self.y) + epsilon)).clip(dBmin, 0.) / (-dBmin) + sign(self.y) * 1.
            if twoChannels:
                self.y2 = sign(self.y2) * (20 * log10(abs(self.y2) + epsilon)).clip(dBmin, 0.) / (-dBmin) + sign(self.y2) * 1.
            else:
                self.y2 = None

        self.time = (arange(len(self.y)) - datarange / 2) / float(SAMPLING_RATE)

        if self.y2 is not None:
            self.PlotZoneUp.setdataTwoChannels(self.time*1e3, self.y, self.y2)
        else:
            self.PlotZoneUp.setdata(self.time*1e3, self.y)

    # method
    def canvasUpdate(self):
        return

    def pause(self):
        self.PlotZoneUp.pause()

    def restart(self):
        self.PlotZoneUp.restart()

    # slot
    def set_db_scope(self, value):
        self.dBscope = value != 0

    # slot
    def set_timerange(self, timerange):
        self.timerange = timerange

    # slot
    def set_y_range_min(self, ymin):
        self.y_range_min = ymin
        if self.y_range_max < ymin:
            self.y_range_max = ymin + 0.2
            self.settings_dialog.doubleSpinBox_yrange_max.setValue(self.y_range_max)

        self.PlotZoneUp.setverticalrange(self.y_range_min, self.y_range_max)
        self.PlotZoneUp.restart()

    # slot
    def set_y_range_max(self, ymax):
        self.y_range_max = ymax
        if self.y_range_min > ymax:
            self.y_range_min = ymax - 0.2
            self.settings_dialog.doubleSpinBox_yrange_min.setValue(self.y_range_min)

        self.PlotZoneUp.setverticalrange(self.y_range_min, self.y_range_max)
        self.PlotZoneUp.restart()

    # slot
    def settings_called(self, checked):
        self.settings_dialog.show()

    # method
    def saveState(self, settings):
        self.settings_dialog.saveState(settings)

    # method
    def restoreState(self, settings):
        self.settings_dialog.restoreState(settings)


class Scope_Settings_Dialog(QtWidgets.QDialog):

    def __init__(self, parent, logger):
        super().__init__(parent)

        self.logger = logger

        self.setWindowTitle("Scope settings")

        self.formLayout = QtWidgets.QFormLayout(self)

        self.checkBox_dB = QtWidgets.QCheckBox(self)
        self.checkBox_dB.setCheckable(True)
        self.checkBox_dB.setChecked(DEFAULT_DB_SCOPE)

        self.formLayout.addRow("dB scale:", self.checkBox_dB)

        self.doubleSpinBox_timerange = QtWidgets.QDoubleSpinBox(self)
        self.doubleSpinBox_timerange.setDecimals(1)
        self.doubleSpinBox_timerange.setMinimum(0.1)
        self.doubleSpinBox_timerange.setMaximum(1000.0)
        self.doubleSpinBox_timerange.setProperty("value", DEFAULT_TIMERANGE)
        self.doubleSpinBox_timerange.setObjectName("doubleSpinBox_timerange")
        self.doubleSpinBox_timerange.setSuffix(" ms")

        self.formLayout.addRow("Time range:", self.doubleSpinBox_timerange)

        self.doubleSpinBox_yrange_min = QtWidgets.QDoubleSpinBox(self)
        self.doubleSpinBox_yrange_min.setDecimals(1)
        self.doubleSpinBox_yrange_min.setSingleStep(0.1)
        self.doubleSpinBox_yrange_min.setMinimum(-1.0)
        self.doubleSpinBox_yrange_min.setMaximum(0.8)
        self.doubleSpinBox_yrange_min.setProperty("value", DEFAULT_Y_VALUE_MIN)
        self.doubleSpinBox_yrange_min.setObjectName("doubleSpinBox_yrange_min")
        # self.doubleSpinBox_yrange_min.setSuffix(" ms") # todo: ratio or dB ???

        self.formLayout.addRow("Y range min:", self.doubleSpinBox_yrange_min)

        self.doubleSpinBox_yrange_max = QtWidgets.QDoubleSpinBox(self)
        self.doubleSpinBox_yrange_max.setDecimals(1)
        self.doubleSpinBox_yrange_max.setSingleStep(0.1)
        self.doubleSpinBox_yrange_max.setMinimum(-0.8)
        self.doubleSpinBox_yrange_max.setMaximum(1.0)
        self.doubleSpinBox_yrange_max.setProperty("value", DEFAULT_Y_VALUE_MAX)
        self.doubleSpinBox_yrange_max.setObjectName("doubleSpinBox_yrange_max")
        self.doubleSpinBox_yrange_max.setValue(1.0)
        # self.doubleSpinBox_yrange_max.setSuffix(" ms") # todo: ratio or dB ???

        self.formLayout.addRow("Y range max:", self.doubleSpinBox_yrange_max)

        self.setLayout(self.formLayout)

        self.checkBox_dB.stateChanged.connect(self.parent().set_db_scope)
        self.doubleSpinBox_timerange.valueChanged.connect(self.parent().set_timerange)
        self.doubleSpinBox_yrange_min.valueChanged.connect(self.parent().set_y_range_min)
        self.doubleSpinBox_yrange_max.valueChanged.connect(self.parent().set_y_range_max)

    # method
    def saveState(self, settings):
        settings.setValue("timeRange", self.doubleSpinBox_timerange.value())
        settings.setValue("yValueMin", self.doubleSpinBox_yrange_min.value())
        settings.setValue("yValueMax", self.doubleSpinBox_yrange_max.value())

    # method
    def restoreState(self, settings):
        timeRange = settings.value("timeRange", DEFAULT_TIMERANGE, type=float)
        self.doubleSpinBox_timerange.setValue(timeRange)

        yValueMin = settings.value("yValueMin", DEFAULT_Y_VALUE_MIN, type=float)
        self.doubleSpinBox_yrange_min.setValue(yValueMin)

        yValueMax = settings.value("yValueMax", DEFAULT_Y_VALUE_MAX, type=float)
        self.doubleSpinBox_yrange_max.setValue(yValueMax)
