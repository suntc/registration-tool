'''
Created on 2016-07-27
@author: Sun Tianchen
'''

from PyQt4 import QtCore, QtGui
import pyqtgraph as pg
import controlTemplate

class ControlWidget(QtGui.QWidget):
	"""docstring for ControlWidget"""

	sigAutoRequested = QtCore.Signal(object)
	sigManualRequested = QtCore.Signal(object)
	sigFileLoaded = QtCore.Signal(object)
	sigFileSaved = QtCore.Signal(object)
	sigHeatmapRequested = QtCore.Signal(object)
	sigModeChanged = QtCore.Signal(object)

	def __init__(self):
		QtGui.QWidget.__init__(self)
		## file name as a project
		self.currentFileName = None
		self.filePath = None
		## set up ui from template
		self.ui = controlTemplate.Ui_Form()
		self.ui.setupUi(self)
		'''
		self.ui.ctrlList.setColumnCount(2)
		#self.ui.ctrlList.setColumnWidth(0, 200)
		self.ui.ctrlList.setColumnWidth(1, 20)
		self.ui.ctrlList.setVerticalScrollMode(self.ui.ctrlList.ScrollPerPixel)
		self.ui.ctrlList.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
		'''
		## manage custom buttons
		'''
		## add custom buttons
		item = QtGui.QTreeWidgetItem(['Manually set correspondence', '', ''])
		self.ui.ctrlList.addTopLevelItem(item)
		byp = QtGui.QPushButton('X')
		byp.setCheckable(True)
		byp.setFixedWidth(20)
		item.bypassBtn = byp
		self.ui.ctrlList.setItemWidget(item, 1, byp)
		byp.clicked.connect(self.manualClicked)
		self.btn_list.setdefault('manual', byp)

		item = QtGui.QTreeWidgetItem(['Auto detect correspondence', '', ''])
		self.ui.ctrlList.addTopLevelItem(item)
		byp = QtGui.QPushButton('X')
		byp.setCheckable(True)
		byp.setFixedWidth(20)
		item.bypassBtn = byp
		self.ui.ctrlList.setItemWidget(item, 1, byp)
		byp.clicked.connect(self.autoClicked)
		self.btn_list.setdefault('auto', byp)
		'''
		## connect buttons with slot methods
		#self.ui.ctrlList.itemChanged.connect(self.itemChanged)
		#self.ui.btn_list['auto'].clicked.connect(self.autoClicked)
		#self.ui.btn_list['manual'].clicked.connect(self.manualClicked)
		self.ui.btn_list['auto'].toggled.connect(self.autoClicked)
		self.ui.btn_list['manual'].toggled.connect(self.manualClicked)
		self.ui.loadBtn.clicked.connect(self.loadClicked)
		self.ui.saveBtn.clicked.connect(self.saveClicked)
		self.ui.saveAsBtn.clicked.connect(self.saveAsClicked)
		self.ui.btn_list['heatmap'].clicked.connect(self.heatmapClicked)
		self.ui.btn_list['mode'].currentIndexChanged.connect(self.modeChanged)


	def manualClicked(self):
		#self.ui.btn_list['manual'].setChecked(True)
		#self.ui.btn_list['auto'].setChecked(False)
		#self.ui.shearCheck.setChecked(False)
		#self.ui.shearCheck.setCheckable(False)
		if self.ui.btn_list['manual'].isChecked():
			self.sigManualRequested.emit(self)

	def autoClicked(self):
		#self.ui.btn_list['auto'].setChecked(True)
		#self.ui.btn_list['manual'].setChecked(False)
		#self.ui.shearCheck.setCheckable(True)
		#self.ui.shearCheck.setChecked(True)
		if self.ui.btn_list['auto'].isChecked():
			self.sigAutoRequested.emit(self)

	def loadClicked(self):
		newFile = self.loadFile()
		#self.setCurrentFile(newFile)

	def saveClicked(self):
		if self.currentFileName is None:
			self.saveAsClicked()
		else:
			try:
				self.saveFile(self.currentFileName)
				#self.ui.saveBtn.success("Saved.")
			except:
				self.ui.saveBtn.failure("Error")
				raise

	def saveAsClicked(self):
		try:
			if self.currentFileName is None:
				newFile = self.saveFile()
			else:
				newFile = self.saveFile(suggestedFileName=self.currentFileName)
			#self.ui.saveAsBtn.success("Saved.")
			#print "Back to saveAsClicked."
		except:
			self.ui.saveBtn.failure("Error")
			raise

	def heatmapClicked(self):
		self.sigHeatmapRequested.emit(self)

	def loadFile(self, fileName=None, startDir=None):
		if fileName is None:
			if startDir is None:
				startDir = self.filePath
			if startDir is None:
				startDir = '.'
			self.fileDialog = pg.FileDialog(None, "Load Project..", startDir, "Project File (*.fc)")
			#self.fileDialog.setFileMode(QtGui.QFileDialog.AnyFile)
			#self.fileDialog.setAcceptMode(QtGui.QFileDialog.AcceptSave) 
			self.fileDialog.show()
			self.fileDialog.fileSelected.connect(self.loadFile)
			return
			## NOTE: was previously using a real widget for the file dialog's parent, but this caused weird mouse event bugs..
			#fileName = QtGui.QFileDialog.getOpenFileName(None, "Load Flowchart..", startDir, "Flowchart (*.fc)")
		fileName = unicode(fileName)
		state = configfile.readConfigFile(fileName)
		self.restoreState(state, clear=True)
		self.viewBox.autoRange()
		#self.emit(QtCore.SIGNAL('fileLoaded'), fileName)
		self.sigFileLoaded.emit(fileName)
		
	def saveFile(self, fileName=None, startDir=None, suggestedFileName='flowchart.fc'):
		if fileName is None:
			if startDir is None:
				startDir = self.filePath
			if startDir is None:
				startDir = '.'
			self.fileDialog = pg.FileDialog(None, "Save Project..", startDir, "Project File (*.mi)")
			#self.fileDialog.setFileMode(QtGui.QFileDialog.AnyFile)
			self.fileDialog.setAcceptMode(QtGui.QFileDialog.AcceptSave) 
			#self.fileDialog.setDirectory(startDir)
			self.fileDialog.show()
			self.fileDialog.fileSelected.connect(self.saveFile)
			return
			#fileName = QtGui.QFileDialog.getSaveFileName(None, "Save Flowchart..", startDir, "Flowchart (*.fc)")
		fileName = unicode(fileName)
		configfile.writeConfigFile(self.saveState(), fileName)
		self.sigFileSaved.emit(fileName)

	def saveState(self):
		state = Node.saveState(self)
		state['nodes'] = []
		state['connects'] = []
		#state['terminals'] = self.saveTerminals()
		
		for name, node in self._nodes.items():
			cls = type(node)
			if hasattr(cls, 'nodeName'):
				clsName = cls.nodeName
				pos = node.graphicsItem().pos()
				ns = {'class': clsName, 'name': name, 'pos': (pos.x(), pos.y()), 'state': node.saveState()}
				state['nodes'].append(ns)
			
		conn = self.listConnections()
		for a, b in conn:
			state['connects'].append((a.node().name(), a.name(), b.node().name(), b.name()))
		
		state['inputNode'] = self.inputNode.saveState()
		state['outputNode'] = self.outputNode.saveState()
		
		return state

	def modeChanged(self):
		self.sigModeChanged.emit(str(self.ui.btn_list['mode'].currentText()))

	def heatmap_button_enabled(self):
		## slot
		self.ui.btn_list['heatmap'].setEnabled(True)

	def heatmap_loaded(self, keys):
		## slot for imagePanel's sigHeatmapLoaded
		for k in keys:
			itm = QtGui.QTreeWidgetItem([k])
			self.ui.btn_list['heatmapTree'].addTopLevelItem(itm)

	def clear_heatmap_tree(self, (id, arr)):
		## slot method for imageBar's sigImageLoaded
		if id == 0:
			self.ui.btn_list['heatmapTree'].clear()

'''
app = QtGui.QApplication([])
win = QtGui.QMainWindow()
win.setWindowTitle('pyqtgraph example')
cw = ControlWidget()
win.setCentralWidget(cw)
layout = QtGui.QGridLayout()
#cw.setLayout(layout)

win.show()
'''

if __name__ == '__main__':
	import sys
	if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
		QtGui.QApplication.instance().exec_()