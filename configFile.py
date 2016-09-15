'''
Created on 2016-08-15
@author: Sun Tianchen
'''
from PyQt4 import QtCore, QtGui
import pyqtgraph as pg
import pickle

class ConfigFile(QtCore.QObject):
	'''
	every file shares the same copy of ConfigFile object
	config file stores:
	1. original array of image
	2. points added
	3. curves added
	4. opencv transformation of photo
	5. image transformation (translation, rotation, size) of images
	6. heatmap of image
	7. 
	'''
	sigLoadConfig = QtCore.Signal(object)
	def __init__(self):
		QtCore.QObject.__init__(self)
		self.default_path = './'
		self.current_fname = None
		self.configs = {}
		self.configs['original_array'] = [None, None]
		self.configs['vl'] = None
		self.configs['contour'] = [None, None]
		self.configs['curves_params'] = [] ## [[track, tense, pen_param]]

	def write_config_file(self, fname):
		try:
			outfile = open(fname, "wb")
			print outfile
			pickle.dump(self.configs, outfile)
			#curves = self.configs['curves_params']
			#pickle.dump(curves, outfile)
			outfile.close()
		except Exception as e:
			print "save config error", e
			return

	def read_config_file(self, fname):
		try:
			infile = open(fname, "rb")
			self.configs = pickle.load(infile)
			infile.close()
		except Exception as e:
			print "read config error", e
			return

	def save_config(self):
		if self.current_fname == None:
			fname = pg.FileDialog.getSaveFileName(None, "Save project file", self.default_path)
			if fname == '' or fname == None:
				return
		else:
			fname = self.current_fname
		print "file name = ", fname
		self.write_config_file(fname)
		self.current_fname = fname

	def save_config_as(self):
		fname = pg.FileDialog.getSaveFileName(None, "Save project file", self.default_path)
		if fname == '' or fname == None:
			return
		print "file name = ", fname
		self.write_config_file(fname)
		self.current_fname = fname


	def load_config(self):
		fname = pg.FileDialog.getOpenFileName(None, "Load project file", self.default_path)
		if fname == '' or fname == None:
			return
		self.read_config_file(fname)
		print self.configs
		self.current_fname = fname
		self.sigLoadConfig.emit(fname)


