'''
Created on 2016-07-11
@author: Sun Tianchen
'''

from itertools import groupby
import pyqtgraph as pg
from skimage import transform as tf
from pyqtgraph import ROI
from PyQt4 import QtCore, QtGui
import cv2
import numpy as np
import poly_point_isect
from uiImageItem import UiImageItem
from scipy.spatial.distance import pdist
import align

class CurveObject(object):
	"""Class representing the drag and drop curve"""
	def __init__(self, path, pen, track=None, tense=None, color=None, size=None, line=None, cap=None, join=None):
		self.path = path
		self.pen = pen
		self.track = track
		self.pen_param = {'color':color, 'size':size, 'line':line, 'cap':cap, 'join':join}
		self.curve_tense = tense

class ImageROI(ROI):
	"""subclass of ROI for holding/processing image
	   for now the heatmap methods and curve methods are independent: heatmap uses heatmap_current_array for displaying
	   if sample needs curve drawing too, we need to add a judgement to select heatmap_current_array/current_array
	"""

	sigSendBackRequested = QtCore.Signal(object)
	sigAddVertexRequested = QtCore.Signal(object)
	sigLoadImageRequested = QtCore.Signal(object)
	sigDragTriggered = QtCore.Signal(object)
	sigTrackCompleted = QtCore.Signal(object)
	sigCurveUpdated = QtCore.Signal(object)

	def __init__(self, pos, size, centered=False, simple=False, sideScalers=False, movable=True, rotatable=True, sendBack=True, alpha=False, **args):
		self.sendBack = sendBack
		self.image_array = None
		self.image_item = None
		## created for histo
		self.original_array = None
		self.current_array = None
		self.current_curve_array = None
		## created for sample photo
		self.heatmap_original_arrays = None ## dictionary
 		self.heatmap_current_array = None

		self.curve_color = QtGui.QColor(79,106,25)
		self.curve_tense = 0.4
		self.curve_size = 5
		self.prev_alpha = 255

		self.state_flag = {}
		self.state_flag['isDrag'] = False
		self.state_flag['isPaint'] = False
		self.state_flag['isMoving'] = False
		self.state_flag['isHeatmap'] = False
		self.state_flag['isDelete'] = False

		self.widgets = {}

		self.curves = [] ## storing curveObject
		self.track = []

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
		alphaSlider.setMinimum(20)
		alphaSlider.setValue(255/2)
		alphaSlider.valueChanged.connect(self.set_alpha)
		self.widgets['alpha'] = alphaSlider
		alpha.setDefaultWidget(alphaSlider)
		self.menu.addAction(alpha)
			
