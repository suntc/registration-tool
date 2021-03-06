from PyQt4 import QtCore, QtGui
from pyqtgraph.widgets.TreeWidget import TreeWidget
from pyqtgraph.widgets.FeedbackButton import FeedbackButton

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Form(object):
    def __init__(self):
        self.btn_list = {}

    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(217, 499)
        Form.setMaximumWidth(217)
        self.gridLayout = QtGui.QGridLayout(Form)
        #self.gridLayout.setMargin(0)
        #self.gridLayout.setVerticalSpacing(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        ## buttons -- load/save/saveas
        self.loadBtn = QtGui.QPushButton(Form)
        self.loadBtn.setObjectName(_fromUtf8("loadBtn"))
        self.gridLayout.addWidget(self.loadBtn, 0, 0, 1, 1)
        self.saveBtn = FeedbackButton(Form)
        self.saveBtn.setObjectName(_fromUtf8("saveBtn"))
        self.gridLayout.addWidget(self.saveBtn, 0, 1, 1, 2)
        self.saveAsBtn = FeedbackButton(Form)
        self.saveAsBtn.setObjectName(_fromUtf8("saveAsBtn"))
        self.gridLayout.addWidget(self.saveAsBtn, 0, 3, 1, 1)
        ## auto manual switching
        self.autoLabel = QtGui.QLabel(Form)
        self.autoLabel.setObjectName(_fromUtf8("autoLabel"))
        #self.autoBtn = QtGui.QPushButton(Form)
        #self.autoBtn.setObjectName(_fromUtf8("autoBtn"))
        #self.autoBtn.setCheckable(True)
        ## use radio button instead
        self.autoRadio = QtGui.QRadioButton()
        self.manualLabel = QtGui.QLabel(Form)
        self.manualLabel.setObjectName(_fromUtf8("manualLabel"))
        #self.manualBtn = QtGui.QPushButton(Form)
        self.manualLabel.setObjectName(_fromUtf8("manualBtn"))
        #self.manualBtn.setCheckable(True)
        self.manualRadio = QtGui.QRadioButton()
        self.manualRadio.setChecked(True)
        ## by default manual is set
        #self.manualBtn.setChecked(True)
        '''
        self.shearLabel = QtGui.QLabel(Form)
        self.shearLabel.setObjectName(_fromUtf8("shearLabel"))
        self.shearCheck = QtGui.QCheckBox(Form)
        self.shearCheck.setObjectName(_fromUtf8("shearCheck"))
        self.shearCheck.setCheckable(False)
        '''
        ## register mode selection
        self.modeCombo = QtGui.QComboBox()
        self.modeCombo.addItem(_fromUtf8("Rigid"))
        self.modeCombo.addItem(_fromUtf8("Affine"))
        self.modeCombo.addItem(_fromUtf8("Projective"))
        self.modeCombo.addItem(_fromUtf8("Piecewise affine"))
        self.modeCombo.setCurrentIndex(1)
        self.gridLayout.addWidget(self.modeCombo, 4, 0, 1, 3)
        self.gridLayout.addWidget(self.autoLabel, 1, 0, 1, 3)
        #self.gridLayout.addWidget(self.autoBtn, 1, 3, 1, 1)
        self.gridLayout.addWidget(self.autoRadio, 1, 3, 1, 1)
        #self.gridLayout.addWidget(self.shearLabel, 2, 1, 1, 2)
        #self.gridLayout.addWidget(self.shearCheck, 2, 3, 1, 1)
        self.gridLayout.addWidget(self.manualLabel, 3, 0, 1, 3)
        #self.gridLayout.addWidget(self.manualBtn, 3, 3, 1, 1)
        self.gridLayout.addWidget(self.manualRadio, 3, 3, 1, 1)

        self.registrationBtn = QtGui.QPushButton('registrationBtn')
        self.gridLayout.addWidget(self.registrationBtn, 5, 1, 1, 2)
        #self.segLabel = QtGui.QLabel("-----")
        #self.gridLayout.addWidget(self.segLabel, 20, 0, 0, 3)
        ## button -- show/hide heatmap
        self.hmBtn = QtGui.QPushButton(Form)
        self.hmBtn.setEnabled(False)
        self.gridLayout.addWidget(self.hmBtn, 6, 0, 1, 2)
        ## tree widget
        self.hmTree = QtGui.QTreeWidget(Form)
        self.hmTree.setColumnCount(1)
        self.hmTree.setHeaderLabel("Channels")
        self.hmTree.setMaximumHeight(200)
        i1 = QtGui.QTreeWidgetItem(['Channel 1'])
        i2 = QtGui.QTreeWidgetItem(['Channel 2'])
        i3 = QtGui.QTreeWidgetItem(['Channel 3'])
        #self.hmTree.addTopLevelItem(i1)
        #self.hmTree.addTopLevelItem(i2)
        #self.hmTree.addTopLevelItem(i3)
        self.gridLayout.addWidget(self.hmTree, 7, 0, 1, 3)
        '''
        self.ctrlList = TreeWidget(Form)
        self.ctrlList.setObjectName(_fromUtf8("ctrlList"))
        self.ctrlList.headerItem().setText(0, _fromUtf8("1"))
        self.ctrlList.header().setVisible(False)
        self.ctrlList.header().setStretchLastSection(False)
        self.gridLayout.addWidget(self.ctrlList, 3, 0, 1, 4)
        '''
        self.fileNameLabel = QtGui.QLabel(Form)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.fileNameLabel.setFont(font)
        self.fileNameLabel.setText(_fromUtf8(""))
        self.fileNameLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.fileNameLabel.setObjectName(_fromUtf8("fileNameLabel"))
        #self.gridLayout.addWidget(self.fileNameLabel, 0, 1, 1, 1)

        ## button list
        self.btn_list.setdefault('auto', self.autoRadio)
        self.btn_list.setdefault('manual', self.manualRadio)
        self.btn_list.setdefault('reg', self.registrationBtn)
        self.btn_list.setdefault('heatmap', self.hmBtn)
        self.btn_list.setdefault('heatmapTree', self.hmTree)
        self.btn_list.setdefault('mode', self.modeCombo)
        ## dummy
        self.dummy = QtGui.QWidget()
        self.dummy.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        self.gridLayout.addWidget(self.dummy, 8, 0)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.loadBtn.setText(_translate("Form", "Load..", None))
        self.saveBtn.setText(_translate("Form", "Save", None))
        self.saveAsBtn.setText(_translate("Form", "As..", None))
        #self.reloadBtn.setText(_translate("Form", "Reload Libs", None))
        #self.showChartBtn.setText(_translate("Form", "Flowchart", None))
        self.autoLabel.setText(_translate("Form", "Auto Detect Correspondence", None))
        self.manualLabel.setText(_translate("Form", "Manully Set Correspondence", None))
        #self.autoBtn.setText(_translate("Form", "X", None))
        #self.manualBtn.setText(_translate("Form", "X", None))
        self.registrationBtn.setText(_translate("Form", "Align Image", None))
        #self.shearLabel.setText(_translate("Form", "Allow Shearing", None))
        self.hmBtn.setText(_translate("Form", "Load Heatmap", None))


