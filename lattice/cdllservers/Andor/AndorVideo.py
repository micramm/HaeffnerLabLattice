#import numpy as np
#import time
#from PyQt4 import QtGui, QtCore
#
#from twisted.internet.defer import inlineCallbacks, returnValue
#from twisted.internet.threads import deferToThread
#
#import matplotlib
#matplotlib.use('Qt4Agg')
#from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
#from matplotlib.figure import Figure
#from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
#
#class Qt4MplCanvas(FigureCanvas):
#    def __init__(self, camera):
#
#        self.fig = Figure()
#
#        FigureCanvas.__init__(self, self.fig)
#        #self.fig, self.ax = plt.subplots()
#
#        self.ax = self.fig.add_subplot(111)
#        self.ax.axis([0, 658, 0, 496])
#        self.ax.set_aspect(1.0)
#        self.ax.autoscale(False)
#        newdata = np.ones(658*496)
#        newarray = np.reshape(newdata, (496, 658))
#        self.im = self.ax.matshow(newarray)
#              
#    def update(self, event):
#        print 'redrawn?'
#        self.im.set_data(camera.data)
#        self.im.axes.figure.canvas.draw()
#        
#class VideoWindow(QtGui.QWidget):
#    def __init__(self, camera):
#        QtGui.QWidget.__init__(self)
#        layout = QtGui.QVBoxLayout()
#    
#        self.qmc = Qt4MplCanvas(camera)
#        # instantiate the navigation toolbar
#        ntb = NavigationToolbar(self.qmc, self)
#        
#        Button = QtGui.QPushButton("Update", self)
#        Button.setGeometry(QtCore.QRect(0, 0, 30, 30))
#        Button.clicked.connect(self.qmc.update)        
#    
#        # Layout that involves the canvas, toolbar, graph options...etc.
#        layout.addWidget(ntb)
#        layout.addWidget(self.qmc)
#        layout.addWidget(Button)
#        
#        self.setLayout(layout)
#
#class AndorClient():
#    def __init__(self, reactor):
#        self.reactor = reactor
#        #self.connect()
#
#    @inlineCallbacks
#    def connect(self):
#        from labrad.wrappers import connectAsync
#        from labrad.types import Error
#        self.cxn = yield connectAsync()
#        try:
#            self.server = yield self.cxn.andor_server
#            self.setupCamera()
#        except Exception ,e:
#            print 'server not connected: {}'.format(e)
#
#    @inlineCallbacks
#    def setupCamera(self):
#        temp = yield self.server.get_current_temperature()
#        print temp
#
#        yield self.server.set_trigger_mode(0)
#        yield self.server.set_read_mode(4)
#
#        yield self.server.set_emccd_gain(255)
#        yield self.server.set_exposure_time(.3)      
#        yield self.server.cooler_on()
#        
#        
#        imageRegion = yield self.server.get_image_region()
#        self.width = imageRegion[3]
#        self.height = imageRegion[5]
#        
#        print 'width: ', self.width
#        print 'height: ', self.height
#        
#        error = yield self.server.set_image_region(1,1,1,self.width,1,self.height)
#        print 'image error: ', error
#        
#        self.liveVideo()
#
#    @inlineCallbacks
#    def liveVideo(self):
#        
#        time.sleep(5)
#        
#        width = self.width
#        height = self.height
#             
##        newdata = np.zeros(width*height)
##        newarray = np.reshape(newdata, (height, width))
#        
#
#        print "Ready for Acquisition..."
#        
#        status = yield self.server.get_status()
#        if (status == 'DRV_IDLE'):
#            yield self.server.set_acquisition_mode(5)
#            yield self.server.start_acquisition()
#            for i in range(10):
#                print i
#                data = yield self.server.get_most_recent_image()
#                newdata = data.asarray
#                print newdata.shape
#                self.data = newdata
#                newarray = np.reshape(newdata, (height, width))
#                print newarray[0, 4:7]
#                self.data = newarray
#            yield self.server.abort_acquisition()
#
#        
#if __name__ == "__main__":
#    a = QtGui.QApplication( [] )
#    import qt4reactor
#    qt4reactor.install()
#    from twisted.internet import reactor
#    Camera = AndorClient(reactor)
#    videoWindow = VideoWindow(Camera)
#    videoWindow.show()
#    reactor.run()










import sys
from PyQt4 import QtGui, QtCore
from matplotlib.figure import Figure
import time

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.threads import deferToThread



