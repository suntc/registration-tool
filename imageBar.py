'''
Created on 2016-07-12
@author: Sun Tianchen
'''

from imageROI import ImageROI

class InImageCell(object):
	def __init__(self, v, roi):
		self.v = v
		self.roi = roi

class ImageBar(object):
	"""docstring for ImageBar"""
	def __init__(self, layout, images):
		self.w = layout
		self.images = images
		self.cells = []
		for i, item in enumerate(images):
			v = self.w.addViewBox(row=i, col=0, lockAspect=True, enableMouse=False)
			roi = ImageROI([0,0], [100,100], simple=True)
			roi.set_image(item)
			v.addItem(roi)
			self.cells.append(InImageCell(v, roi))