"""
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(217, 499)
        self.gridLayout = QtGui.QGridLayout(Form)
        #self.gridLayout.setMargin(0)
        #self.gridLayout.setVerticalSpacing(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        ## buttons -- load/save/saveas
        self.loadBtn = QtGui.QPushButton(Form)
        self.loadBtn.setObjectName(_fromUtf8("loadBtn"))
        self.gridLayout.addWidget(self.loadBtn, 4, 0, 1, 1)
        self.saveBtn = FeedbackButton(Form)
        self.saveBtn.setObjectName(_fromUtf8("saveBtn"))
        self.gridLayout.addWidget(self.saveBtn, 4, 1, 1, 2)
        self.saveAsBtn = FeedbackButton(Form)
        self.saveAsBtn.setObjectName(_fromUtf8("saveAsBtn"))
        self.gridLayout.addWidget(self.saveAsBtn, 4, 3, 1, 1)
        '''
        self.reloadBtn = FeedbackButton(Form)
        self.reloadBtn.setCheckable(False)
        self.reloadBtn.setFlat(False)
        self.reloadBtn.setObjectName(_fromUtf8("reloadBtn"))
        self.gridLayout.addWidget(self.reloadBtn, 4, 0, 1, 2)
        self.showChartBtn = QtGui.QPushButton(Form)
        self.showChartBtn.setCheckable(True)
        self.showChartBtn.setObjectName(_fromUtf8("showChartBtn"))
        self.gridLayout.addWidget(self.showChartBtn, 4, 2, 1, 2)
        '''
        self.autoLabel = QtGui.QLabel(Form)
        self.autoLabel.setObjectName(_fromUtf8("autoLabel"))
        self.autoBtn = QtGui.QPushButton(Form)
        self.autoBtn.setObjectName(_fromUtf8("autoBtn"))
        self.autoBtn.setCheckable(True)
        self.btn_list.setdefault('auto', self.autoBtn)
        self.manualLabel = QtGui.QLabel(Form)
        self.manualLabel.setObjectName(_fromUtf8("manualLabel"))
        self.manualBtn = QtGui.QPushButton(Form)
        self.manualLabel.setObjectName(_fromUtf8("manualBtn"))
        self.manualBtn.setCheckable(True)
        ## by default manual is set
        self.manualBtn.setChecked(True)
        self.btn_list.setdefault('manual', self.manualBtn)
        self.shearLabel = QtGui.QLabel(Form)
        self.shearLabel.setObjectName(_fromUtf8("shearLabel"))
        self.shearCheck = QtGui.QCheckBox(Form)
        self.shearCheck.setObjectName(_fromUtf8("shearCheck"))
        self.shearCheck.setCheckable(False)
        self.gridLayout.addWidget(self.autoLabel, 7, 0, 1, 3)
        self.gridLayout.addWidget(self.autoBtn, 7, 3, 1, 1)
        self.gridLayout.addWidget(self.shearLabel, 10, 1, 1, 2)
        self.gridLayout.addWidget(self.shearCheck, 10, 3, 1, 1)
        self.gridLayout.addWidget(self.manualLabel, 13, 0, 1, 3)
        self.gridLayout.addWidget(self.manualBtn, 13, 3, 1, 1)
        self.registrationBtn = QtGui.QPushButton('registrationBtn')
        self.btn_list.setdefault('reg', self.registrationBtn)
        self.gridLayout.addWidget(self.registrationBtn, 16, 1, 1, 2)
        #self.segLabel = QtGui.QLabel("-----")
        #self.gridLayout.addWidget(self.segLabel, 20, 0, 0, 3)
        ## button -- show/hide heatmap
        self.hmBtn = QtGui.QPushButton(Form)
        self.hmBtn.setEnabled(False)
        self.gridLayout.addWidget(self.hmBtn, 17, 0, 1, 2)
        self.btn_list.setdefault('heatmap', self.hmBtn)
        
        '''
        self.ctrlList = TreeWidget(Form)
        self.ctrlList.setObjectName(_fromUtf8("ctrlList"))
        self.ctrlList.headerItem().setText(0, _fromUtf8("1"))
        self.ctrlList.header().setVisible(False)
        self.ctrlList.header().setStretchLastSection(False)
        self.gridLayout.addWidget(self.ctrlList, 3, 0, 1, 4)
        '''
        self.fileNameLabel = QtGui.QLabel(Form)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.fileNameLabel.setFont(font)
        self.fileNameLabel.setText(_fromUtf8(""))
        self.fileNameLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.fileNameLabel.setObjectName(_fromUtf8("fileNameLabel"))
        self.gridLayout.addWidget(self.fileNameLabel, 0, 1, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)
"""

    