##############################################################################
## setup methods

	def set_image(self, image_arr):
		print "imageROI set_image"
		for child in self.childItems():
			if isinstance(child, pg.graphicsItems.ImageItem.ImageItem):
				child.setParentItem(None)
		## use uiImageItem instead of imageItem
		#img = pg.ImageItem(image_arr)
		img = UiImageItem(image_arr)
		## may add to paralist
		'''
		kern = np.array([
		    [[100,100,100], [100,100,100], [100,100,100]],
		    [[100,100,100], [100,100,100], [100,100,100]],
		    [[100,100,100], [100,100,100], [100,100,100]]
		])
		
		kern = np.array([
		    [[100,100,100], [100,100,100]],
		    [[100,100,100], [100,100,100]],
		])
		'''
		#img.set_draw_kernel(kern, mask=kern, center=(1,1), mode='set')
		#img.set_draw_kernel(center=(1,1), mode='set')
		#img.set_draw_pen(self.curve_color, self.curve_size)
		img.setParentItem(self)
		self.image_array = image_arr
		self.original_array = np.array(image_arr, copy=True)
		self.current_array = np.array(self.original_array, copy=True)
		self.current_curve_array = None
		self.image_item = img
		self.setSize([image_arr.shape[0], image_arr.shape[1]])

	def set_alpha(self, alpha):
		#print(self.current_curve_array == None)
		self.widgets['alpha'].setValue(int(alpha))
		if self.current_curve_array == None or np.sum(self.current_array[:,:,3]) == 0:
			self.image_item.setOpacity(alpha/255.)
			self.prev_alpha = alpha
		else:
			if abs(self.prev_alpha - alpha) < 10:
				return
			self.image_item.setOpacity(1)
			temp_arr = np.array(self.original_array, copy=True) ## not good for future work?, maybe add other element
			temp_arr[:,:,3] = alpha
			self.current_array = self.overlap_image(self.current_curve_array, temp_arr)
			#self.current_array = temp_arr
			self.image_item.setImage(self.current_array)
			self.prev_alpha = alpha

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

	def load_image_clicked(self, item):
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
		if not self.state_flag['isHeatmap']:
			self.image_item.setImage(cv2.resize(self.current_array, dsize=(x, y)))
		else:
			self.image_item.setImage(cv2.resize(self.heatmap_current_array, dsize=(x, y)))
		self.image_item.setParentItem(self)

	def get_control_points(self, x0, y0, x1, y1, x2, y2, t):
		## computing contorl points for cubic spline
		## (x1, y1) is the point in the middle
		d01 = pdist([[x0,y0],[x1,y1]])
		d12 = pdist([[x2,y2],[x1,y1]])
		fa = t * d01 / (d01 + d12) ## scale factor
		fb = t * d12 / (d01 + d12)
		p1x = x1 - fa * (x2 - x0)
		p1y = y1 - fa * (y2 - y0)
		p2x = x1 + fb * (x2 - x0)
		p2y = y1 + fb * (y2 - y0)
		return [p1x, p1y], [p2x, p2y] 


	def mouseClickEvent(self, ev):
		if ev.button() == QtCore.Qt.LeftButton:
			print "left click ui image"
			print ev.pos()
			print "is delete = ", self.state_flag['isDelete']
			ev.accept()
			if not (self.state_flag['isPaint'] or self.state_flag['isDelete']):## if is painting, don't send click signal
				self.sigAddVertexRequested.emit((self, ev.pos()))
			elif self.state_flag['isDelete']:
				self.delete_curve(ev.pos().x(), ev.pos().y())
				## delete curve: build a rect around pos and judge interlect
		ROI.mouseClickEvent(self, ev)
	
	'''
	def mouseDragEvent(self, ev):
		print "ROI drag"
		track = []
		if ev.button() != QtCore.Qt.LeftButton:
			ev.ignore()
			return
		else:
			if self.isPaint:
				ev.accept()
				self.image_item.draw_at(ev.pos())
				#ROI.mouseDragEvent(self, ev)
	'''
##########################################################################
## heatmap methods

	def set_heatmaps(self, hm_arrs):
		self.heatmap_original_arrays = hm_arrs

	def affine_heatmap(self, key, aft):
		self.heatmap_current_array = cv2.warpAffine(self.heatmap_original_arrays[key], aft, (self.image_array.shape[1], self.image_array.shape[0]))

	def projective_heatmap(self, key, tform):
		self.heatmap_current_array = tf.warp(self.heatmap_original_arrays[key], tform, output_shape=(self.image_array.shape[0], self.image_array.shape[1]))

	def piecewise_affine_heatmap(self, key, param):
		## param (fp, tp, tri)
		fp = param[0]
		tp = param[1]
		tri = param[2]
		back_arr = np.zeros([self.state['size'][0],self.state['size'][1],4])
		self.heatmap_current_array = align.pw_affine(self.heatmap_original_arrays[key],back_arr,fp,tp,tri)
		ri, ci, di = np.nonzero(self.heatmap_current_array)
		self.heatmap_current_array[ri,ci,3] = 255
		pass

	def show_heatmap(self, enable, key=None, mode=None, param=None):
		if enable:
			self.state_flag['isHeatmap'] = True
			if mode == 'affine':
				self.affine_heatmap(key, param)
			elif mode == 'piecewise':
				self.piecewise_affine_heatmap(key, param)
			elif mode == 'projective':
				self.projective_heatmap(key, param)
			else:
				self.heatmap_current_array = self.heatmap_original_arrays[key]
			## overlap the heatmap and the array
			## transparent part in heat map array is [0,0,0,0]
			#b, g, r, a = cv2.split(self.heatmap_current_array)
			#self.heatmap_current_array = cv2.merge((r, g, b, a))
			self.heatmap_current_array = self.overlap_image(self.heatmap_current_array, self.current_array)
			self.image_item.setImage(cv2.resize(self.heatmap_current_array, dsize=(int(self.state['size'][1]), int(self.state['size'][0]) )))

		else:
			self.state_flag['isHeatmap'] = False
			self.image_item.setImage(cv2.resize(self.current_array, dsize=(int(self.state['size'][1]), int(self.state['size'][0]) )))
			#self.image_item.setImage(self.original_array)


