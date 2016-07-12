'''
Created on 2016-07-10
@author: Sun Tianchen
'''

from imageROI import ImageROI
import pyqtgraph as pg

class ImagePanel(object):
	"""
	docstring for ImagePanel
	============================
	image_arrays:		[arr, arr, ...] arr is numpy array of the image data

	"""
	def __init__(self, layout, image_arrays):
		self.w = layout
		self.image_arrays = image_arrays
		self.imroi = []
		self.backActivated = False
		self.v = self.w.addViewBox(row=0, col=0, lockAspect=True)
		for i, arr in enumerate(self.image_arrays):
			roi = ImageROI([0,0], [100,100])
			roi.set_image(arr)
			roi.setZValue(10 + i)
			g = pg.GridItem()
			self.v.addItem(g)
			self.v.addItem(roi)
			roi.sigSendBackRequested.connect(self.send_back)
			self.imroi.append(roi)

	def add_image(self, arr):
		count = len(self.imroi)
		self.imroi.sort(key=lambda k: k.zValue())
		roi = ImageROI([0,0], [100,100])
		roi.set_image(arr)
		roi.setZValue(10 + count)
		self.v.addItem(roi)
		roi.sigSendBackRequested.connect(self.send_back)
		self.imroi.append(roi)

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
