'''
Created on 2016-07-13
@author: Sun Tianchen
'''

from PIL import Image
import numpy as np

class ImageFileLoader(object):
	"""docstring for ImageFileLoader"""
	def __init__(self):
		pass
	
	def load(self, path):
		#im = Image.open(path)
		#im.show()
		#np.asarray(Image.open(path))
		return np.asarray(Image.open(path), dtype='f')
	
	def save(self, path, arr):
		pass