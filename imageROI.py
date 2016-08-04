'''
Created on 2016-07-11
@author: Sun Tianchen
'''

import pyqtgraph as pg
from pyqtgraph import ROI
from PyQt4 import QtCore, QtGui
import cv2
import numpy as np

class ImageROI(ROI):
	"""subclass of ROI for holding/processing image"""

	sigSendBackRequested = QtCore.Signal(object)
	sigAddVertexRequested = QtCore.Signal(object)
	sigLoadImageRequested = QtCore.Signal(object)

	def __init__(self, pos, size, centered=False, simple=False, sideScalers=False, movable=True, rotatable=True, sendBack=True, alpha=False, **args):
		self.sendBack = sendBack
		self.image_array = None
		self.image_item = None
		if simple:
			print "simple image roi"
			ROI.__init__(self, pos, size, removable=False, movable=movable, **args)
			return
		ROI.__init__(self, pos, size, movable=movable, **args)
		if centered:
			center = [0.5, 0.5]
		else:
			center = [0, 0]
		if rotatable:
			self.addRotateHandle([1,0], [0.5,0.5])
			self.addRotateHandle([0,1], [0.5,0.5])
			self.addScaleHandle([1,1], [0.5,0.5])
			#self.addScaleRotateHandle([1,0], [1,0.5])
			#self.addScaleRotateHandle([0,1], [0,0.5])
		self.get_menu()
		if alpha:
			self.add_alpha_slider()

	def contextMenuEnabled(self):
		return True

	def get_menu(self):
		if self.menu is None:
			self.menu = QtGui.QMenu()
			self.menu.setTitle("ImageROI")
		if self.sendBack:
			sbAct = QtGui.QAction("Send to Back", self.menu)
			sbAct.triggered.connect(self.send_back_clicked)
			self.menu.addAction(sbAct)
			#self.memu.sbAct = sbAct
			return

	def add_alpha_slider(self):
		alpha = QtGui.QWidgetAction(self.menu)
		alphaSlider = QtGui.QSlider()
		alphaSlider.setOrientation(QtCore.Qt.Horizontal)
		alphaSlider.setMaximum(255)
		alphaSlider.setMinimum(40)
		alphaSlider.setValue(255/2)
		alphaSlider.valueChanged.connect(self.set_alpha)
		alpha.setDefaultWidget(alphaSlider)
		self.menu.addAction(alpha)
			

	def set_image(self, image_arr):
		for child in self.childItems():
			if isinstance(child, pg.graphicsItems.ImageItem.ImageItem):
				child.setParentItem(None)
		img = pg.ImageItem(image_arr)
		img.setParentItem(self)
		self.image_array = image_arr
		self.image_item = img
		self.setSize([image_arr.shape[0], image_arr.shape[1]])

	def set_alpha(self, alpha):
		self.image_item.setOpacity(alpha/255.)
		'''
		shape = self.image_array.shape
		#alpha_channel = np.ones((shape[0],shape[1])) * alpha
		if shape[2] == 3:
			r, g, b = cv2.split(self.image_array)
		elif shape[2] == 4:
			r, g, b, a = cv2.split(self.image_array)
		self.image_array = cv2.merge((r, g, b, r * 0 + alpha))
		self.set_image(self.image_array)
		'''


	def mouseClickEvent(self, ev):
		if ev.button() == QtCore.Qt.LeftButton:
			print "left click ui image"
			print ev.pos()
			ev.accept()
			self.sigAddVertexRequested.emit((self, ev.pos()))
		ROI.mouseClickEvent(self, ev)
	

	def load_imgae_clicked(self, item):
		self.sigLoadImageRequested.emit(self)

	def send_back_clicked(self):
		self.sigSendBackRequested.emit(self)

	def do_scale(self, x, y):
		for child in self.childItems():
			if isinstance(child, pg.graphicsItems.ImageItem.ImageItem):
				child.setParentItem(None)
		#print self.image_array.shape
		#img = pg.ImageItem(cv2.resize(self.image_array, dsize=(x, y)))
		#img.setParentItem(self)
		self.image_item.setImage(cv2.resize(self.image_array, dsize=(x, y)))
		self.image_item.setParentItem(self)

	def movePoint(self, handle, pos, modifiers=QtCore.Qt.KeyboardModifier(), finish=True, coords='parent'):
		## overload ROI.py's movePoint(), reload image after scaling
		## call ROI.movePoint() at the end
		#print "imageROI movePoint"
		newState = self.stateCopy()
		index = self.indexOfHandle(handle)
		h = self.handles[index]
		p0 = self.mapToParent(h['pos'] * self.state['size'])
		p1 = pg.Point(pos)

		if coords == 'parent':
			pass
		elif coords == 'scene':
			p1 = self.mapSceneToParent(p1)
		else:
			raise Exception("New point location must be given in either 'parent' or 'scene' coordinates.")

		if 'center' in h:
			c = h['center']
			cs = c * self.state['size']
			lp0 = self.mapFromParent(p0) - cs
			lp1 = self.mapFromParent(p1) - cs

		if h['type'] == 's':
			## If a handle and its center have the same x or y value, we can't scale across that axis.
			if h['center'][0] == h['pos'][0]:
				lp1[0] = 0
			if h['center'][1] == h['pos'][1]:
				lp1[1] = 0
			
			## snap 
			if self.scaleSnap or (modifiers & QtCore.Qt.ControlModifier):
				lp1[0] = round(lp1[0] / self.snapSize) * self.snapSize
				lp1[1] = round(lp1[1] / self.snapSize) * self.snapSize
				
			## preserve aspect ratio (this can override snapping)
			if h['lockAspect'] or (modifiers & QtCore.Qt.AltModifier):
				#arv = Point(self.preMoveState['size']) - 
				lp1 = lp1.proj(lp0)
			
			## determine scale factors and new size of ROI
			hs = h['pos'] - c
			if hs[0] == 0:
				hs[0] = 1
			if hs[1] == 0:
				hs[1] = 1
			newSize = lp1 / hs
			
			## Perform some corrections and limit checks
			if newSize[0] == 0:
				newSize[0] = newState['size'][0]
			if newSize[1] == 0:
				newSize[1] = newState['size'][1]
			if not self.invertible:
				if newSize[0] < 0:
					newSize[0] = newState['size'][0]
				if newSize[1] < 0:
					newSize[1] = newState['size'][1]
			if self.aspectLocked:
				newSize[0] = newSize[1]
			minx = 50
			miny = 50
			self.do_scale(int(max(miny, newSize[1])), int(max(minx, newSize[0])))
			if newSize[0] > minx and newSize[1] > minx:
				ROI.movePoint(self, handle, pos, modifiers, finish, coords)
		else:
			ROI.movePoint(self, handle, pos, modifiers, finish, coords)

