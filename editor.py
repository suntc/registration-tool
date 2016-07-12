'''
Created on 2016-07-10
@author: Sun Tianchen
'''

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np

from imagePanel import ImagePanel
from imageBar import ImageBar

## create GUI
app = QtGui.QApplication([])
w = pg.GraphicsWindow(size=(1200,800), border=True)
w.setWindowTitle('simple editor')

## Create image to display
arr = np.ones((100, 100), dtype=float)
arr[45:55, 45:55] = 0
arr[25, :] = 5
arr[:, 25] = 5
arr[75, :] = 5
arr[:, 75] = 5
arr[50, :] = 10
arr[:, 50] = 10
arr += np.sin(np.linspace(0, 20, 100)).reshape(1, 100)
arr += np.random.normal(size=(100,100))

## load image
w0 = w.addLayout(row=0,col=0)
imbar = ImageBar(w0, [arr, arr, arr])

## image panel
w1 = w.addLayout(row=0, col=1)
impanel = ImagePanel(w1, [arr, arr, arr, arr, arr])


if __name__ == '__main__':
	import sys

	if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
		QtGui.QApplication.instance().exec_()