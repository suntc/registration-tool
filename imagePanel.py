'''
Created on 2016-07-10
@author: Sun Tianchen
'''

from imageROI import ImageROI
from load import ImageFileLoader
import align
from buttonArea import ButtonArea
import pyqtgraph as pg
from skimage import transform as tf
from PyQt4 import QtCore, QtGui
import cv2
import numpy as np

class ImagePanel(QtGui.QWidget):
	"""
	docstring for ImagePanel
	============================
	image_arrays:		[arr, arr, ...] arr is numpy array of the image data

	"""
	sigHeatmapLoaded = QtCore.Signal(object)
	def __init__(self, layout, image_arrays=[], configs=None):
		QtGui.QWidget.__init__(self)
		self.w = layout
		self.image_arrays = image_arrays
		self.imroi = [] ## only used by send_back, considering remove this
		self.images = {}
		self.raw_array = {}
		self.triangulation_array = None
		self.warped_top_array = None
		self.backActivated = False
		self.state = {
			'lastAlign' : None, ## 'rigid'/'affine'
			'heatmapLoaded' : False,
			'heatmapShown'	: False,
			'lastHeatmap' : None,
			'showTri' : True,
		}
		self.prev_region = [{'size':None, 'pos':None, 'angle':None}, {'size':None, 'pos':None, 'angle':None}]
		self.affine_matrix = None
		self.piecewise_param = None
		self.projective_tform = None
		self.v = self.w.addViewBox(row=0, col=0, lockAspect=True)
		self.button_area = ButtonArea(parent=self, mode='panel')
		self.w.addItem(self.button_area, row=1, col=0)
		self.w.layout.setRowFixedHeight(1, 12.)

		g = pg.GridItem()
		self.v.addItem(g)
		for i, arr in enumerate(self.image_arrays):
			self.add_image(arr)

		## signals
		self.button_area.buttons['restore'].clicked.connect(self.restore_alignment)
		self.button_area.buttons['tri'].clicked.connect(self.triangulation_requested)
		
	def image_loaded(self, (id, arr)):
		## slot method for imageBar's sigImageLoaded
		print "slot: image loaded"
		self.add_image(id, arr)
		self.state['lastAlign'] = None
		if id == 0: ## need other clearance
			self.state['heatmapLoaded'] = False
			self.state['heatmapShown'] = False
			self.state['lastHeatmap'] = None
		## signal
		if id == 0:
			self.images[id].sigRegionChanged.connect(self.image_top_changed)
		else:
			self.images[id].sigRegionChanged.connect(self.image_bottom_changed)

	def transform_requested(self, (scale, angle, tx, ty)):
		## slot method for sigTransformRequested
		## last phase of a alignment
		print "transform_requested %f,%f,%f,%f" % (scale, angle, tx, ty)
		self.images[0].setAngle(-90)
		self.images[0].setPos((0, 0))
		self.images[0].set_image(cv2.resize(self.raw_array[0], None, fx=scale, fy=scale))
		self.images[0].rotate(angle)
		self.images[0].translate((tx, ty, 1))
		self.images[0].set_alpha(0.5 * 255)
		self.images[1].setAngle(-90)
		self.images[1].setPos((0, 0))
		self.images[1].set_alpha(0.5 * 255)
		self.state['lastAlign'] = 'rigid'

	def affine_requested(self, (aft)):
		## slot method for sigAffineRequested
		## last phase of a alignment
		shape = self.raw_array[1].shape
		nphoto = cv2.warpAffine(self.raw_array[0], aft, (shape[1], shape[0]))
		self.images[0].setAngle(-90)
		self.images[0].setPos((0, 0))
		self.images[0].set_image(nphoto)
		self.images[0].do_scale(shape[1], shape[0])
		self.images[0].set_alpha(0.5 * 255)
		self.images[1].setAngle(-90)
		self.images[1].setPos((0, 0))
		self.images[1].set_alpha(0.5 * 255)
		self.images[1].do_scale(shape[1], shape[0])
		## for heatmap
		self.state['lastAlign'] = 'affine'
		self.affine_matrix = aft
		#self.images[0].affine_heatmap(aft, shape[1], shape[0])
		#self.images[0].set_size((shape[0], shape[1]))

	def piecewise_requested(self, (fp, tp, tri)):
		shape = self.raw_array[1].shape
		'''
		polys = []
		for t in tri:
			polys.append(np.array(np.dstack((fp[:,t][1],fp[:,t][0]))[0], dtype=np.int32))
		cv2.polylines(self.raw_array[0], polys, True, [0,0,255,255], 2)
		from PIL import Image
		img = Image.fromarray(self.raw_array[0])
		img.show()
		'''
		nphoto = align.pw_affine(self.raw_array[0],self.raw_array[1],fp,tp,tri)
		self.images[0].setAngle(-90)
		self.images[0].setPos((0, 0))
		self.images[0].set_image(nphoto)
		self.images[0].set_alpha(0.5 * 255)
		self.images[1].setAngle(-90)
		self.images[1].setPos((0, 0))
		self.images[1].set_alpha(0.5 * 255)
		self.images[0].do_scale(shape[1], shape[0])
		self.images[1].do_scale(shape[1], shape[0])
		## create triangulation image
		self.triangulation_array = nphoto.copy()
		polys = []
		for t in tri:
			polys.append(np.array(np.dstack((tp[:,t][1],tp[:,t][0]))[0], dtype=np.int32))
		cv2.polylines(self.triangulation_array, polys, True, [0,0,255,255], 2)
		#cv2.imshow('img',self.triangulation_array)
		#cv2.waitKey(0)
		'''
		self.images[0].setAngle(-90)
		self.images[0].setPos((0, 0))
		self.images[0].set_image(self.triangulation_array)
		self.images[0].set_alpha(0.5 * 255)
		'''
		## save state
		self.state['lastAlign'] = 'piecewise'
		self.piecewise_param = (fp, tp, tri)
		self.warped_top_array = nphoto

	def projective_requested(self, (tform)):
		print "imagePanel: projective_requested"
		shape = self.raw_array[1].shape
		nphoto = tf.warp(self.raw_array[0], tform, output_shape=(shape[0], shape[1]))
		#cv2.imshow('img', nphoto)
		#cv2.waitKey(0)
		self.images[0].setAngle(-90)
		self.images[0].setPos((0, 0))
		self.images[0].set_image(nphoto)
		self.images[0].do_scale(shape[1], shape[0])
		self.images[0].set_alpha(0.5 * 255)
		self.images[1].setAngle(-90)
		self.images[1].setPos((0, 0))
		self.images[1].set_alpha(0.5 * 255)
		self.images[1].do_scale(shape[1], shape[0])
		## for heatmap
		self.state['lastAlign'] = 'projective'
		self.projective_tform = tform

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


	def heatmap_requested(self):
		## slot method to load or show/hide heatmap
		## make sure sample photo is already loaded
		if not self.state['heatmapLoaded']: ## heatmap has not been loaded
			fname = pg.FileDialog.getOpenFileName(None, "Open matlab File", './', "Matlab File (*.mat)")
			loader = ImageFileLoader()
			if fname != '' and fname != None:
				print "file name = ", fname
				array_dict = loader.mat_to_array(str(fname))
				row = self.raw_array[0].shape[0]
				col = self.raw_array[0].shape[1]
				to_pop = []
				print "row = ", row
				print "col = ", col
				for key in array_dict:
					print array_dict[key].shape[0], array_dict[key].shape[1]
					## do rotation check
					if array_dict[key].shape[0] == row and array_dict[key].shape[1] == col:
						pass
					elif array_dict[key].shape[1] == row and array_dict[key].shape[0] == col:
						## need rotation
						array_dict[key] = np.rot90(key)
					else:
						to_pop.append(key)
				for k in to_pop:
					print "delete ", k
					array_dict.pop(k)
				self.sigHeatmapLoaded.emit(array_dict) ## inform control widget
				self.state['heatmapLoaded'] = True
				self.images[0].set_heatmaps(array_dict)
		'''
		if not self.state['heatmapShown']: ## heatmap is not shown
			self.images[0].show_heatmap(True)
		else:
			self.images[0].show_heatmap(False)
		'''

	def heatmap_changed(self, item, column):
		## slot
		#print "item = ", item.text(column)
		#print "column = ", column
		key = str(item.text(column))
		if self.state['lastHeatmap'] == key:
			## hide the current heatmap
			self.images[0].show_heatmap(enable=False)
			self.state['lastHeatmap'] = None
			return
		self.state['lastHeatmap'] = key
		if self.state['lastAlign'] == 'affine':
			self.images[0].show_heatmap(enable=True, key=key, mode='affine', param=self.affine_matrix)
		elif self.state['lastAlign'] == 'piecewise':
			self.images[0].show_heatmap(enable=True, key=key, mode='piecewise', param=self.piecewise_param)
		elif self.state['lastAlign'] == 'projective':
			self.images[0].show_heatmap(enable=True, key=key, mode='projective', param=self.projective_tform)
		else:
			self.images[0].show_heatmap(enable=True, key=key, mode=None)

	def curve_changed(self, (arr, curve_arr)):
		## slot for sigCurveChanged
		print "slot curve changed"
		#self.images[1].image_item.setImage(cv2.resize(arr, dsize=(int(self.images[1].state['size'][1]), int(self.images[1].state['size'][0]) ))) ## not needed
		prev_alpha =  self.images[1].prev_alpha
		## looks bad that set_alpha is used both a slot method and a function...
		self.images[1].prev_alpha = 255
		self.images[1].current_curve_array = curve_arr
		#self.images[1].set_alpha(self.images[1].prev_alpha)
		self.images[1].set_alpha(prev_alpha)
		print "right set alpha =", self.images[1].prev_alpha

