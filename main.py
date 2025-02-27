#!/usr/bin/env python
# -*- coding: utf-8 -*-

########################################################################
#                                                                      #
# This file is part of openPSTD.                                       #
#                                                                      #
# openPSTD is free software: you can redistribute it and/or modify     #
# it under the terms of the GNU General Public License as published by #
# the Free Software Foundation, either version 3 of the License, or    #
# (at your option) any later version.                                  #
#                                                                      #
# openPSTD is distributed in the hope that it will be useful,          #
# but WITHOUT ANY WARRANTY; without even the implied warranty of       #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the        #
# GNU General Public License for more details.                         #
#                                                                      #
# You should have received a copy of the GNU General Public License    #
# along with openPSTD.  If not, see <http://www.gnu.org/licenses/>.    #
#                                                                      #
########################################################################

__author__ = 'michiel'

import sys
import platform

import PySide
from PySide.QtGui import QApplication, QMainWindow, QMessageBox, QFileDialog

import model
from MainWindow_ui import Ui_MainWindow
import operations.BaseOperation
import operations.MenuFileOperations
import operations.SceneOperations
import operations.ViewOperations
import operations.MouseHandlerOperations
import MouseHandlers

__version__ = '0.0.1'


class MainWindow(QMainWindow, Ui_MainWindow, operations.BaseOperation.OperationRunner):
    # noinspection PyUnresolvedReferences
    def __init__(self, parent=None):
        self.m = model.Model()
        self.m.SceneDescChanged.append(self.updateViews)
        self.m.SimulationChanged.append(self.updateViews)

        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        self.actionShow_grid.setChecked(True)

        self.actionAbout.triggered.connect(self.about)
        self.actionNew.triggered.connect(self.createRunOperation(operations.MenuFileOperations.New))
        self.actionOpen.triggered.connect(self.OpenOperation)
        self.actionSave.triggered.connect(self.SaveOperation)
        self.actionClose.triggered.connect(self.createRunOperation(operations.MenuFileOperations.Close))
        self.actionView_complete_scene.triggered.connect(self.createRunOperation(operations.ViewOperations.ViewWholeScene))
        self.actionShow_grid.triggered.connect(self.ToggleGrid)

        self.btnSimulate.clicked.connect(self.simulate_operation)

        self.actionAdd_Domain.triggered.connect(self.createChangeMouseHandlerOperation(MouseHandlers.MouseCreateDomainStragegy, self.actionAdd_Domain))
        self.actionMove_scene.triggered.connect(self.createChangeMouseHandlerOperation(MouseHandlers.MouseMoveSceneStrategy, self.actionMove_scene))

        self.MouseHandlerActions = [self.actionAdd_Domain, self.actionMove_scene]

        self.createChangeMouseHandlerOperation(MouseHandlers.MouseMoveSceneStrategy, self.actionMove_scene)()

        self.actionDebug1.triggered.connect(self.createRunOperation(operations.DebugOperations.Debug1Action))
        self.actionDebug2.triggered.connect(self.createRunOperation(operations.DebugOperations.Debug2Action))
        self.actionDebug3.triggered.connect(self.createRunOperation(operations.DebugOperations.Debug3Action))
        self.actionDebug4.triggered.connect(self.createRunOperation(operations.DebugOperations.Debug4Action))

    def createRunOperation(self, operationClass):
        mw = self
        def RunOperation():
            operation = operationClass()
            mw.run_operation(operation)
        return RunOperation

    def createChangeMouseHandlerOperation(self, mouseHandlerClass, action):
        mw = self
        def RunOperation():
            [action2.setChecked(False) for action2 in filter((lambda a: not a == action), mw.MouseHandlerActions)]
            [action2.setChecked(True) for action2 in filter((lambda a: a == action), mw.MouseHandlerActions)]
            operation = operations.MouseHandlerOperations.ChangeMouseHandler(mouseHandlerClass())
            mw.run_operation(operation)
        return RunOperation

    def OpenOperation(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open file', '')
        if(fname != ''):
            operation = operations.MenuFileOperations.Open(fname)
            self.run_operation(operation)

    def SaveOperation(self):
        fname, _ = QFileDialog.getSaveFileName(self, 'Open file', '')
        if(fname != ''):
            operation = operations.MenuFileOperations.Save(fname)
            self.run_operation(operation)

    def ToggleGrid(self):
        operation = operations.ViewOperations.SetVisibilityLayer("Grid", self.actionShow_grid.isChecked())
        self.run_operation(operation)


    def run_operation(self, op):
        op.run(operations.BaseOperation.Receiver(self.m, self))

    def simulate_operation(self):
        operation = operations.SceneOperations.Simulate()
        s = self
        def status_changed():
            pass
        def status_text_changed():
            s.statusbar.showMessage(operation.statusText)
        operation.statusChanged.append(status_changed)
        operation.statusTextChanged.append(status_text_changed)
        operation.start(operations.BaseOperation.Receiver(self.m, self))

    def updateViews(self):
        frames = self.m.Simulation.get_sequence_frame_numbers()
        if(len(frames) > 0):
            self.m.visible_frame = frames[-1]
        self.mainView.update_scene(self.m)

    def about(self):
        '''Popup a box with about message.'''
        QMessageBox.about(self, "About PySide, Platform and the like",
                """<b>Platform Details</b> v %s
               <p>Copyright � 2010 Joe Bloggs.
               All rights reserved in accordance with
               GPL v2 or later - NO WARRANTIES!
               <p>This application can be used for
               displaying platform details.
               <p>Python %s -  PySide version %s - Qt version %s on %s""" % (__version__,
                platform.python_version(), PySide.__version__,  PySide.QtCore.__version__,
                platform.system()))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    frame = MainWindow()
    frame.show()
    app.exec_()