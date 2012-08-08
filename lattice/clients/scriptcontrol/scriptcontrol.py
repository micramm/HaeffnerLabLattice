import time
from twisted.internet.defer import inlineCallbacks
from twisted.internet.threads import deferToThread
from PyQt4 import QtGui, QtCore
from experimentlist import ExperimentListWidget
from experimentgrid import ExperimentGrid
from globalgrid import GlobalGrid
from parameterlimitswindow import ParameterLimitsWindow


class ScriptControl(QtGui.QWidget):
    def __init__(self,reactor, parent=None):
        QtGui.QWidget.__init__(self)
        self.reactor = reactor
        self.experiments = ['Test', 'Test2']
        self.connect()
        
    @inlineCallbacks
    def connect(self):
        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync()
        self.server = self.cxn.semaphore
        self.server.initialize_experiments(self.experiments)
        self.setupMainWidget()
        
    @inlineCallbacks
    def setupMainWidget(self):
        self.mainLayout = QtGui.QHBoxLayout()
        # mainGrid is in mainLayout that way its size can be controlled.
        self.mainGrid = QtGui.QGridLayout()
        self.mainGrid.setSpacing(5)
        
        self.mainLayout.addLayout(self.mainGrid)
        
        self.experimentListWidget = ExperimentListWidget(self)
        self.experimentListWidget.show()
        self.mainGrid.addWidget(self.experimentListWidget, 0, 0, QtCore.Qt.AlignCenter)
        
        # not this again!
        yield deferToThread(time.sleep, .05)
        self.setupExperimentGrid(self.experiments[0])
       
        parameterLimitsButton = QtGui.QPushButton("Parameter Limits", self)
        parameterLimitsButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        parameterLimitsButton.clicked.connect(self.parameterLimitsWindowEvent)
        self.mainGrid.addWidget(parameterLimitsButton, 1, 1, QtCore.Qt.AlignRight)
        
        self.setupGlobalGrid()

        self.setLayout(self.mainLayout)
        self.show()


    def parameterLimitsWindowEvent(self, evt):
        experiment = self.experimentGrid.experiment
        try:
            self.parameterLimitsWindow.hide()
            del self.parameterLimitsWindow
            self.parameterLimitsWindow = ParameterLimitsWindow(self, experiment)
            self.parameterLimitsWindow.show()
        except:
            # first time
            self.parameterLimitsWindow = ParameterLimitsWindow(self, experiment)
            self.parameterLimitsWindow.show()

    def setupExperimentGrid(self, experiment):
        try:
            self.experimentGrid.hide()
        except:
            # First time
            pass
        self.experimentGrid = ExperimentGrid(self, experiment)           
        self.mainGrid.addWidget(self.experimentGrid, 0, 2, QtCore.Qt.AlignCenter)
        self.experimentGrid.show()  

    def setupGlobalGrid(self):
        self.globalGrid = GlobalGrid(self)           
        self.mainGrid.addWidget(self.globalGrid, 0, 3, QtCore.Qt.AlignCenter)
        self.globalGrid.show()          

    @inlineCallbacks
    def saveParametersToRegistryAndQuit(self):
        success = yield self.server.save_parameters_to_registry()
        if (success == True):
            print 'Current Parameters Saved Successfully.'
        self.reactor.stop()
                
    def closeEvent(self, x):
        self.saveParametersToRegistryAndQuit()

if __name__=="__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    scriptControl = ScriptControl(reactor)
    reactor.run()

