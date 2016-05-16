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


from urllib.parse import urlparse

from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import Qt


class ClickableLabel(QLabel):
    clicked = pyqtSignal(str)
    DEFAULT_CSS = 'QLabel { font-size: 11pt; color : gray; }'

    def __init__(self, parent=None):
        super(QLabel, self).__init__(parent)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.text())

    def enterEvent(self, QEvent):
        self.setUnderlinedText()

    def leaveEvent(self, QEvent):
        self.setNormalText()

    def setNormalText(self):
        netloc = urlparse(self.url).netloc
        if netloc.startswith('www.'):
            netloc = netloc[4:]
        self.setText('(%s)' % netloc)

    def setUnderlinedText(self):
        netloc = urlparse(self.url).netloc
        if netloc.startswith('www.'):
            netloc = netloc[4:]
        self.setText('(<u>%s</u>)' % netloc)
