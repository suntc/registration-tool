'''
Created on 2016-07-13
@author: Sun Tianchen
'''

from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib import cm
import scipy.io
import cv2

class ImageFileLoader(object):
	"""docstring for ImageFileLoader"""
	def __init__(self):
		pass
	
	def load(self, path, dtype=None):
		#im = Image.open(path)
		#im.show()
		#arr = np.asarray(Image.open(path))
		#cv2.imshow('img', arr)
		if dtype == 'f':
			return np.asarray(Image.open(path), dtype='f')
		else:
			arr = np.asarray(Image.open(path))
			arr.setflags(write=True)
			if len(arr.shape) == 3 and arr.shape[2] == 3:
				arr = np.insert(arr,3,255,axis=2)
			return arr

	def save(self, path, arr):
		pass

	def mat_to_array(self, path):
		mat = scipy.io.loadmat(path)
		arr_dict = {}
		jet = plt.get_cmap('jet')
		jet.set_under(color='k', alpha=0)
		jet.set_over(color='k', alpha=0)
		for key in mat:
			if key not in ['__header__', '__globals__', '__version__']:
				arr_dict[key] = mat[key]
		for key in arr_dict:
			arr_dict[key] = np.where(np.isnan(arr_dict[key]), -1, arr_dict[key])
			cnorm = colors.Normalize(vmin=0.01,vmax=max(0.01,np.max(arr_dict[key])))
			scalarmap = cm.ScalarMappable(norm=cnorm, cmap=jet)
			arr = scalarmap.to_rgba(arr_dict[key])
			arr = arr * 255
			arr = np.array(arr, dtype='i')
			im = Image.fromarray(np.uint8(arr))
			arr_dict[key] = np.asarray(im)
			#arr_dict[key] = arr
		return arr_dict