##########################################################################
## methods for drawing curve

	def set_curve_pen(self, color, size, tense):
		## slot method for button['ok']
		## set pen for drawing curve
		self.image_item.set_draw_pen(color, size)
		argb = color.rgb()
		a = int(argb >> 24)
		r = int(argb >> 16 & 255)
		g = int(argb >> 8 & 255)
		b = int(argb & 255)
		self.curve_size = size
		self.curve_tense = tense
		self.curve_color = QtGui.QColor(b, g, r)

	def mouseDragEvent(self, ev):
		if ev.button() != QtCore.Qt.LeftButton:
			ev.ignore()
			return
		else:
			self.state_flag['isDrag'] = True
			print "start drag", self.state_flag['isDrag']
			if ev.isStart():
				self.track = []
			if self.state_flag['isPaint']:
				if ev.isStart():
					print "start"
					self.state_flag['isMoving'] = True
				ev.accept()
				print ev.pos()
				try:
					self.image_item.draw_at(ev.pos())
					self.track.append((ev.pos().x(),ev.pos().y()))
					#self.sigDragTriggered.emit(pg.Point(ev.pos().y(),-ev.pos().x()))
					#self.sigDragTriggered.emit(ev.pos())
				except ValueError as e:
					pass
			else:
				ROI.mouseDragEvent(self, ev)

		if ev.isFinish():
			print "finish drag"
			self.state_flag['isDrag'] = False
			if self.state_flag['isMoving'] == True:
				print "end"
				self.track.append((ev.pos().x(),ev.pos().y()))
				try:
					self.image_item.draw_at(ev.pos())
				except ValueError as e:
					pass
				self.image_item.setImage(np.array(self.original_array, copy=True), levels=[0,255])
				#self.image_item.setImage(self.image_array)
				#self.sigDragTriggered.emit(pg.Point(ev.pos().y(),-ev.pos().x()))
				#self.sigDragTriggered.emit(ev.pos())
				#self.sigTrackCompleted.emit(self)
				slack = True
				self.track = [x[0] for x in groupby(self.track)]
				segments = []
				for i in range(len(self.track)-1):
					segments.append((self.track[i],self.track[i+1]))
				try:
					isect = poly_point_isect.isect_segments(tuple(segments), True)
				except AssertionError as e:
					## there are some problems with the method
					isect = []
				isect.sort(key=lambda k:k[1][1])
				print "track has", len(self.track), "points"
				## allow drawing unclosed curve, so the instersection judgement is not needed
				'''
				if len(isect) > 0:
					first_isect = isect[0]
					print "first intersect: ", first_isect
					self.track = self.track[first_isect[1][0]+1 : first_isect[1][1]-1] + [first_isect[0]]
					print len(self.track)
					#self.curves.append(self.make_curve([[30,30],[50,5],[300,30],[400,100],[300,300],[200,400],[30,300]], 0.5, 1))
					#print self.track
					#self.track = [(124.79421229324313, 300.80197629011207), (134.39463578398144, 267.200494072528), (148.7952710200889, 233.59901185494397), (161.59583567440663, 203.1976708009393), (172.79632974693467, 187.1969649830421), (179.19661207409354, 179.19661207409354), (193.597247310201, 164.79597683798607), (217.59830603704674, 139.19484752935062), (241.5993647638925, 123.19414171145343), (264.00035290894857, 113.59371822071512), (288.00141163579434, 103.99329472997684), (308.8023291990607, 97.59301240281798), (328.0031761805373, 94.39287123923853), (350.40416432559334, 94.39287123923853), (372.8051524706494, 103.99329472997684), (385.6057171249671, 108.79350647534599), (393.60607003391567, 115.19378880250486), (406.40663468823345, 123.19414171145343), (414.406987597182, 131.19449462040205), (420.8072699243409, 143.99505927471978), (427.20755225149975, 155.19555334724777), (433.60783457865864, 171.19625916514497), (440.0081169058175, 191.99717672841126), (444.8083286511866, 214.39816487346735), (446.40839923297636, 223.99858836420566), (444.8083286511866, 243.19943534568222), (438.4080463240278, 265.6004234907383), (432.0077639968689, 283.2011998904252), (427.20755225149975, 291.20155279937376), (424.00741108792033, 292.8016233811635), (420.8072699243409, 296.0017645447429), (419.2071993425512, 297.60183512653265), (409.60677585181287, 304.0021174536915), (401.6064229428643, 308.80232919906064), (395.2061406157054, 312.0024703626401), (380.80550537959795, 320.0028232715887), (363.20472897991107, 328.00317618053725), (345.6039525802242, 336.0035290894859), (329.603246762327, 345.60395258022413), (323.20296443516816, 348.8040937438036), (315.2026115262195, 353.60430548917276), (312.0024703626401, 353.60430548917276), (304.00211745369154, 358.4045172345419), (296.0017645447429, 361.60465839812133), (284.8012704722149, 368.0049407252802), (278.40098814505603, 371.2050818888596), (268.8005646543177, 372.8051524706493), (262.4002823271589, 372.8051524706493), (254.39992941821023, 372.8051524706493), (239.99929418210277, 372.8051524706493), (220.7984472006262, 366.4048701434905), (209.59795312809817, 363.20472897991107), (206.39781196451875, 361.60465839812133), (201.5976002191496, 356.8044466527522), (193.597247310201, 352.004234907383), (185.5968944012524, 344.00388199843445), (180.79668265588325, 337.60359967127556), (172.79632974693467, 326.4031055987476), (164.79597683798607, 318.40275268979894), (163.19590625619637, 316.80268210800926), (153.59548276545806, 305.6021880354812), (147.1952004382992, 294.4016939629532), (140.7949181111403, 281.60112930863545), (132.358182316249, 274.328081209592)]
					self.curves.append(CurveObject(path=self.make_curve(self.track, self.curve_tense, 8), pen=QtGui.QPen(self.curve_color, self.curve_size, QtCore.Qt.SolidLine, QtCore.Qt.FlatCap, QtCore.Qt.MiterJoin)))
				'''
				#self.curves.append(CurveObject(path=self.make_curve(self.track, self.curve_tense, step='auto'), pen=QtGui.QPen(self.curve_color, self.curve_size, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin)))
				self.curves.append(CurveObject(self.make_curve(self.track, self.curve_tense, step='auto'), QtGui.QPen(self.curve_color, self.curve_size, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin), self.track, self.curve_tense,  self.curve_color, self.curve_size, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
				self.update_curve()
				self.state_flag['isMoving'] = False
	

	def filter_track(self, track, dist_threshold=3, slope_threshold=None):
		"""
		dist_threshold=3: if gap > pensize * 3 -- keep the point 
		keep how many?
		"""
		const = 90
		pensize = np.sqrt(self.original_array.shape[0] * self.original_array.shape[1]) / const
		minp = 30
		pensize = round(pensize)
		total_dist =  np.sum( [pdist([track[i],track[i+1]]) for i in range(len(track)-1)] )
		print "minp * pensize = ",  minp * pensize
		if total_dist < minp * pensize:
			return track
		print "total_dist = " ,total_dist
		ntrack = [track[0]]
		cur_dist = 0
		for i in range(len(track)-2):
			cur_dist += pdist(np.array([track[i+1], track[i]]))
			if cur_dist > pensize * dist_threshold:
				ntrack.append(track[i+1])
				cur_dist = 0
		ntrack.append(track[len(track)-1])
		print len(ntrack), "points are left"
		return ntrack


	def make_curve(self, track, t, step=1):
		## return qpaintep: int, 3 means 1/3 points are leftterpath
		## s
		ntrack = []
		ntrack.append(track[0])
		## improve the step later using distance
		if step is not 'auto':
			for i in range(1, len(track)-1, step):
				ntrack.append(track[i])
		else:## auto determine which points are left by point-wise distance and slope
			ntrack = self.filter_track(track)

		ntrack.append(track[len(track)-1])
		cpoints = [[None, None] for i in ntrack]
		closed = False ## not needed to be closed curve
		for i in range(len(ntrack)):
			if i == len(ntrack) - 1:
				p1, p2 = self.get_control_points(ntrack[i-1][0], ntrack[i-1][1], ntrack[i][0], ntrack[i][1], ntrack[0][0], ntrack[0][1], t)
				cpoints[i-1][1] = p1
				cpoints[i][0] = p2
			elif i == 0:
				p1, p2 = self.get_control_points(ntrack[len(ntrack)-1][0], ntrack[len(ntrack)-1][1], ntrack[0][0], ntrack[0][1], ntrack[1][0], ntrack[1][1], t)
				cpoints[len(ntrack)-1][1] = p1
				cpoints[0][0] = p2
			else:
				p1, p2 = self.get_control_points(ntrack[i-1][0], ntrack[i-1][1], ntrack[i][0], ntrack[i][1], ntrack[i+1][0], ntrack[i+1][1], t)
				cpoints[i-1][1] = p1
				cpoints[i][0] = p2
		#print p1, p2		
		path = QtGui.QPainterPath()
		path.moveTo(ntrack[0][0], ntrack[0][1])
		## make painterPath
		if closed:
			for i in range(len(ntrack)):
				if i == len(ntrack) - 1:
					path.cubicTo(cpoints[i][0][0], cpoints[i][0][1], cpoints[i][1][0], cpoints[i][1][1], ntrack[0][0], ntrack[0][1])
					#path.lineTo(ntrack[0][0], ntrack[0][1])
				else:
					path.cubicTo(cpoints[i][0][0], cpoints[i][0][1], cpoints[i][1][0], cpoints[i][1][1], ntrack[i+1][0], ntrack[i+1][1])
					#path.lineTo(ntrack[i+1][0], ntrack[i+1][1])
		else:
			for i in range(len(ntrack)-1):
				path.cubicTo(cpoints[i][0][0], cpoints[i][0][1], cpoints[i][1][0], cpoints[i][1][1], ntrack[i+1][0], ntrack[i+1][1])
				#path.lineTo(ntrack[i+1][0], ntrack[i+1][1])

		return path

	def update_curve(self):
		## line 178, 90
		#n_image = np.array(self.current_array, copy=True)
		n_image = np.array(self.original_array, copy=True)
		self.device = QtGui.QImage(n_image, self.image_array.shape[0], self.image_array.shape[1], QtGui.QImage.Format_ARGB32)
		self.device.fill(QtGui.qRgba(0,0,0,0))
		p = QtGui.QPainter(self.device)
		for curve in self.curves:
			p.setPen(curve.pen)
			p.drawPath(curve.path)
			#arr = pg.functions.imageToArray(self.device, copy=True)
			#cv2.imshow('img', arr)
			#cv2.waitKey(0)
		#p.drawText(20,300,"Hello")
		arr = pg.functions.imageToArray(self.device, copy=True)
		self.current_curve_array = arr
		## overlay curve on current image
		'''
		temp_arr = np.array(arr, copy=True)
		temp_arr[np.nonzero(temp_arr)] = 1
		temp_arr = 1 - temp_arr
		n_image = n_image * temp_arr + arr
		'''
		n_image = self.overlap_image(arr, n_image)
		self.current_array = n_image
		#cv2.imshow('img', n_image)
		#cv2.waitKey(0)
		self.image_item.setImage(np.array(n_image, copy=True), levels=[0,255])
		self.sigCurveUpdated.emit((np.array(n_image, copy=True), np.array(self.current_curve_array, copy=True)) ) ## inform imageBar

	def delete_curve(self, x, y, device=None):
		## using matrix methods
		#if self.device == None:
			#self.device = QtGui.QImage(n_image, self.image_array.shape[0], self.image_array.shape[1], QtGui.QImage.Format_ARGB32)
		self.device2 = QtGui.QImage(self.image_array.shape[0], self.image_array.shape[1], QtGui.QImage.Format_ARGB32)
		#rect = QtCore.QRectF(x-r, y-r, margin, margin)
		hit = False
		p = QtGui.QPainter(self.device2)
		for i, curve in enumerate(self.curves):
			self.device2.fill(QtGui.qRgba(0,0,0,0))
			p.setPen(curve.pen)
			p.drawPath(curve.path)
			radius = curve.pen.width() / 2. + 1
			arr = pg.functions.imageToArray(self.device2, copy=True)
			selected = arr[x-radius : x+radius+1, y-radius : y+radius+1]
			if np.sum(selected) != 0:
				hit = True
				print "delete hit"
				self.curves.pop(i)
				self.update_curve()
				#self.image_item.setImage(self.original_array, levels=[0,255])
				return

	def restore_curve_file(self, curves_params):
		## curves_params: [[track, tense, pen_param]]
		for item in curves_params:
			self.curves.append(CurveObject(self.make_curve(item[0], item[1], step='auto'), QtGui.QPen(item[2]['color'], item[2]['size'], item[2]['line'], item[2]['cap'], item[2]['join']), item[0], item[1], item[2]['color'], item[2]['size'], item[2]['line'], item[2]['cap'], item[2]['join']))
		self.update_curve()

###############################################

	def overlap_image(self, front_arr, back_arr):
		## front arr's transparent part must be [0,0,0,0]
		temp_arr = np.array(front_arr, copy=True)
		temp_arr[np.nonzero(temp_arr)[0:2]] = np.array([1,1,1,1]) ## np.nonzero(temp_arr)[0:2] may have duplicates, low efficiency?
		temp_arr = 1 - temp_arr
		return back_arr * temp_arr + front_arr


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