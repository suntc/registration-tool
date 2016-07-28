'''
Created on 2016-07-12
@author: Sun Tianchen
'''

import pyqtgraph as pg
from pyqtgraph import ImageItem
from PyQt4 import QtCore, QtGui

class UiImageItem(ImageItem):
	"""subclass of ImageItem for holding input image"""
	
	sigAddVertexRequested = QtCore.Signal(object)
	sigLoadImageRequested = QtCore.Signal(object)

	def __init__(self, image=None):
		ImageItem.__init__(self, image)

	
	def mouseClickEvent(self, ev):
		if ev.button() == QtCore.Qt.LeftButton:
			print "left click ui image"
			print ev.pos()
			ev.accept()
			self.sigAddVertexRequested.emit((self, ev.pos()))
		ImageItem.mouseClickEvent(self, ev)
	

	def load_imgae_clicked(self, item):
		self.sigLoadImageRequested.emit(self)