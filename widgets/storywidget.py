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
import threading
from urllib.parse import urlparse
from html import unescape

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QTreeView, QStyledItemDelegate, \
    QAbstractItemView
from PyQt5.QtGui import QDesktopServices, QStandardItemModel, QTextDocument, \
    QStandardItem
from PyQt5.QtCore import QUrl, Qt, QSize, pyqtSignal, QSortFilterProxyModel

from utilities import getResourcesPath


class StoryWidget(QWidget):
    fetchedComment = pyqtSignal(dict)

    def __init__(self, HNItem, parent=None):
        super().__init__(parent)
        self.listWidget = self.parent()
        self.stackedWidget = self.listWidget.parent()
        self.mainWindow = self.stackedWidget.parent().parent()
        uic.loadUi(os.path.join(getResourcesPath(), 'ui', 'storywidget.ui'),
                   self)
        self.pos = HNItem['pos']
        self.kids = HNItem['kids'] if 'kids' in HNItem else []
        self.commentsTree = CommentTree()
        self.commentsTree.setVerticalScrollMode(
            QAbstractItemView.ScrollPerPixel)
        self.commentsTree.setSelectionMode(QAbstractItemView.NoSelection)
        self.commentsTree.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.commentsTree.header().hide()
        self.fetchedComment.connect(self.addComment)

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
        self.mainWindow.toolBar.setVisible(True)
        if self.stackedWidget.indexOf(self.commentsTree) != -1:
            self.stackedWidget.setCurrentWidget(self.commentsTree)
            return
        self.stackedWidget.addWidget(self.commentsTree)
        self.maxCommentCount = len(self.kids)
        self.currentCommentCount = 0
        for tup in enumerate(self.kids):
            thd = threading.Thread(target=self.fetchComment, args=(tup,))
            thd.daemon = True
            thd.start()

    def fetchComment(self, tup):
        HTComment = self.mainWindow.hn.get('item/%r' % tup[1], name=None)
        HTComment['pos'] = tup[0]
        self.fetchedComment.emit(HTComment)

    def addComment(self, HNComment):
        self.currentCommentCount += 1
        if not 'deleted' in HNComment:
            authorItem = QStandardItem(
                '<style>#author { color: gray; font-size: 11pt; '
                'margin-bottom: 5px } </style><p id="author">' +
                HNComment['by'] + ' ' +
                format_time(HNComment['time']) + '</p>')
            authorItem.setData(HNComment['pos'], Qt.UserRole + 1337)
            textItem = QStandardItem(unescape(HNComment['text']))
            textItem.setData(HNComment['pos'], Qt.UserRole + 1337)
            authorItem.appendRow(textItem)
            self.commentsTree.rootItem.appendRow(authorItem)
        if self.currentCommentCount == self.maxCommentCount:
            self.commentsTree.sortByColumn(0, Qt.AscendingOrder)
            self.commentsTree.expandAll()
            self.stackedWidget.setCurrentWidget(self.commentsTree)


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


class CommentTree(QTreeView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setUniformRowHeights(False)
        self.setAnimated(True)
        self.model = QStandardItemModel()
        self.filter = CommentModel()
        self.filter.setSourceModel(self.model)
        self.setModel(self.filter)
        self.filter.setDynamicSortFilter(False)
        self.rootItem = self.model.invisibleRootItem()
        self.setWordWrap(True)
        self.setItemDelegate(ItemWordWrap())


class ItemWordWrap(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(self, painter, option, index):
        text = index.data()
        doc = QTextDocument()
        doc.setHtml(text)
        doc.setTextWidth(option.rect.width())
        painter.save()
        painter.translate(option.rect.x(), option.rect.y())
        doc.drawContents(painter)
        painter.restore()
        index.model().setData(index, option.rect.width(), Qt.UserRole + 1337)

    def sizeHint(self, option, index):
        text = index.model().data(index)
        doc = QTextDocument()
        doc.setHtml(text)
        width = index.model().data(index, Qt.UserRole + 1337)
        doc.setTextWidth(width)
        return QSize(doc.idealWidth(), doc.size().height())


class CommentModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)

    def lessThan(self, left, right):
        left = self.sourceModel().data(left, Qt.UserRole + 1337)
        right = self.sourceModel().data(right, Qt.UserRole + 1337)
        return left < right