import matplotlib.pyplot as plt 
import numpy as np

class CPUMonitor(FigureCanvas):
    """Matplotlib Figure widget to display CPU utilization"""
    def __init__(self, parent):

        self.parent = parent
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        FigureCanvas.__init__(self, self.fig)

        #self.X = np.random.rand(5,5)
        #rows,cols,self.slices = self.X.shape
        #self.Y = np.random.rand(5,5)
        #rows,cols,self.slices = self.X.shape
        
        newdata = np.ones(2*2)
        newarray = np.reshape(newdata, (2, 2))
        self.data = newarray

        
        #self.im = self.ax.matshow(self.X[:,:])
        #self.im = self.ax.matshow(self.data)
        self.update()
        
        self.fig.canvas.draw()

        self.cnt = 0
        # call the update method (to speed-up visualization)
        #self.timerEvent(None)
        # start timer, trigger event every 1000 millisecs (=1sec)
        #self.timer = self.startTimer(500)

    def startYourEngines(self):
        self.timer = self.startTimer(50)
    
    def timerEvent(self, evt):
#        if (self.cnt == 12):
#            self.im = self.ax.matshow(self.data)
#            
#        
##        if (self.cnt == 0):
##            self.cnt = 1
##            self.im.set_data(self.X)
##        elif (self.cnt == 1):
##            self.im.set_data(self.Y)
##            self.cnt = 0    
#        elif (self.cnt > 12):    
#            self.im.set_data(self.data)            
#            #print self.data[0, 4:10]
#            
#            self.im.axes.figure.canvas.draw()
        try: 
            self.im.set_data(self.data)
            self.im.axes.figure.canvas.draw()
        except AttributeError:
            self.im = self.ax.matshow(self.data)
            self.im.axes.figure.canvas.draw()
        
        self.cnt += 1
        
    def updateData(self, data, width, height):
        self.data = np.reshape(data, (height, width))
        try: 
            self.im.set_data(self.data)
            self.im.axes.figure.canvas.draw()
        except AttributeError:
            self.im = self.ax.matshow(self.data)
            self.im.axes.figure.canvas.draw()
            print 'show yourself!'
        
        
class AppWindow(QtGui.QWidget):
    """Creates the window for the new plot"""
    def __init__(self, parent):
        QtGui.QWidget.__init__(self)
        
        self.parent = parent
        
        self.cmon = CPUMonitor(self)
        self.cmon.show()
        # instantiate the navigation toolbar
        ntb = NavigationToolbar(self.cmon, self)
        
        layout = QtGui.QVBoxLayout()

        # Layout that involves the canvas, toolbar, graph options...etc.
        layout.addWidget(ntb)
        layout.addWidget(self.cmon)
        
        
        temperatureButton = QtGui.QPushButton("Temp", self)
        temperatureButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        temperatureButton.clicked.connect(self.printTemperature)     
        
        liveVideoButton = QtGui.QPushButton("Live", self)
        liveVideoButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        liveVideoButton.clicked.connect(self.liveVideo)
        
        singleButton = QtGui.QPushButton("Single", self)
        singleButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        singleButton.clicked.connect(self.singleScan)
        
        abortButton = QtGui.QPushButton("Abort Video", self)
        abortButton.setGeometry(QtCore.QRect(0, 0, 30, 30))
        abortButton.clicked.connect(self.abortVideo)        
        
         # Layout
        self.buttonBox = QtGui.QHBoxLayout()
        
        self.buttonBox.addWidget(temperatureButton)
        self.buttonBox.addWidget(liveVideoButton)
        self.buttonBox.addWidget(singleButton)
        self.buttonBox.addWidget(abortButton)
    
        self.buttonBox.addStretch(0)
        self.buttonBox.setSizeConstraint(QtGui.QLayout.SetFixedSize)        
        layout.addLayout(self.buttonBox)
        
        self.setLayout(layout)

    def abortVideo(self, evt):
        self.parent.abortVideo()

    def printTemperature(self, evt):
        self.parent.printTemperature()
    
    def singleScan(self, evt):
        self.parent.singleScan()
    
    def liveVideo(self, evt):
        self.parent.liveVideo()
    
    def closeEvent(self, evt):
        try:
            self.killTimer(self.cmon.timer)
        except AttributeError:
            pass            

