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
import time
from urllib.parse import urlparse

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl

from utilities import getResourcesPath


class StoryWidget(QWidget):
    def __init__(self, HNItem, parent=None):
        super().__init__(parent)
        self.listWidget = self.parent()
        self.stackedWidget = self.listWidget.parent()
        self.mainWindow = self.stackedWidget.parent().parent()
        uic.loadUi(os.path.join(getResourcesPath(), 'ui', 'storywidget.ui'),
                   self)
        self.pos = HNItem['pos']
        self.kids = HNItem['kids'] if 'kids' in HNItem else []

        # format position
        self.labelPosition.setText('%2d. ' % self.pos)
        self.labelPosition.setStyleSheet(
            'QLabel { font-size : 12pt; color: gray}')

        # format title
        self.labelTitle.setText('%s ' % HNItem['title'])
        self.labelTitle.setStyleSheet('QLabel { font-size : 12pt; }')
        self.labelTitle.underlineTextOnHover = False
        self.labelTitle.clicked.connect(self.openURL)

        # format url
        try:
            # if story has a source url
            self.labelTitle.url = HNItem['url']

            # format url nicely (eg http://www.google.com/ -> google.com)
            netloc = urlparse(self.labelTitle.url).netloc
            if netloc.startswith('www.'):
                netloc = netloc[4:]
            self.labelURL.setText('(%s)' % netloc)
            self.labelURL.setStyleSheet(
                'QLabel { font-size: 11pt; color : gray; }')
        except KeyError as e:
            # story doesn't have a source url. Don't display labelURL.
            # story is a job.
            # TODO: infer URL of job...
            self.labelTitle.url = ""
            self.labelURL.setVisible(False)
            self.labelComments.setVisible(False)

        # format subtitle and comments (if existing)
        if HNItem['type'] == 'job':
            self.labelSubtitle.setText(format_time(HNItem['time']))
        else:
            self.labelSubtitle.setText('%d points by %s %s | ' %
                                       (HNItem['score'],
                                        HNItem['by'],
                                        format_time(HNItem['time'])))
            self.labelComments.commentCount = HNItem['descendants']
            self.labelComments.setNormalText()
        self.labelSubtitle.setStyleSheet(
            'QLabel { font-size : 9pt; color: gray }')
        self.labelComments.setStyleSheet(
            'QLabel { font-size : 9pt; color: gray }')
        self.labelComments.clicked.connect(self.openComments)

    def openURL(self, url):
        if url:
            QDesktopServices.openUrl(QUrl(url))

    def openComments(self):
        for kid in self.kids:
            item = self.mainWindow.hn.get('item/%r' % kid, name=None)
            if not 'deleted' in item:
                print(item)


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
