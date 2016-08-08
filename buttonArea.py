'''
Created on 2016-08-04
@author: Sun Tianchen
'''

from PyQt4 import QtCore, QtGui
import pyqtgraph as pg

class ButtonArea(pg.GraphicsWidget):
	def __init__(self, parent=None):
		pg.GraphicsWidget.__init__(self, parent)
		self.buttons = {}
		self.buttons['lock'] = pg.ButtonItem(pg.pixmaps.getPixmap('lock'), 14, self)
		self.buttons['lock'].setPos(0, 0)
		self.buttons['lock'].setOpacity(0.4)
		self.buttons['del'] = pg.ButtonItem(pg.pixmaps.getPixmap('default'), 14, self)
		self.buttons['del'].setPos(20, 0)

		
		