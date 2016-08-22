'''
Created on 2016-08-11
@author: Sun Tianchen
'''

from PyQt4 import QtCore, QtGui

class ColorWidegt(QtGui.QWidget):
	"""docstring for ColorWidegt"""
	def __init__(self, parent=None):
		'''
		default values:
		Pen:
		Size:
		Tense:
		'''
		QtGui.QWidget.__init__(self, parent=parent)
		self.buttons = {}
		self.gridLayout = QtGui.QGridLayout(self)
		self.cd = QtGui.QColorDialog()
		self.cd.setWindowFlags(QtCore.Qt.Widget)
		self.cd.setOptions(QtGui.QColorDialog.DontUseNativeDialog)
		self.cd.setOptions(QtGui.QColorDialog.NoButtons)
		self.gridLayout.addWidget(self.cd)
		self.hblayout = QtGui.QHBoxLayout()
		self.hblayout2 = QtGui.QHBoxLayout()
		self.hblayout3 = QtGui.QHBoxLayout()
		## slider
		self.psSl = QtGui.QSlider(QtCore.Qt.Horizontal)
		self.psSl.setMinimum(1)
		self.psSl.setMaximum(30)
		self.psSl.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
		self.psLabel = QtGui.QLabel("Pen size")
		self.psText = QtGui.QLineEdit()
		self.psText.setValidator(QtGui.QIntValidator(1, 30, self.psText))
		self.psText.setMaximumWidth(30)
		self.psText.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
		self.psText.setText(str(self.psSl.value()))
		self.pxLabel = QtGui.QLabel("px")
		self.hblayout.addWidget(self.psLabel)
		self.hblayout.addWidget(self.psSl)
		self.hblayout.addWidget(self.psText)
		self.hblayout.addWidget(self.psLabel)
		#self.hblayout.addWidget(self.pxLabel)
		self.gridLayout.addLayout(self.hblayout, 1, 0, QtCore.Qt.AlignLeft)
		## slider 2
		self.tsSl = QtGui.QSlider(QtCore.Qt.Horizontal)
		self.tsSl.setMinimum(30)
		self.tsSl.setMaximum(70)
		self.tsSl.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
		self.tsLabel = QtGui.QLabel("Tense")
		self.tsText = QtGui.QLineEdit()
		self.tsText.setValidator(QtGui.QDoubleValidator(0.3, 0.7, 2, self.tsText))
		self.tsText.setMaximumWidth(30)
		self.tsText.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
		self.tsText.setText(str(self.tsSl.value()))
		self.hblayout.addWidget(self.tsLabel)
		self.hblayout.addWidget(self.tsSl)
		self.hblayout.addWidget(self.tsText)
		self.gridLayout.addLayout(self.hblayout2, 2, 0, QtCore.Qt.AlignLeft)
		## buttons
		self.okBtn = QtGui.QPushButton("OK")
		self.cancelBtn = QtGui.QPushButton("Cancel")
		self.okBtn.setMaximumWidth(50)
		self.cancelBtn.setMaximumWidth(50)
		self.hblayout3.addWidget(self.okBtn)
		self.hblayout3.addWidget(self.cancelBtn)
		self.gridLayout.addLayout(self.hblayout3, 3, 0)
		#self.setFixedSize(self.size())
		## set up dict
		self.buttons['cancel'] = self.cancelBtn
		self.buttons['ok'] = self.okBtn
		self.buttons['color'] = self.cd
		self.buttons['size'] = self.psSl
		self.buttons['tense'] = self.tsSl
		## connect signal and slots
		self.psText.textEdited.connect(self.ps_line_text_changed)
		self.psSl.valueChanged.connect(self.ps_bar_changed)
		self.tsText.textEdited.connect(self.ts_line_text_changed)
		self.tsSl.valueChanged.connect(self.ts_bar_changed)

		## store current value
		self.cur_color = QtGui.QColor(79,106,25)
		self.cur_tense = 0.4
		self.cur_size = 10

		self.restore_value()

	def ok_clicked(self):
		pass

	def cancel_click(self):
		pass

	def ps_bar_changed(self, value):
		self.psText.setText(str(value))

	def ps_line_text_changed(self):
		if len(self.psText.text()) > 0:
			self.psSl.setValue(int(self.psText.text()))

	def ts_bar_changed(self, value):
		self.tsText.setText(str(value/100.))

	def ts_line_text_changed(self):
		if len(self.tsText.text()) > 0:
			self.tsSl.setValue(int(float(self.tsText.text()) * 100))

	def set_cur_value(self):
		self.cur_color = self.buttons['color'].currentColor()
		self.cur_size = self.buttons['size'].value()
		self.cur_tense = self.buttons['tense'].value() / 100.

	def restore_value(self):
		## color -- color Dialog
		## size -- psSl, psText
		## tense -- tsSl, tsText
		self.cd.setCurrentColor(self.cur_color)
		self.psSl.setValue(self.cur_size)
		self.psText.setText(str(self.cur_size))
		self.tsSl.setValue(100 * self.cur_tense)
		self.tsText.setText(str(self.cur_tense))

app = QtGui.QApplication([])
'''
win = QtGui.QMainWindow()
win.setWindowTitle('pyqtgraph example')
cw = ColorWidegt()
cd = QtGui.QColorDialog()
cd.setOptions(QtGui.QColorDialog.DontUseNativeDialog)
cd.setOptions(QtGui.QColorDialog.NoButtons)
win.setCentralWidget(cd)
layout = QtGui.QGridLayout()
win.show()
'''
#cw = ColorWidegt()
#cw.show()

if __name__ == '__main__':
	import sys
	if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
		QtGui.QApplication.instance().exec_()