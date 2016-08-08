'''
Created on 2016-07-12
@author: Sun Tianchen
'''
from PyQt4 import QtCore, QtGui
import pyqtgraph as pg
import numpy as np
from scipy.spatial.distance import pdist
from math import asin, pi
from uiImageItem import UiImageItem
from imageROI import ImageROI
from load import ImageFileLoader
from buttonArea import ButtonArea
from pathPlotItem import PathPlotItem
import align

class VertexList(object):
	"""
	VertexList stores the vertex-pair of the 2 input images
	designed for performing image warping
	======================
	remove()
	remove_pair()
	"""
	def __init__(self):
		self.vlist = {0 : [], 1 : []}
		#self.IDLE = 0
		#self.WAITFOR1 = 1
		#self.WAITFOR2 = 2
		#self.state = self.IDLE

	## add and remove may be methods of upper layer class
	'''
	def add_vertex(self, id, x, y):
		if id == 1:
			if self.state is IDLE:
				self.vlist.append({1:[x, y]})
				self.state = self.WAITFOR2
				return True
			elif self.state is WAITFOR1:
				self.vlist[len(self.vlist)-1].setdefault(1,[x, y])
				self.state = self.IDLE
				return True
			elif self.state is WAITFOR2:
				return False
		elif id == 2:
			if self.state is IDLE:
				self.vlist.append({2:[x, y]})
				self.state = self.WAITFOR2
				return True
			elif self.state is WAITFOR1:
				return False
			elif self.state is WAITFOR2:
				self.vlist[len(self.vlist)-1].setdefault(2,[x, y])
				self.state = self.IDLE
				return True
	'''

	def add_vertex(self, id, x, y):
		self.vlist[id].append([x, y])
		#self.vlist[len(self.vlist)-1].setdefault(id ,[x, y])

	'''
	def remove_vertex(self, id, index, x, y):
		count = len(self.vlist)
		if index < 0 or index > count - 1:
			return False
		if len(self.vlist[index]) == 2: ## corresponding images has that vertex pair
			self.vlist[index].pop(id)
			return True
		elif id in self.vlist[index]: ## corresponding images only have one(that) vertex 
			self.vlist.pop(index)
			return True

	def remove_vertex_pair(self, index, x, y):
		count = len(self.vlist)
		if index < 0 or index > count - 1:
			return False
		self.vlist.pop(index)
		return True
	'''

class InImageCell(object):
	def __init__(self, v, image, scatter, open_action=None, button_area=None):
		self.v = v
		self.image = image
		self.open_action = open_action
		self.scatter = scatter
		self.button_area = button_area
		

