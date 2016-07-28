'''
Created on 2016-07-11
@author: Sun Tianchen
'''

import pyqtgraph as pg
from pyqtgraph import ROI
from PyQt4 import QtCore, QtGui

class ImageROI(ROI):
	"""subclass of ROI for holding/processing image"""

	sigSendBackRequested = QtCore.Signal(object)

	def __init__(self, pos, size, centered=False, simple=False, sideScalers=False, **args):
		if simple:
			print "simple image roi"
			ROI.__init__(self, pos, size, removable=False, movable=False, **args)
			return
		ROI.__init__(self, pos, size, **args)
		if centered:
			center = [0.5, 0.5]
		else:
			center = [0, 0]
		self.addRotateHandle([1,0], [0.5,0.5])
		self.addRotateHandle([0,1], [0.5,0.5])
		self.get_menu()

	def contextMenuEnabled(self):
		return True

	def get_menu(self):
		if self.menu is None:
			self.menu = QtGui.QMenu()
			self.menu.setTitle("ImageROI")
			sbAct = QtGui.QAction("Send to Back", self.menu)
			sbAct.triggered.connect(self.send_back_clicked)
			self.menu.addAction(sbAct)
			return sbAct
			#self.memu.sbAct = sbAct
		
	def send_back_clicked(self):
		self.sigSendBackRequested.emit(self)

	def set_image(self, image_arr):
		for child in self.childItems():
			if isinstance(child, pg.graphicsItems.ImageItem.ImageItem):
				child.setParentItem(None)
		img = pg.ImageItem(image_arr)
		img.setParentItem(self)
