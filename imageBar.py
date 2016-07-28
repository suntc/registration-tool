'''
Created on 2016-07-12
@author: Sun Tianchen
'''
import pyqtgraph as pg
from uiImageItem import UiImageItem
from PyQt4 import QtCore, QtGui

from load import ImageFileLoader

class VertexList(object):
	"""
	VertexList stores the vertex-pair of the 2 input images
	designed for performing image warping
	======================
	remove()
	remove_pair()
	"""
	def __init__(self):
		self.vlist = []
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
		self.vlist.append({id : [x, y]})
		#self.vlist[len(self.vlist)-1].setdefault(id ,[x, y])

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
		if index < 0 or index > count - 1:
			return False
		self.vlist.pop(index)
		return True

class InImageCell(object):
	def __init__(self, v, image, scatter, open_action=None):
		self.v = v
		self.image = image
		self.open_action = open_action
		self.scatter = scatter
		

class ImageBar(object):
	"""docstring for ImageBar"""
	def __init__(self, layout, images=None):
		self.w = layout
		self.images = images
		## file related
		self.loader = ImageFileLoader()
		self.default_path = "./"
		## module states
		self.IDLE = 0
		self.WAITFORIMAGE = 1
		self.ADDINGVERTEX = 2
		self.CLIPPING = 3
		self.state = self.WAITFORIMAGE
		self.cells = {}
		## max number of images can be loaded
		self.max_img = 2
		## create vertex list
		self.vl = VertexList()
		## create empty boxes to hold images
		for i in range(self.max_img):
			pass
			#v = self.w.addViewBox(row=i, col=0, lockAspect=True, enableMouse=False)
			#self.cells.setdefault(i, InImageCell(v, UiImageItem()))
		

		if images:
			for i, item in enumerate(images):
				v = self.w.addViewBox(row=i, col=0, lockAspect=True, enableMouse=True)
				img = UiImageItem()
				v.addItem(img)
				img.setImage(item)
				img.sigAddVertexRequested.connect(self.add_point)
				img.sigLoadImageRequested.connect(self.load_image_requested)
				## add scatter plot item
				scatter = pg.ScatterPlotItem(size=10, pen=pg.mkPen('w'), pxMode=True, brush=pg.intColor(100, 100))
				#spots = [{'pos': [1000,-1000], 'data': 1},{'pos': [1200,-600], 'data': 1}]
				#scatter.addPoints(spots)
				scatter.setZValue(10)
				v.addItem(scatter)
				self.cells.setdefault(i, InImageCell(v, img, scatter))
				
		self.set_menu()

		

	def set_menu(self):
		for k in self.cells:
			liAct = QtGui.QAction("Load Image", self.cells[k].v.menu)
			liAct.triggered.connect(self.cells[k].image.load_imgae_clicked)
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
				print fname
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
		self.cells[id].v.removeItem(self.cells[id].image)
		img = UiImageItem()
		self.cells[id].v.addItem(img)
		img.setImage(arr)
		## rotate the imageItem (oddly the image is rotated by default)
		img.setRotation(-90)
		self.cells[id].image = img
		## connect images signals to slot in class ImageBar
		img.sigAddVertexRequested.connect(self.add_point)
		img.sigLoadImageRequested.connect(self.load_image_requested)
		self.cells[id].open_action.triggered.connect(img.load_imgae_clicked)
		## clear existed points
		self.clear_point(id=id)

		if 0 in self.cells and 1 in self.cells: ## not so good
			self.state = self.IDLE

	def add_point(self, (image_item, pos)):
		## slot method for signal(addVertexRequsted)
		print "add point ", pos
		## need to transform the coordinate
		spots = [{'pos': [pos[1],-pos[0]], 'data': 1}]
		for k in self.cells:
			if self.cells[k].image == image_item:
				## add vertex to screen
				self.cells[k].scatter.addPoints(spots)
				## add vertex to vertex list
				self.vl.add_vertex(k, pos[0], pos[1])

	def clear_point(self, id=None):
		print "clear points"
		if id != None:
			self.cells[id].scatter.clear()
		else:
			for k in self.cells:
				self.cells[k].scatter.clear()

	def remove_point(self, xxxxx):
		## slot method for signal(removeVertexRequsted)
		pass

	def remove_point_pair(self, xxxxx):
		## slot method for signal(removeVertexPairRequsted)
		pass

	def save_points(self):
		print "save points"
		p1 = []
		p2 = []
		for item in self.vl.vlist:
			if 0 in item:
				p1.append(item[0])
			if 1 in item:
				p2.append(item[1])	
		with open("./vertices.txt", "w") as outfile:
			outfile.write(str(p1) + '\n')
			outfile.write(str(p2))
			outfile.close()

