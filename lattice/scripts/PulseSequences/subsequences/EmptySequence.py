from scripts.PulseSequences.PulseSequence import PulseSequence

class empty_sequence(PulseSequence):
    
    @staticmethod
    def configuration():
        config = [
                  'empty_sequence_duration'
                  ]
        return config
        
    def sequence(self):
        self.end = self.start + self.p.empty_sequence_duration