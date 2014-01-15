from common.abstractdevices.script_scanner.scan_methods import experiment
from dephasing_scan_duration import dephase_scan_duration
from lattice.scripts.scriptLibrary.common_methods_729 import common_methods_729 as cm
from lattice.scripts.scriptLibrary import dvParameters
import time
import labrad
from labrad.units import WithUnit
from numpy import linspace

class dephase_scan_phase(experiment):
    
    name = 'Dephase Scan Phase'
    dephasing_required_parameters = [('Dephasing_Pulses', 'scan_phase')]
    
    @classmethod
    def all_required_parameters(cls):
        parameters = set(cls.dephasing_required_parameters)
        parameters = parameters.union(set(dephase_scan_duration.all_required_parameters()))
        parameters = list(parameters)
        #removing parameters we'll be overwriting, and they do not need to be loaded
        parameters.remove(('Dephasing_Pulses','evolution_pulses_phase'))
        return parameters
        
    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.scan_dur = self.make_experiment(dephase_scan_duration)
        self.scan_dur.initialize(cxn, context, ident)
        self.scan = []
        self.cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
        self.drift_tracker = cxn.sd_tracker
        self.dv = cxn.data_vault
        self.data_save_context = cxn.context()
    
    def setup_sequence_parameters(self):
        minim,maxim,steps = self.parameters.Dephasing_Pulses.scan_phase
        minim = minim['deg']; maxim = maxim['deg']
        self.scan = linspace(minim,maxim, steps)
        self.scan = [WithUnit(pt, 'deg') for pt in self.scan]
        
    def run(self, cxn, context):
        self.setup_sequence_parameters()
        for i,phase in enumerate(self.scan):
            should_stop = self.pause_or_stop()
            if should_stop: break
            self.parameters['Dephasing_Pulses.evolution_pulses_phase'] = phase
            self.scan_dur.set_parameters(self.parameters)
            self.scan_dur.set_progress_limits(*self.calc_progress_limits(i))
            self.scan_dur.run(cxn, context)
     
    def finalize(self, cxn, context):
        pass
    
    def calc_progress_limits(self, iteration):
        minim = self.min_progress + (self.max_progress - self.min_progress) * float(iteration) / len(self.scan)
        maxim = self.min_progress + (self.max_progress - self.min_progress) * float(iteration+1. ) / len(self.scan)
        print iteration, minim, maxim
        
        return (minim,maxim)

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = dephase_scan_phase(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)