################################################################
## button area

	def restore_alignment(self):
		if 0 in self.images:
			self.images[0].setPos((0, 0))
			self.images[0].setAngle(-90)
			if self.state['lastAlign'] == None:
				self.images[0].do_scale(self.raw_array[0].shape[1], self.raw_array[0].shape[0])
			else:
				self.images[0].do_scale(self.raw_array[1].shape[1], self.raw_array[1].shape[0])
			#self.images[0].set_alpha(0.5 * 255)
		if 1 in self.images:
			self.images[1].setPos((0, 0))
			self.images[1].setAngle(-90)
			#self.images[1].set_alpha(0.5 * 255)
			self.images[1].do_scale(self.raw_array[1].shape[1], self.raw_array[1].shape[0])

	def triangulation_requested(self):
		if self.state['lastAlign'] == 'piecewise' and self.triangulation_array != None:
			if self.state['showTri']:
				self.button_area.buttons['tri'].setOpacity(0.4)
				alpha = self.images[0].prev_alpha
				self.images[0].set_image(self.warped_top_array)
				self.state['showTri'] = False
			else:
				self.button_area.buttons['tri'].setOpacity(1)
				alpha = self.images[0].prev_alpha
				self.images[0].set_image(self.triangulation_array)
				self.state['showTri'] = True
			s = self.images[0].getState()
			self.images[0].do_scale(int(s['size'][1]), int(s['size'][0]))
			self.images[0].set_alpha(alpha)
			self.images[0].setSize([int(s['size'][0]), int(s['size'][1])])


################################################################

	def image_top_changed(self):
		## slot
		#print "top changed ", self.images[0].state_flag['isDrag']
		states = self.images[0].state
		bs = self.images[1].state
		#self.images[1].setAngle(bs['angle'] + states['angle']-self.prev_region[0]['angle'])
		self.prev_region[0] = self.images[0].saveState()

	def image_bottom_changed(self):
		## slot
		#print "bottom changed", self.images[1].state_flag['isDrag']
		self.prev_region[1] = self.images[1].saveState()