from PyQt4 import QtGui, QtCore
from twisted.internet.defer import inlineCallbacks

class ExperimentGrid(QtGui.QWidget):
    def __init__(self, parent, experiment):
        QtGui.QWidget.__init__(self)
        self.parent = parent
        self.experiment = experiment
        self.parent.setWindowTitle(self.experiment)
        self.setupExperimentGrid()

    @inlineCallbacks
    def setupExperimentGrid(self):
        self.experimentGrid = QtGui.QGridLayout()
        self.experimentGrid.setSpacing(5)
        
        self.doubleSpinBoxParameterDict = {}
        self.parameterDoubleSpinBoxDict = {}
        
        expParamNames = yield self.parent.server.get_experiment_parameter_names(self.experiment)
        
        gridRow = 0
        gridCol = 0
        for parameter in expParamNames:
            # create a label and spin box, add it to the grid
            value = yield self.parent.server.get_experiment_parameter(self.experiment, parameter)
            label = QtGui.QLabel(parameter)
            doubleSpinBox = QtGui.QDoubleSpinBox()
            doubleSpinBox.setRange(value[0], value[1])
            doubleSpinBox.setValue(value[2])
            doubleSpinBox.setSingleStep(.1)
            doubleSpinBox.setKeyboardTracking(False)
            self.connect(doubleSpinBox, QtCore.SIGNAL('valueChanged(double)'), self.updateValueToSemaphore)
            
            self.doubleSpinBoxParameterDict[doubleSpinBox] = parameter
            self.parameterDoubleSpinBoxDict[parameter] = doubleSpinBox 
            
            self.experimentGrid.addWidget(label, gridRow, gridCol, QtCore.Qt.AlignCenter)
            self.experimentGrid.addWidget(doubleSpinBox, gridRow, gridCol + 1, QtCore.Qt.AlignCenter)
            
            gridCol += 2
            if (gridCol == 6):
                gridCol = 0
                gridRow += 1
        
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.setLayout(self.experimentGrid)    
    
    @inlineCallbacks
    def updateValueToSemaphore(self, parameterValue):
        yield self.parent.server.set_experiment_parameter(self.experiment, self.doubleSpinBoxParameterDict[self.sender()], [self.sender().minimum(), self.sender().maximum(), parameterValue])
