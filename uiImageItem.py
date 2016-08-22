'''
Created on 2016-07-12
@author: Sun Tianchen
'''

import pyqtgraph as pg
from pyqtgraph import ImageItem
from PyQt4 import QtCore, QtGui
import numpy as np
import collections

class UiImageItem(ImageItem):
	"""subclass of ImageItem for holding input image"""
	
	sigAddVertexRequested = QtCore.Signal(object)
	sigLoadImageRequested = QtCore.Signal(object)

	def __init__(self, image=None):
		ImageItem.__init__(self, image)
		self.draw_kernel = None
		self.draw_kernel_center = None
		self.draw_mode = None
		self.draw_mask = None

	def set_draw_kernel(self, kernel=None, mask=None, center=(0,0), mode='set', size=5):
		## reimplement draw method to be called by parent object
		print "shape: ", self.image.shape
		if kernel == None:
			## decide kernel based on the shape of the array
			## some problem with the color displayed; need to modify
			if len(self.image.shape) == 2:
				## gray
				kernel = mask = np.ones([size,size]) * 0.5
			elif self.image.shape[2] == 3:
				## RGB image
				kernel = mask = np.ones([size,size,3]) * [100,100,100]
			elif self.image.shape[2] == 4:
				## RGBa image
				kernel = mask = np.ones([size,size,4]) * [100,100,100,255]
		self.draw_kernel = kernel
		self.draw_kernel_center = center
		self.draw_mode = mode
		self.draw_mask = mask

	def set_draw_pen(self, color, size):
		## may replcace the set_draw_kernel method with a more explicit para list
		## not considering gray scale image
		## color.rgb() returns argb as a int
		argb = color.rgb()
		a = int(argb >> 24)
		r = int(argb >> 16 & 255)
		g = int(argb >> 8 & 255)
		b = int(argb & 255)
		if self.image.shape[2] == 3:
			## RGB image
			kernel = mask = np.ones([size,size,3]) * [r, g, b]
		elif self.image.shape[2] == 4:
			## RGBa image
			kernel = mask = np.ones([size,size,4]) * [r, g, b, a]
		self.draw_kernel = kernel
		self.draw_kernel_center = (0, 0)
		self.draw_mode = 'set'
		self.draw_mask = mask

	def draw_at(self, pos, ev=None):
		pos = [int(pos.x()), int(pos.y())]
		dk = self.draw_kernel
		kc = self.draw_kernel_center
		sx = [0,dk.shape[0]]
		sy = [0,dk.shape[1]]
		tx = [pos[0] - kc[0], pos[0] - kc[0]+ dk.shape[0]]
		ty = [pos[1] - kc[1], pos[1] - kc[1]+ dk.shape[1]]
		
		for i in [0,1]:
			dx1 = -min(0, tx[i])
			dx2 = min(0, self.image.shape[0]-tx[i])
			tx[i] += dx1+dx2
			sx[i] += dx1+dx2

			dy1 = -min(0, ty[i])
			dy2 = min(0, self.image.shape[1]-ty[i])
			ty[i] += dy1+dy2
			sy[i] += dy1+dy2

		ts = (slice(tx[0],tx[1]), slice(ty[0],ty[1]))
		ss = (slice(sx[0],sx[1]), slice(sy[0],sy[1]))
		mask = self.draw_mask
		src = dk
		
		if isinstance(self.draw_mode, collections.Callable):
			self.draw_mode(dk, self.image, mask, ss, ts, ev)
		else:
			src = src[ss]
			if self.draw_mode == 'set':
				if mask is not None:
					mask = mask[ss]
					## make drawing with only one color
					self.image[ts] = self.draw_kernel
				else:
					self.image[ts] = src
			elif self.draw_mode == 'add':
				self.image[ts] += src
			else:
				raise Exception("Unknown draw mode '%s'" % self.draw_mode)
			self.updateImage()

	'''
	def draw_at(self, pos, ev=None):
		pos = [int(pos.x()), int(pos.y())]
		dk = self.draw_kernel
		kc = self.draw_kernel_center
		sx = [0,dk.shape[0]]
		sy = [0,dk.shape[1]]
		tx = [pos[0] - kc[0], pos[0] - kc[0]+ dk.shape[0]]
		ty = [pos[1] - kc[1], pos[1] - kc[1]+ dk.shape[1]]
		
		for i in [0,1]:
			dx1 = -min(0, tx[i])
			dx2 = min(0, self.image.shape[0]-tx[i])
			tx[i] += dx1+dx2
			sx[i] += dx1+dx2

			dy1 = -min(0, ty[i])
			dy2 = min(0, self.image.shape[1]-ty[i])
			ty[i] += dy1+dy2
			sy[i] += dy1+dy2

		ts = (slice(tx[0],tx[1]), slice(ty[0],ty[1]))
		ss = (slice(sx[0],sx[1]), slice(sy[0],sy[1]))
		mask = self.draw_mask
		src = dk
		
		if isinstance(self.draw_mode, collections.Callable):
			self.draw_mode(dk, self.image, mask, ss, ts, ev)
		else:
			src = src[ss]
			if self.draw_mode == 'set':
				if mask is not None:
					mask = mask[ss]
					self.image[ts] = self.image[ts] * (1-mask) + src * mask
				else:
					self.image[ts] = src
			elif self.draw_mode == 'add':
				self.image[ts] += src
			else:
				raise Exception("Unknown draw mode '%s'" % self.draw_mode)
			self.updateImage()
	'''

	'''
	def mouseDragEvent(self, ev):
		if ev.button() != QtCore.Qt.LeftButton:
			ev.ignore()
			print "UiImageItem ignore"
			return
		#elif self.drawKernel is not None:
			#pass
			#ev.accept()
			#ev.ignore()
			#print "UiImageItem ignore"
			#self.drawAt(ev.pos(), ev)
	'''

	'''
	def mouseClickEvent(self, ev):
		if ev.button() == QtCore.Qt.LeftButton:
			print "left click ui image"
			print ev.pos()
			ev.accept()
			self.sigAddVertexRequested.emit((self, ev.pos()))
		ImageItem.mouseClickEvent(self, ev)
	
	def load_imgae_clicked(self, item):
		self.sigLoadImageRequested.emit(self)
	'''