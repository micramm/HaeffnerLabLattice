import labrad
import numpy
import time
from scripts.scriptLibrary import dvParameters 
from scripts.PulseSequences.scan729 import scan729 as sequence
from fly_processing import Interpolator

class Bunch:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)
    
    def __setitem__(self, key, val):
        self.__dict__[key] = val
    
    def toDict(self):
        return self.__dict__
    
class scan729():
    ''''
    Performs frequency scan of 729, for each frequency calculates the probability of the ion going dark. Plots the result.
    
    Possible improvements:
        if exceeds 32K counts per iterations of cycles, be able to repeat that multiple times for a given frequency. allow for this change in data analysis
        multiple data processing, including histogram to get the threshold
    '''
    experimentName = 'scan729DDS'
    
    def __init__(self, seqParams, exprtParams, analysisParams):
        #connect and define servers we'll be using
        self.cxn = labrad.connect()
        self.cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
        self.dv = self.cxn.data_vault
        self.pulser = self.cxn.pulser
        self.seqP = Bunch(**seqParams)
        self.expP = Bunch(**exprtParams)
        self.anaP = Bunch(**analysisParams)
        self.readouts = []
        
    def initialize(self):
        #directory name and initial variables
        self.dirappend = time.strftime("%Y%b%d_%H%M_%S",time.localtime())
        self.directory = ['','Experiments', self.experimentName, self.dirappend]
        #saving
        self.dv.cd(self.directory ,True )
        self.dv.new('Counts',[('Freq', 'MHz')],[('Counts','Arb','Arb')] )
        self.programPulser()
        self.setupLogic()
        
    def setupLogic(self):
        self.pulser.switch_auto('axial',  True) #axial needs to be inverted, so that high TTL corresponds to light ON
        self.pulser.switch_auto('110DP',  False) #high TTL corresponds to light OFF
        self.pulser.switch_auto('866DP', False) #high TTL corresponds to light OFF
        #self.pulser.switch_auto('729DP', True)
        self.pulser.switch_manual('crystallization',  False)
    
    def programPulser(self):
        seq = sequence(self.pulser)
        self.pulser.new_sequence()
        seq.setVariables(**params)
        seq.defineSequence()
        self.pulser.program_sequence()
    
    def run(self):
        sP = self.seqP
        xP = self.expP
        self.initialize()
        self.sequence()
        self.finalize()
        print 'DONE {}'.format(self.dirappend)
        
    def sequence(self):
        sP = self.seqP
        xP = self.expP
        for i in range(xP.iterations):
            print i+1
            self.pulser.start_number(xP.startNumber)
            self.pulser.wait_sequence_done()
            self.pulser.stop_sequence()
            readouts = self.pulser.get_readout_counts().asarray
            readouts = numpy.split(readouts,xP.startNumber)
            for i in range(len(readouts)):
                self.dv.add(numpy.vstack((sP.frequencies_729,readouts[i])).transpose())
                self.readouts.append(readouts[i])
    
    def finalize(self):
        #go back to inital logic
        for name in ['axial', '110DP']:
            self.pulser.switch_manual(name)
        #save information to file
        measureList = ['trapdrive','endcaps','compensation','dcoffsetonrf','cavity397','cavity866','multiplexer397','multiplexer866','axialDP', 'pulser']
        measuredDict = dvParameters.measureParameters(self.cxn, self.cxnlab, measureList)
        dvParameters.saveParameters(self.dv, measuredDict)
        dvParameters.saveParameters(self.dv, self.seqP.toDict())
        dvParameters.saveParameters(self.dv, self.expP.toDict())
        #show histogram
        self.analyze()
    
    def analyze(self):
        t1 = time.clock()
        threshold = self.anaP.threshold
        readouts = self.readouts
        print readouts
        totalAnalyzedReadouts = numpy.zeros(len(self.seqP.frequencies_729))
        for i in range(len(self.readouts)):
            for j in range(len(self.seqP.frequencies_729)):
                if (readouts[i][j] >= threshold):
                    totalAnalyzedReadouts[j] += 1
                else:
                    totalAnalyzedReadouts[j] += 0
        ones = numpy.ones(len(totalAnalyzedReadouts))            
        totalAnalyzedReadouts = numpy.divide(totalAnalyzedReadouts, float(self.expP.iterations * self.expP.startNumber))
        totalAnalyzedReadouts = numpy.subtract(ones, totalAnalyzedReadouts)
        t2 = time.clock()
        print 'Analysis took: ', (t2-t1), 'seconds.'
        self.dv.new('Spectrum Analyzed',[('Freq', 'MHz')],[('Counts','Arb','Arb')] )
        self.dv.add(numpy.vstack((self.seqP.frequencies_729,totalAnalyzedReadouts)).transpose())
        self.dv.add_parameter('plotLive', True)

        
    def __del__(self):
        self.cxn.disconnect()
    
if __name__ == '__main__':
    cxn = labrad.connect()
    dv = cxn.data_vault
    dv.cd(['','Calibrations', 'Double Pass 729DP'])
    dv.open(12)
    data = dv.get().asarray
    freq_interp =  data[:,0]
    ampl_interp = data[:,1]
    cxn.disconnect()
    interp = Interpolator(freq_interp, ampl_interp)
    
    freq_min = 160.0
    freq_max = 250.0
    freq_step = 1.0
    
    freqs = numpy.arange(freq_min, freq_max + freq_step, freq_step)
    freqs = numpy.clip(freqs, freq_min, freq_max)
    ampls = interp.interpolated(freqs)
    freqs = freqs.tolist()
    ampls = ampls.tolist()

    params = {
                'frequencies_729':freqs,
                'amplitudes_729': ampls,
                'doppler_cooling':10*10**-3,
                'heating_time':1.0e-3,
                'rabi_time':0.1e-3,#0.5*10**-3,
                'readout_time':5*10**-3,
                'repump_time':10*10**-3,
                'repump_854_ampl': -3.0,
                'repump_866_ampl': -11.0,
                'doppler_cooling_freq':103.0,
                'doppler_cooling_ampl':-11.0,
                'readout_freq':107.0,
                'readout_ampl':-11.0
            }
    exprtParams = {
        'startNumber': 10,
        'iterations': 10
        }
    
    analysis = {
        'threshold':30,
        }
    exprt = scan729(params,exprtParams, analysis)
    exprt.run()