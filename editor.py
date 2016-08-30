'''
Created on 2016-07-10
@author: Sun Tianchen
'''

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np

from imagePanel import ImagePanel
from imageBar import ImageBar
from controlWidget import ControlWidget

## create GUI
#app = QtGui.QApplication([])
w = pg.GraphicsWindow(size=(1200,800), border=True)

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
w0 = w.addLayout(row=0,col=1)
#imbar = ImageBar(w0, [arr, arr])
imbar = ImageBar(w0, path=['./load_specimen.png', './load_histo.png'])

## image panel
w1 = w.addLayout(row=0, col=2)
#impanel = ImagePanel(w1, [arr, arr, arr, arr, arr])
impanel = ImagePanel(w1)

## create  control widget
cwid = ControlWidget()

## connect signal
imbar.sigImageLoaded.connect(impanel.image_loaded)
imbar.sigImageLoaded.connect(cwid.clear_heatmap_tree)
cwid.sigAutoRequested.connect(imbar.auto_requested)
cwid.sigManualRequested.connect(imbar.manual_requested)
cwid.sigModeChanged.connect(imbar.mode_changed)
cwid.ui.btn_list['reg'].clicked.connect(imbar.align_image_requested)
cwid.ui.btn_list['heatmap'].clicked.connect(impanel.heatmap_requested)
cwid.ui.btn_list['heatmapTree'].itemActivated.connect(impanel.heatmap_changed)
impanel.sigHeatmapLoaded.connect(cwid.heatmap_loaded)
#cwid.ui.shearCheck.stateChanged.connect(imbar.shear_state_changed)
imbar.sigCurveChanged.connect(impanel.curve_changed)
imbar.registrator.sigTransformRequested.connect(impanel.transform_requested)
imbar.registrator.sigAffineRequested.connect(impanel.affine_requested)
imbar.registrator.sigPiecewiseRequested.connect(impanel.piecewise_requested)
imbar.sigEnableHeatmapButton.connect(cwid.heatmap_button_enabled)
## manage layout
win = QtGui.QMainWindow()
win.setWindowTitle('Image Editor')
cw = pg.LayoutWidget()
win.setCentralWidget(cw)
cw.addWidget(cwid)
cw.addWidget(w)

win.show()

if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()