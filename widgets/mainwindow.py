# QHN. Created on 16.05.2016
# Copyright (c) 2016 Andreas Schulz
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import os
import threading
from firebase import firebase

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal

from utilities import getResourcesPath
from widgets.storywidget import StoryWidget
from widgets.storylistitem import StoryListItem


class MainWindow(QMainWindow):
    fetchedItem = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(getResourcesPath(), 'ui', 'mainwindow.ui'),
                   self)
        self.backButton = QPushButton("<-")
        self.backButton.clicked.connect(self.backPressed)
        self.toolBar.addWidget(self.backButton)
        self.toolBar.setVisible(False)
        self.listWidget.setAttribute(Qt.WA_MacShowFocusRect, 0)

        # start HN Connection
        self.hn = firebase.FirebaseApplication(
            'https://hacker-news.firebaseio.com/v0/')
        topstory_items = self.hn.get('topstories', name=None)
        topstory_items = topstory_items[:30]
        self.fetchedItem.connect(self.addItem)

        for tup in enumerate(topstory_items):
            tup = tup[0] + 1, tup[1]
            thd = threading.Thread(target=self.fetchItem, args=(tup,))
            thd.daemon = True
            thd.start()

    def backPressed(self):
        self.stackedWidget.setCurrentIndex(0)
        self.toolBar.setVisible(False)

    def fetchItem(self, tup):
        HNItem = self.hn.get('item/%r' % tup[1], name=None)
        HNItem['pos'] = tup[0]
        self.fetchedItem.emit(HNItem)

    def addItem(self, HNItem):
        listitem = StoryListItem(HNItem['pos'])
        storyitem = StoryWidget(HNItem, parent=self.listWidget)
        listitem.setSizeHint(storyitem.sizeHint())
        self.listWidget.addItem(listitem)
        self.listWidget.setItemWidget(listitem, storyitem)
