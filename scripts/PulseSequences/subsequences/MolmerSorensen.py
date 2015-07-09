from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit

class molmer_sorensen(pulse_sequence):
    
    required_parameters = [
                          ('MolmerSorensen','frequency'),
                          ('MolmerSorensen','amplitude'),
                          ('MolmerSorensen','duration'),
                          ('MolmerSorensen','phase'),
                          ('MolmerSorensen','analysis_pulse_enable'),
                          ('MolmerSorensen','analysis_phase'),
                          ('MolmerSorensen','analysis_amplitude'),
                          ('MolmerSorensen','analysis_duration'),
                          ('MolmerSorensen','shape_profile'),
                          ]

    def sequence(self):
        #this hack will be not needed with the new dds parsing methods
        p = self.parameters.MolmerSorensen
        frequency_advance_duration = WithUnit(6, 'us')
        ampl_off = WithUnit(-63.0, 'dBm')
        self.end = self.start + 2*frequency_advance_duration + p.duration
        #first advance the frequency but keep amplitude low
        self.addDDS('729', self.start, frequency_advance_duration, p.frequency, ampl_off)
        self.addDDS('729', self.start + frequency_advance_duration, p.duration, p.frequency, p.amplitude, p.phase, profile=int(p.profile))
        self.addTTL('bichromatic_1', self.start, p.duration + 2*frequency_advance_duration)
        
        if p.analysis_pulse_enable:
            analysis_start = self.end
            self.addDDS('729', analysis_start , p.analysis_duration, p.frequency, p.analysis_amplitude, p.analysis_phase)
            self.end = analysis_start + p.analysis_duration