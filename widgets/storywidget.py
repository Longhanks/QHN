# PyQt5Template. Created on 21.04.2015
# Copyright (c) 2015 Andreas Schulz
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
import time

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl

from widgets.clickablelabel import ClickableLabel
from utilities import getResourcesPath


class StoryWidget(QWidget):
    def __init__(self, HNItem, parent=None):
        super(QWidget, self).__init__(parent)
        uic.loadUi(os.path.join(getResourcesPath(), 'ui', 'storywidget.ui'),
                   self)
        self.labelPosition.setText('%2d. ' % HNItem['pos'])
        self.labelPosition.setStyleSheet(
            'QLabel { font-size : 12pt; color: gray}')
        self.labelTitle.setText('%s ' % HNItem['title'])
        self.labelTitle.setStyleSheet('QLabel { font-size : 12pt; }')
        self.labelURL.url = HNItem['url']
        self.labelURL.setStyleSheet(ClickableLabel.DEFAULT_CSS)
        self.labelURL.setNormalText()
        self.labelURL.clicked.connect(self.openURL)
        if HNItem['type'] == 'job':
            self.labelSubtitle.setText(format_time(HNItem['time']))
        else:
            self.labelSubtitle.setText('%d points by %s %s | %s' %
                                       (HNItem['score'],
                                        HNItem['by'],
                                        format_time(HNItem['time']),
                                        format_comments(
                                            HNItem['descendants'])))
        self.labelSubtitle.setStyleSheet(
            'QLabel { font-size : 9pt; color: gray }')

    def openURL(self):
        QDesktopServices.openUrl(QUrl(self.sender().url))


def format_time(seconds):
    m, s = divmod(int(time.time()) - seconds, 60)
    h, m = divmod(m, 60)
    if h > 0:
        if h == 1:
            return '%d hour ago' % h
        return '%d hours ago' % h
    else:
        if m == 1:
            return '%d minute ago' % m
        return '%d minutes ago' % m


def format_comments(comment_count):
    if comment_count == 1:
        return '%d comment' % comment_count
    return '%d comments' % comment_count