class AndorClient():
    def __init__(self, reactor):
        self.reactor = reactor
        self.live = True
        self.openVideoWindow()
        self.connect()

    def openVideoWindow(self):
        self.win = AppWindow(self)
        self.win.show()

    @inlineCallbacks
    def connect(self):
        from labrad.wrappers import connectAsync
        from labrad.types import Error
        self.cxn = yield connectAsync()
        try:
            self.server = yield self.cxn.andor_server
            self.setupCamera()
        except Exception ,e:
            print 'server not connected: {}'.format(e)

    @inlineCallbacks
    def setupCamera(self):
        temp = yield self.server.get_current_temperature()
        print temp

        yield self.server.set_trigger_mode(0)
        yield self.server.set_read_mode(4)

        yield self.server.set_emccd_gain(255)
        yield self.server.set_exposure_time(.3)      
        yield self.server.cooler_on()
        
        
        #imageRegion = yield self.server.get_image_region()
        self.hstart = 100
        self.hend = 250
        self.vstart = 100
        self.vend = 250
        
        self.width = self.hend - self.hstart#imageRegion[3]
        self.height = self.vend - self.vstart#imageRegion[5]
        
        print 'width: ', self.width
        print 'height: ', self.height
        
        error = yield self.server.set_image_region(1,1,self.hstart,self.hend,self.vstart,self.vend)
        print 'image error: ', error
        
    @inlineCallbacks
    def printTemperature(self):
        temp = yield self.server.get_current_temperature()
        print temp
    
    @inlineCallbacks
    def singleScan(self):
        
        width = self.width
        height = self.height

#        fig, ax = plt.subplots()
          
        print "Ready for Acquisition..."
        
        status = yield self.server.get_status()
        if (status == 'DRV_IDLE'):
            yield self.server.set_acquisition_mode(1)
            yield self.server.get_acquisition_mode()
            yield self.server.start_acquisition()
            data = yield self.server.get_acquired_data()
            newdata = data.asarray
#            newarray = np.reshape(newdata, (height, width))
#            ax.matshow(newarray)
#                
#        fig.show()
    
    
    @inlineCallbacks
    def liveVideo(self):
               
        width = self.width
        height = self.height
             
#        newdata = np.zeros(width*height)
#        newarray = np.reshape(newdata, (height, width))
        
        print "Ready for Acquisition..."
        
        status = yield self.server.get_status()
        if (status == 'DRV_IDLE'):
            yield self.server.set_acquisition_mode(5)
            yield self.server.start_acquisition()
            cnt = 0
            self.live = True
            while(self.live == True):
#                t1 = time.clock()
                data = yield self.server.get_most_recent_image()
                newdata = data.asarray
#                print newdata.shape
#                t2 = time.clock()
#                print 'Acquisition Time: ', (t2 - t1)
                #self.data = newdata
                #newarray = np.reshape(newdata, (height, width))
                #print newarray[0, 4:7]
                #self.data = newarray
                self.win.cmon.updateData(newdata, (self.width + 1), (self.height + 1))
#                if (cnt == 0):
#                    self.win.cmon.startYourEngines()
#                    cnt += 1
            yield self.server.abort_acquisition()
    
    @inlineCallbacks
    def abortVideo(self):
        self.live = False
        yield self.server.abort_acquisition()
        print 'aborted'

if __name__ == "__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    Camera = AndorClient(reactor)
    reactor.run()
    
#import numpy
#from matplotlib.pyplot import figure, show
#
#
#
#
#class IndexTracker:
#    def __init__(self, ax, X):
#        self.ax = ax
#        ax.set_title('use scroll wheel to navigate images')
#
#        self.X = X
#        rows,cols,self.slices = X.shape
#        self.ind  = self.slices/2
#
#        self.im = ax.matshow(self.X[:,:,self.ind])
#        self.update()
#
#    def onscroll(self, event):
#        print event.button, event.step
#        if event.button=='up':
#            self.ind = numpy.clip(self.ind+1, 0, self.slices-1)
#        else:
#            self.ind = numpy.clip(self.ind-1, 0, self.slices-1)
#
#
#        self.update()
#
#    def update(self):
#        self.im.set_data(self.X[:,:,self.ind])
#        ax.set_ylabel('slice %s'%self.ind)
#        self.im.axes.figure.canvas.draw()
#
#
#fig = figure()
#ax = fig.add_subplot(111)
#
#X = numpy.random.rand(20,20,40)
#
#tracker = IndexTracker(ax, X)
#
#
#
#fig.canvas.mpl_connect('scroll_event', tracker.onscroll)
#show()
    