#class ImageBar(QtGui.QWidget):
class ImageBar(pg.GraphicsWidget):
	"""
		ImageBar serves as the interface of:
		1. load images into program and provide signal to inform imagePanel
		2. keep track of the state of the image: auto/manual, ready for adding point, ...
		3. allowing pointing
		4. performing icp algorithm and provide signal to inform imagePanel
		5. doing array transformation to provide right array to imagePanel for displaying
		6. provide button for interaction: choose mode, save project, lock aspect, delete point
		for icp, the bottom image is used as model

		notice, corrdinate of ROI and scatter plot are different
											(x, y)  -->  (y, -x)
	"""
	sigImageLoaded = QtCore.Signal(object)
	sigTransformRequested = QtCore.Signal(object)
	sigAffineRequested = QtCore.Signal(object)
	def __init__(self, layout, images=None, path=None):
		QtGui.QWidget.__init__(self)
		self.w = layout
		self.images = images
		## file related
		self.loader = ImageFileLoader()
		self.default_path = "./"
		## module state
		self.IDLE = 0
		self.WAITFORIMAGE = 1
		self.ADDINGVERTEX = 2
		self.CLIPPING = 3
		self.AUTO = 4
		self.MANUAL = 5
		self.state = {
			'icp'	: self.MANUAL,
			'shear'	: False,
			'ready'	: {},
			'locked' : [False, False],
			'delete' : [False, False],
		}
		self.cells = {}
		## max number of images can be loaded
		self.max_img = 2
		## create vertex list
		self.vl = VertexList()
		## create empty boxes to hold images
		for i in range(self.max_img):
			## add scatter plot item
			v = self.w.addViewBox(row=i*2, col=1, lockAspect=True, enableMouse=True)
			## button area
			ba = ButtonArea()
			self.w.addItem(ba, row=i*2+1, col=1)
			self.w.layout.setRowFixedHeight(i*2+1, 10.)
			scatter = pg.ScatterPlotItem(size=10, pen=pg.mkPen('w'), pxMode=True, brush=pg.intColor(100, 100), parent=v)
			scatter.setZValue(20)
			v.addItem(scatter)
			pathplot = PathPlotItem()
			v.addItem(pathplot)
			self.cells.setdefault(i, InImageCell(v, None, scatter, button_area=ba))
			#spots = [{'pos': [1000,-1000], 'data': 1},{'pos': [1200,-600], 'data': 1}]
			#scatter.addPoints(spots)
			#v = self.w.addViewBox(row=i, col=0, lockAspect=True, enableMouse=False)
			#self.cells.setdefault(i, InImageCell(v, UiImageItem()))
			##  signal and slot
			#scatter.sigHoverEvent.connect(self.delete_hover)
			scatter.sigClicked.connect(self.delete_point_clicked)
			ba.buttons['lock'].clicked.connect(self.lock_clicked)
			ba.buttons['del'].clicked.connect(self.delete_clicked)
		## setup menus
		self.set_menu()

		if images:
			for i, item in enumerate(images):
				img = UiImageItem()
				self.cells[i].v.addItem(img)
				self.cells[i].image = img
				img.setImage(item)
				img.sigAddVertexRequested.connect(self.add_point)
				img.sigLoadImageRequested.connect(self.load_image_requested)
		
		elif path:
			for i, fname in enumerate(path):
				arr = self.loader.load(str(fname))
				self.add_image(i, arr)
				self.state['ready'] = {}


	def set_menu(self):
		for k in self.cells:
			## remove unwanted menu action:"Mouse Mode", "X Axis", "Y Axis"
			for item in self.cells[k].v.menu.actions():
				if item.text() in ["Mouse Mode", "X Axis", "Y Axis"]:
					self.cells[k].v.menu.removeAction(item)
			## add new actions
			liAct = QtGui.QAction("Load Image", self.cells[k].v.menu)
			#liAct.triggered.connect(self.cells[k].image.load_imgae_clicked)
			self.cells[k].v.menu.addAction(liAct)
			self.cells[k].open_action = liAct
			spAct = QtGui.QAction("Save Points", self.cells[k].v.menu)
			spAct.triggered.connect(self.save_points)
			self.cells[k].v.menu.addAction(spAct)


	def load_image_requested(self, old_image):
		## slot method for loading
		print "load image in image Bar"
		for k in self.cells:
			if self.cells[k].image == old_image:
				fname = pg.FileDialog.getOpenFileName(None, "Open Image File", self.default_path)
				if fname == '' or fname == None:
					return
				print "file name = ", fname
				arr = self.loader.load(str(fname))
				self.add_image(k, arr)
				## send signal to image Panel to update
				
				

	def add_image(self, id, arr):
		"""
		should me more complex
		load image from disk --> make it a numpy array --> pass a image class for image processing --> make connections between this class and image processing class
													   --> pass to this class for displaying 
		"""
		## remove original image and add new one
		if self.cells[id].image:
			self.cells[id].v.removeItem(self.cells[id].image)
		'''
		img = UiImageItem()
		self.cells[id].v.addItem(img)
		img.setImage(arr)
		## rotate the imageItem (oddly the image is rotated by default)
		img.setRotation(-90)
		'''
		## use ROI instead of imageItem
		shape = arr.shape
		img = ImageROI([0,0], [shape[0],shape[1]], movable=False, rotatable=False, sendBack=False, parent=self.cells[id].v)
		img.set_image(arr)
		self.cells[id].image = img
		self.cells[id].v.addItem(img)
		
		## rotate the imageItem (oddly the image is rotated by default)
		## there is a bug with the rotate method
		img.setRotation(-90)
		
		## connect images signals to slot in class ImageBar
		img.sigAddVertexRequested.connect(self.add_point)
		img.sigLoadImageRequested.connect(self.load_image_requested)
		self.cells[id].open_action.triggered.connect(img.load_imgae_clicked)
		## clear existed points
		self.clear_point(id=id)
		## send signal to inform imagePanel
		self.sigImageLoaded.emit((id, arr))
		
		self.state['ready'][id] = True

	def draw_point(self, image_item, pos, id=None, symbol=None):
		## need to transform the coordinate
		## id is added later; it seems a little ugly
		if self.state['icp'] == self.AUTO:
			if symbol == None:
				spots = [{'pos': [pos[1],-pos[0]], 'data': 1, 'symbol' : 'o', 'size' : 10}]
			else:
				spots = [{'pos': [pos[1],-pos[0]], 'data': 1, 'symbol' : symbol, 'size' : 10}]
			if id is not None:
				self.cells[id].scatter.addPoints(spots)
				return id
			for k in self.cells:
				if self.cells[k].image == image_item:
					if k not in self.state['ready']:
						return
					## add vertex to screen
					self.cells[k].scatter.addPoints(spots)
					return k

		elif self.state['icp'] == self.MANUAL:
			spots = [{'pos': [pos[1],-pos[0]], 'data': 1, 'size' : 15}]
			if id is not None:
				if symbol == None:
					spots[0]['symbol'] = str(len(self.vl.vlist[k]) + 1)
				else:
					spots[0]['symbol'] = symbol
				## add vertex to screen
				self.cells[k].scatter.addPoints(spots)
				return id
			for k in self.cells:
				if self.cells[k].image == image_item:
					if k not in self.state['ready']:
						return
					## set number to label
					if symbol == None:
						spots[0]['symbol'] = str(len(self.vl.vlist[k]) + 1)
					else:
						spots[0]['symbol'] = symbol
					## add vertex to screen
					self.cells[k].scatter.addPoints(spots)
					return k

	def add_point(self, (image_item, pos)):
		## slot method for signal(addVertexRequsted)
		print "add point ", pos
		for k in self.cells:
			if self.cells[k].image == image_item:
				if k not in self.state['ready']:
					return
				break
		if self.state['delete'][k] == True:
			return
		id = self.draw_point(image_item, pos)
		if id is not None:
			## add vertex to vertex list
			self.vl.add_vertex(id, pos[0], pos[1])

	def clear_screen_point(self, id=None):
		## need repaint -- use addPoints
		## only clear points on the screen, keep the point data 
		print "clear points"
		if id != None:
			self.cells[id].scatter.clear()
			self.cells[id].scatter.addPoints([])
			#self.vl.vlist[id] = []
		else:
			for k in self.cells:
				self.cells[k].scatter.clear()
				self.cells[k].scatter.addPoints([])
			#self.vl.vlist = {0 : [], 1 : []}

	def clear_point(self, id=None):
		## need repaint -- use addPoints
		## only clear points on the screen, keep the point data 
		print "clear points"
		if id != None:
			self.cells[id].scatter.clear()
			self.cells[id].scatter.addPoints([])
			self.vl.vlist[id] = []
		else:
			for k in self.cells:
				self.cells[k].scatter.clear()
				self.cells[k].scatter.addPoints([])
			self.vl.vlist = {0 : [], 1 : []}

	def redraw_point(self, id=None):
		## rewrite for efficiency: draw only once
		if id == None:
			self.clear_screen_point()
			for key in self.vl.vlist:
				spots = []
				for i, pos in enumerate(self.vl.vlist[key]):
					if self.state['icp'] == self.MANUAL:
						spots.append({'pos':[pos[1],-pos[0]], 'data':1, 'size':15, 'symbol':str(i+1)})
					elif self.state['icp'] == self.AUTO:
						spots.append({'pos':[pos[1],-pos[0]], 'data':1, 'size':10, 'symbol':'o'})
				self.cells[key].scatter.addPoints(spots)
		else:
			self.clear_screen_point(id=id)
			spots = []
			for i, pos in enumerate(self.vl.vlist[id]):
				if self.state['icp'] == self.MANUAL:
					spots.append({'pos':[pos[1],-pos[0]], 'data':1, 'size':15, 'symbol':str(i+1)})
				elif self.state['icp'] == self.AUTO:
					spots.append({'pos':[pos[1],-pos[0]], 'data':1, 'size':10, 'symbol':'o'})
			self.cells[id].scatter.addPoints(spots)
		'''
		for key in self.vl.vlist:
			for i, pos in enumerate(self.vl.vlist[key]):
				if self.state['icp'] == self.MANUAL:
					self.draw_point(self.cells[key].image, pos, symbol=str(i+1))
				else:
					self.draw_point(self.cells[key].image, pos)
		'''

	def remove_point(self, xxxxx):
		## slot method for signal(removeVertexRequsted)
		pass

	def remove_point_pair(self, xxxxx):
		## slot method for signal(removeVertexPairRequsted)
		pass

	def save_points(self):
		print "save points"
		with open("./vertices.txt", "w") as outfile:
			outfile.write(str(self.vl.vlist[0]) + '\n')
			outfile.write(str(self.vl.vlist[1]))
			outfile.close()

	def auto_requested(self):
		## slot method for sigAutoRequested
		print "auto requested"
		self.state['icp'] = self.AUTO
		self.redraw_point()

	def manual_requested(self):
		## slot method for sigAutoRequested
		print "manual requested"
		self.state['icp'] = self.MANUAL
		self.redraw_point()

	def lock_clicked(self, (btn)):
		## slot method for ButtonItem.clicked
		print "lock clicked"
		for k in self.cells:
			if self.cells[k].button_area.buttons['lock'] == btn:
				if self.state['locked'][k] == True:
					self.cells[k].button_area.buttons['lock'].setOpacity(0.4)
					self.state['locked'][k] = False
					self.cells[k].v.setMouseEnabled(True, True)
				else:
					self.cells[k].button_area.buttons['lock'].setOpacity(1)
					self.state['locked'][k] = True
					self.cells[k].v.setMouseEnabled(False, False)

	def delete_clicked(self, (btn)):
		## slot method for ButtonItem.clicked
		print "delete clicked"
		for k in self.cells:
			if self.cells[k].button_area.buttons['del'] == btn:
				if self.state['delete'][k] == True:
					self.cells[k].button_area.buttons['del'].setOpacity(0.4)
					self.state['delete'][k] = False
				else:
					self.cells[k].button_area.buttons['del'].setOpacity(1)
					self.state['delete'][k] = True

	def delete_hover(self, (scatter, pts)):
		## slot method for ScatterPlotItem's hoverEvent
		for k in self.cells:
			if self.cells[k].scatter == scatter:
				if self.state['delete'][k] == False:
					return
				print pts
				for item in pts:
					item.setBrush(10,10,10)

	def delete_point_clicked(self, scatter, pts):
		## slot method for ScatterPlotItem's mouseClickEvent (sigClicked)
		## notice, corrdinate of ROI and scatter plot are different
		##									(x, y)  -->  (y, -x)
		for k in self.cells:
			if self.cells[k].scatter == scatter:
				if self.state['delete'][k] == False:
					return
				for item in pts:
					## use int may not be very robust, but size seems always > 1
					vdkey = (-int(item.pos().y()), int(item.pos().x()))
					for ind, pos in enumerate(self.vl.vlist[k]):
						if vdkey == (int(pos[0]), int(pos[1])):
							break
					self.vl.vlist[k].pop(ind)
				self.redraw_point(id=k)

	def shear_state_changed(self):
		## slot method for allow shear button
		if self.state['shear'] == True:
			self.state['shear'] = False
		else:
			self.state['shear'] = True

	def align_image_requested(self):
		## slot method for PushButton 'align image'
		## check point pair number
		print len(self.vl.vlist[0])
		print len(self.vl.vlist[1]) 
		if len(self.vl.vlist[0]) < 3 or len(self.vl.vlist[1]) < 3:
			print "no enough vertices"
			return
		## perform different algorithm based on icp state

		
		if self.state['icp'] == self.AUTO and self.state['shear'] == False:
			print "icp: auto"
			data = np.array(self.vl.vlist[0], dtype='f')
			model = np.array(self.vl.vlist[1], dtype='f')
			print "data: ", data
			print "model ", model
			maxd = np.max(pdist(data))
			maxm = np.max(pdist(model))
			guess_scale = maxm / maxd
			print "guess_scale = ", guess_scale
			step = 0.05
			min_error = 10e10
			m_trans_h = None
			m_scale = None
			m_rl = None
			m_tl = None
			
			for i in np.arange(max(guess_scale - 1, 0.1), guess_scale + 1.1, step):
				trans_h, error = align.basic_icp(data * i, model)
				if error < min_error:
					min_error = error
					m_trans_h = trans_h
					m_scale = i
					#m_s = s
			## trans_h is the transpose of the transformation matrix
			print m_trans_h
			print "min error = ", min_error
			print "scale = ", m_scale
			## compute angle: asin(sin(theta)), sin(theta) is at [0][1]
			angle = asin(m_trans_h[0][1]) / pi * 180
			tx = m_trans_h[2][0]
			ty = m_trans_h[2][1]
			print "angle = ", angle
			print tx, ty
			#print "m_s = ", m_s
			## the coordinate system is very odd...
			self.sigTransformRequested.emit((m_scale, angle, ty, -tx))
				

		elif self.state['icp'] == self.AUTO and self.state['shear'] == True:
			data = np.array(self.vl.vlist[0], dtype='f')
			model = np.array(self.vl.vlist[1], dtype='f')
			maxd = np.max(pdist(data))
			maxm = np.max(pdist(model))
			guess_scale = maxm / maxd
			step = 0.05
			min_error = 10e10
			m_data = None
			m_model = None
			m_scale = None

			for i in np.arange(max(guess_scale - 1, 0.1), guess_scale + 1.1, step):
				m, error = align.icp_neighbors(data * i, model)
				if error < min_error:
					min_error = error
					m_model = m
			p = []
			s = []
			for item in data:
				p.append([item[1], item[0]])
			for item in m_model:
				s.append([item[1], item[0]])
			data = np.array(p, dtype='f')
			model = np.array(s, dtype='f')
			print "min error = ", min_error
			print "data: ", data
			print "corresponding model:", model
			aft = align.compute_affine(data, model)
			print "affine matrix: ", aft
			self.sigAffineRequested.emit((aft))
		
		elif self.state['icp'] == self.MANUAL:
			print "icp : manual"
			if len(self.vl.vlist[0]) != len(self.vl.vlist[1]):
				print "point number need to be equal"
				return
			p = []
			s = []
			for item in self.vl.vlist[0]:
				p.append([item[1], item[0]])
			for item in self.vl.vlist[1]:
				s.append([item[1], item[0]])
			data = np.array(p, dtype='f')
			model = np.array(s, dtype='f')
			aft = align.compute_affine(data, model)
			print "affine matrix: ", aft
			self.sigAffineRequested.emit((aft))
			## use warp affine would make some part of the data image missing; how to improve?