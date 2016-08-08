'''
Created on 2016-08-18
@author: Sun Tianchen
'''
import pyqtgraph as pg
from pyqtgraph import debug
from PyQt4 import QtCore, QtGui

class PathPlotItem(pg.GraphicsObject):

	def __init__(self):
		pg.GraphicsObject.__init__(self)
		self.is_moving = False
		self.cur_track = [pg.Point(1,2), pg.Point(10,10), pg.Point(12,31)]
		self.temp_track = [] #contain Point()s

	def add_draw_point(self, pt):
		if self.is_moving == False:
			self.is_moving == True
			self.temp_track.append(pt)
		else:
			self.temp_track.append(pt)

	def track_completed(self):
		if self.is_moving == False:
			return
		## process track
		self.is_moving = False
		self.temp_track = []

	def is_closed(self):
		pass

	@debug.warnOnException  ## raising an exception here causes crash
	def paint(self, p, *args):
		## draw temp
		p1 = QtGui.QPainterPath()
		p1.moveTo(0, 0)
		for item in self.temp_track:
			p1.lineTo(item.x(), item.y())
		p.drawPath(p1)


