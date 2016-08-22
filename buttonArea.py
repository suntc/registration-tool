'''
Created on 2016-08-04
@author: Sun Tianchen
'''

from PyQt4 import QtCore, QtGui
import pyqtgraph as pg

from colorWidget import ColorWidegt

class ButtonArea(pg.GraphicsWidget):
	def __init__(self, parent=None, curve=False):
		self.parent = parent
		pg.GraphicsWidget.__init__(self)
		self.buttons = {}
		self.buttons['lock'] = pg.ButtonItem(pg.pixmaps.getPixmap('lock'), 14, self)
		self.buttons['lock'].setPos(0, 0)
		self.buttons['lock'].setOpacity(0.4)
		self.buttons['del'] = pg.ButtonItem(pg.pixmaps.getPixmap('del'), 14, self)
		self.buttons['del'].setPos(20, 0)
		self.buttons['del'].setOpacity(1)
		if curve:
			self.buttons['curve'] = pg.ButtonItem(pg.pixmaps.getPixmap('curve'), 14, self)
			self.buttons['curve'].setPos(40, 0)
			self.buttons['curve'].setOpacity(0.4)
			self.buttons['color'] = pg.ButtonItem(pg.pixmaps.getPixmap('color'), 14, self)
			self.buttons['color'].setPos(60, 0)
			self.buttons['color'].setOpacity(1)
			self.colorWidget = ColorWidegt(parent=self.parent)
			#self.colorWidget
			self.buttons['color'].clicked.connect(self.color_clicked)
			self.colorWidget.buttons['cancel'].clicked.connect(self.cancel_clicked)

	def color_clicked(self):
		self.colorWidget.show()

	def cancel_clicked(self):
		self.colorWidget.hide()