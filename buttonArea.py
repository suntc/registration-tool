'''
Created on 2016-08-04
@author: Sun Tianchen
'''

from PyQt4 import QtCore, QtGui
import pyqtgraph as pg

from colorWidget import ColorWidegt

class ButtonArea(pg.GraphicsWidget):
	def __init__(self, parent=None, mode='bar', curve=False):
		self.parent = parent
		pg.GraphicsWidget.__init__(self)
		self.buttons = {}
		
		if mode == 'bar':
			self.buttons['lock'] = pg.ButtonItem(pg.pixmaps.getPixmap('lock'), 14, self)
			self.buttons['lock'].setPos(0, 0)
			self.buttons['lock'].setOpacity(0.4)
			self.buttons['del'] = pg.ButtonItem(pg.pixmaps.getPixmap('del'), 14, self)
			self.buttons['del'].setPos(20, 0)
			self.buttons['del'].setOpacity(1)
			self.buttons['contour'] = pg.ButtonItem(pg.pixmaps.getPixmap('contour'), 14, self)
			self.buttons['lock'].setToolTip("lock aspect")
			self.buttons['del'].setToolTip("delete")
			self.buttons['contour'].setToolTip("select contour")
			if curve:
				self.buttons['curve'] = pg.ButtonItem(pg.pixmaps.getPixmap('curve'), 14, self)
				self.buttons['curve'].setPos(40, 0)
				self.buttons['curve'].setOpacity(0.4)
				self.buttons['color'] = pg.ButtonItem(pg.pixmaps.getPixmap('color'), 14, self)
				self.buttons['color'].setPos(60, 0)
				self.buttons['color'].setOpacity(0.4)
				self.buttons['contour'].setPos(80, 0)
				self.buttons['contour'].setOpacity(0.4)
				
				self.buttons['curve'].setToolTip("draw curve")
				self.buttons['color'].setToolTip("set draw pen")

				self.colorWidget = ColorWidegt(parent=self.parent)
				#self.colorWidget
				#self.buttons['color'].clicked.connect(self.color_clicked)
				self.colorWidget.buttons['cancel'].clicked.connect(self.cancel_clicked)
			else:
				self.buttons['contour'].setPos(40, 0)
		elif mode == 'panel':
			self.buttons['lock'] = pg.ButtonItem(pg.pixmaps.getPixmap('lock'), 16, self)
			self.buttons['lock'].setPos(0, 0)
			self.buttons['lock'].setOpacity(0.4)
			self.buttons['restore'] = pg.ButtonItem(pg.pixmaps.getPixmap('restore'), 16, self)
			self.buttons['restore'].setPos(22, 0)
			self.buttons['restore'].setOpacity(1)
			self.buttons['tri'] = pg.ButtonItem(pg.pixmaps.getPixmap('tri'), 16, self)
			self.buttons['tri'].setPos(44, 0)
			self.buttons['tri'].setOpacity(0.4)

			self.buttons['lock'].setToolTip("lock aspect")
			self.buttons['restore'].setToolTip("restore alignment")
			self.buttons['tri'].setToolTip("show triangulation (only for piecewise affine)")

			pass

	def color_clicked(self):
		self.colorWidget.show()

	def cancel_clicked(self):
		self.colorWidget.hide()