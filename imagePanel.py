'''
Created on 2016-07-10
@author: Sun Tianchen
'''

from imageROI import ImageROI
import pyqtgraph as pg
import cv2
import numpy as np

class ImagePanel(object):
	"""
	docstring for ImagePanel
	============================
	image_arrays:		[arr, arr, ...] arr is numpy array of the image data

	"""
	def __init__(self, layout, image_arrays=[]):
		self.w = layout
		self.image_arrays = image_arrays
		self.imroi = [] ## only used by send_back, considering remove this
		self.images = {}
		self.raw_array = {}
		self.backActivated = False
		self.v = self.w.addViewBox(row=0, col=0, lockAspect=True)
		g = pg.GridItem()
		self.v.addItem(g)
		for i, arr in enumerate(self.image_arrays):
			self.add_image(arr)
		

	def image_loaded(self, (id, arr)):
		## slot method for imageBar's sigImageLoaded
		print "slot: image loaded"
		self.add_image(id, arr)

	def transform_requested(self, (scale, angle, tx, ty)):
		## slot method for sigTransformRequested
		print "transform_requested %f,%f,%f,%f" % (scale, angle, tx, ty)
		self.images[0].setAngle(-90)
		self.images[0].setPos((0, 0))
		self.images[0].set_image(cv2.resize(self.raw_array[0], None, fx=scale, fy=scale))
		self.images[0].rotate(angle)
		self.images[0].translate((tx, ty, 1))
		self.images[0].set_alpha(0.5 * 255)

	def affine_requested(self, (aft)):
		shape = self.raw_array[1].shape
		nphoto = cv2.warpAffine(self.raw_array[0], aft, (shape[1], shape[0]))
		self.images[0].setAngle(-90)
		self.images[0].setPos((0, 0))
		self.images[0].set_image(nphoto)
		self.images[0].set_alpha(0.5 * 255)
		#self.images[0].set_size((shape[0], shape[1]))
		

	def add_image(self, id, arr):
		if id not in self.images:
			count = len(self.imroi)
			self.imroi.sort(key=lambda k: k.zValue())
			## roi matches the size/shape of array
			shape = arr.shape
			roi = ImageROI([0,0], [shape[0],shape[1]], alpha=True)
			roi.set_image(arr)
			roi.setZValue(10 + count)
			self.v.addItem(roi)
			roi.sigSendBackRequested.connect(self.send_back)
			self.imroi.append(roi)
			self.images[id] = roi
			self.raw_array[id] = arr
			roi.setAngle(-90)
			roi.set_alpha(0.5 * 255)
			'''
			## just for test, to delete
			if id == 0:
				self.transform_requested((5.1, -12, -212, 640))
			'''

		else:
			self.images[id].set_image(arr)
			self.raw_array[id] = arr
			self.images[id].setAngle(-90)
			self.images[id].set_alpha(0.5 * 255)
			'''
			## just for test, to delete
			if id == 0:
				self.transform_requested((5.1, 15, 0, 0))
			'''

	def send_back(self, roi):
		print "send back"
		count = len(self.imroi)
		if count == 1:
			return
		self.imroi.sort(key=lambda k: k.zValue())
		bottomZ = self.imroi[0].zValue()
		for i, item in enumerate(self.imroi):
			if item is roi:
				roi.setZValue(bottomZ)
				break
			else:
				item.setZValue(self.imroi[i + 1].zValue())