from common.abstractdevices.script_scanner.scan_methods import experiment
from lattice.scripts.scriptLibrary.common_methods_729 import common_methods_729 as cm
from lattice.scripts.experiments.Camera.ion_state_detector import ion_state_detector
from labrad.units import WithUnit
import numpy
import time
       
class base_excitation(experiment):
    name = ''  
    excitation_required_parameters = [
                            ('OpticalPumping','frequency_selection'),
                            ('OpticalPumping','manual_frequency_729'),
                            ('OpticalPumping','line_selection'),
                            
                            ('OpticalPumpingAux','aux_op_line_selection'),
                            ('OpticalPumpingAux','aux_op_enable'),
                            
                            ('SidebandCooling','frequency_selection'),
                            ('SidebandCooling','manual_frequency_729'),
                            ('SidebandCooling','line_selection'),
                            ('SidebandCooling','sideband_selection'),
                            
                            ('SequentialSBCooling', 'sideband_selection'),
                            
                            ('TrapFrequencies','axial_frequency'),
                            ('TrapFrequencies','radial_frequency_1'),
                            ('TrapFrequencies','radial_frequency_2'),
                            ('TrapFrequencies','rf_drive_frequency'),
                            ('TrapFrequencies', 'aux_radial'),
                            ('TrapFrequencies', 'aux_axial'),
                            
                            ('StateReadout', 'repeat_each_measurement'),
                            ('StateReadout', 'state_readout_threshold'),
                            ('StateReadout', 'threshold_list'),

                            ('StateReadout', 'use_camera_for_readout'),
                            #('StateReadout', 'state_readout_duration'),
                            ('StateReadout', 'camera_readout_duration'),
                            ('StateReadout', 'pmt_readout_duration'),
                            ('StateReadout', 'pmt_mode'),
                            
                            ('IonsOnCamera','ion_number'),
                            ('IonsOnCamera','vertical_min'),
                            ('IonsOnCamera','vertical_max'),
                            ('IonsOnCamera','vertical_bin'),
                            ('IonsOnCamera','horizontal_min'),
                            ('IonsOnCamera','horizontal_max'),
                            ('IonsOnCamera','horizontal_bin'),
                            
                            ('IonsOnCamera','fit_amplitude'),
                            ('IonsOnCamera','fit_background_level'),
                            ('IonsOnCamera','fit_center_horizontal'),
                            ('IonsOnCamera','fit_center_vertical'),
                            ('IonsOnCamera','fit_rotation_angle'),
                            ('IonsOnCamera','fit_sigma'),
                            ('IonsOnCamera','fit_spacing'),
                           ]
    pulse_sequence = None
    
    @classmethod
    def all_required_parameters(cls):
        params = set(cls.excitation_required_parameters)
        params = params.union(set(cls.pulse_sequence.all_required_parameters()))
        params = list(params)
        params.remove(('OpticalPumping', 'optical_pumping_frequency_729'))
        params.remove(('SidebandCooling', 'sideband_cooling_frequency_729'))
        params.remove(('OpticalPumpingAux', 'aux_optical_frequency_729'))
        params.remove(('SequentialSBCooling', 'frequency'))
        params.remove(('StateReadout', 'state_readout_duration'))
        params.remove(('SidebandPrecooling', 'frequency_1'))
        params.remove(('SidebandPrecooling', 'frequency_2'))
        return params
    
    def initialize(self, cxn, context, ident):
        self.pulser = cxn.pulser
        self.drift_tracker = cxn.sd_tracker
        self.dv = cxn.data_vault
        self.total_readouts = []
        self.readout_save_context = cxn.context()
        self.histogram_save_context = cxn.context()
        self.readout_save_iteration = 0
        self.use_camera = self.parameters.StateReadout.use_camera_for_readout
        self.setup_sequence_parameters()
        self.setup_initial_switches()
        self.setup_data_vault()
        if self.use_camera:
            self.initialize_camera(cxn)

    def initialize_camera(self, cxn):
        self.total_camera_confidences = []
        p = self.parameters.IonsOnCamera
        from lmfit import Parameters as lmfit_Parameters
        self.camera = cxn.andor_server
        self.fitter = ion_state_detector(int(p.ion_number))
        self.camera_initially_live_display = self.camera.is_live_display_running()
        self.camera.abort_acquisition()
        self.initial_exposure = self.camera.get_exposure_time()
        exposure = self.parameters.StateReadout.state_readout_duration
        self.camera.set_exposure_time(exposure)
        self.initial_region = self.camera.get_image_region()
        self.image_region = [
                             int(p.horizontal_bin),
                             int(p.vertical_bin),
                             int(p.horizontal_min),
                             int(p.horizontal_max),
                             int(p.vertical_min),
                             int(p.vertical_max),
                             ]
        self.fit_parameters = lmfit_Parameters()
        self.fit_parameters.add('ion_number', value = int(p.ion_number))
        self.fit_parameters.add('background_level', value = p.fit_background_level)
        self.fit_parameters.add('amplitude', value = p.fit_amplitude)
        self.fit_parameters.add('rotation_angle', p.fit_rotation_angle)
        self.fit_parameters.add('center_x', value = p.fit_center_horizontal)
        self.fit_parameters.add('center_y', value = p.fit_center_vertical)
        self.fit_parameters.add('spacing', value = p.fit_spacing)
        self.fit_parameters.add('sigma', value = p.fit_sigma)
        x_axis = numpy.arange(self.image_region[2], self.image_region[3] + 1, self.image_region[0])
        y_axis = numpy.arange(self.image_region[4], self.image_region[5] + 1, self.image_region[1])
        xx,yy = numpy.meshgrid(x_axis, y_axis)
        self.fitter.set_fitted_parameters(self.fit_parameters, xx, yy)
        self.camera.set_image_region(*self.image_region)
        self.camera.set_acquisition_mode('Kinetics')
        self.initial_trigger_mode = self.camera.get_trigger_mode()
        self.camera.set_trigger_mode('External')
        
    def setup_data_vault(self):
        localtime = time.localtime()
        self.datasetNameAppend = time.strftime("%Y%b%d_%H%M_%S",localtime)
        self.datasetNameAppend += '_rdout'
        dirappend = [ time.strftime("%Y%b%d",localtime) ,time.strftime("%H%M_%S", localtime)]
        self.save_directory = ['','Experiments']
        self.save_directory.extend([self.name])
        self.save_directory.extend(dirappend)
        self.dv.cd(self.save_directory ,True, context = self.readout_save_context)
        self.dv.new('Readout {}'.format(self.datasetNameAppend),[('Iteration', 'Arb')],[('Readout Counts','Arb','Arb')], context = self.readout_save_context)        
    
    def setup_sequence_parameters(self):
        op = self.parameters.OpticalPumping
        sp = self.parameters.StatePreparation
        optical_pumping_frequency = cm.frequency_from_line_selection(op.frequency_selection, op.manual_frequency_729, op.line_selection, self.drift_tracker, sp.optical_pumping_enable)
        self.parameters['OpticalPumping.optical_pumping_frequency_729'] = optical_pumping_frequency
        aux = self.parameters.OpticalPumpingAux
        aux_optical_pumping_frequency = cm.frequency_from_line_selection('auto', WithUnit(0,'MHz'),  aux.aux_op_line_selection, self.drift_tracker, aux.aux_op_enable)
        self.parameters['OpticalPumpingAux.aux_optical_frequency_729'] = aux_optical_pumping_frequency
        sc = self.parameters.SidebandCooling
        sideband_cooling_frequency = cm.frequency_from_line_selection(sc.frequency_selection, sc.manual_frequency_729, sc.line_selection, self.drift_tracker, sp.sideband_cooling_enable)
        if sc.frequency_selection == 'auto': 
            trap = self.parameters.TrapFrequencies
            sideband_cooling_frequency = cm.add_sidebands(sideband_cooling_frequency, sc.sideband_selection, trap)
        self.parameters['SidebandCooling.sideband_cooling_frequency_729'] = sideband_cooling_frequency
        
        sc2 = self.parameters.SequentialSBCooling
        sc2freq = cm.frequency_from_line_selection(sc.frequency_selection, sc.manual_frequency_729, sc.line_selection, self.drift_tracker, sp.sideband_cooling_enable)
        sc2freq = cm.add_sidebands(sc2freq, sc2.sideband_selection, trap)
        self.parameters['SequentialSBCooling.frequency'] = sc2freq

        ### sideband precooling stuff ###
        spc = self.parameters.SidebandPrecooling
        sbc_carrier_frequency = cm.frequency_from_line_selection(sc.frequency_selection, sc.manual_frequency_729, sc.line_selection, self.drift_tracker, sp.sideband_cooling_enable)
        frequency_1 = WithUnit(0.0, 'MHz')
        frequency_2 = WithUnit(0.0, 'MHz')
        if spc.mode_1 != 'off':
            tf = self.parameters['TrapFrequencies.' + spc.mode_1]
            frequency_1 = sbc_carrier_frequency - tf
        if spc.mode_2 != 'off':
            tf = self.parameters['TrapFrequencies.' + spc.mode_2]
            frequency_2 = sbc_carrier_frequency - tf
        self.parameters['SidebandPrecooling.frequency_1'] = frequency_1
        self.parameters['SidebandPrecooling.frequency_2'] = frequency_2

        # set state readout time
        if self.use_camera:
            self.parameters['StateReadout.state_readout_duration'] = self.parameters.StateReadout.camera_readout_duration
        else:
            self.parameters['StateReadout.state_readout_duration'] = self.parameters.StateReadout.pmt_readout_duration

    
    def setup_initial_switches(self):
        self.pulser.switch_manual('crystallization',  False)
        #switch off 729 at the beginning
        self.pulser.output('729global', False)
        self.pulser.output('729local', False)
    
    def plot_current_sequence(self, cxn):
        from common.okfpgaservers.pulser.pulse_sequences.plot_sequence import SequencePlotter
        dds = cxn.pulser.human_readable_dds()
        ttl = cxn.pulser.human_readable_ttl()
        channels = cxn.pulser.get_channels()
        sp = SequencePlotter(ttl, dds, channels)
        sp.makePlot()
        
    def run(self, cxn, context, readout_mode = 'excitations'):
        threshold = int(self.parameters.StateReadout.state_readout_threshold)
        repetitions = int(self.parameters.StateReadout.repeat_each_measurement)
        pulse_sequence = self.pulse_sequence(self.parameters)
        pulse_sequence.programSequence(self.pulser)
        #self.plot_current_sequence(cxn)
        if self.use_camera:
            #print 'starting acquisition'
            self.camera.set_number_kinetics(repetitions)
            self.camera.start_acquisition()
        self.pulser.start_number(repetitions)
        self.pulser.wait_sequence_done()
        self.pulser.stop_sequence()
        self.pmt_mode = self.parameters.StateReadout.pmt_mode
        if not self.use_camera:
            #get percentage of the excitation using the PMT threshold
            readouts = self.pulser.get_readout_counts()
            self.save_data(readouts)            
            if len(readouts):
                if self.pmt_mode == 'simple': exci = numpy.count_nonzero(readouts <= threshold) / float(len(readouts))
                if self.pmt_mode == 'number_dark': exci, states = self.count_dark(readouts)
                print self.pmt_mode
            else:
                #got no readouts
                exci = -1.0
            if readout_mode == 'excitations': 
                ion_state = [exci]
            elif readout_mode == 'num_excited':
                ion_state = states
#             print readouts
        else:
            #get the percentage of excitation using the camera state readout
            proceed = self.camera.wait_for_kinetic()
            if not proceed:
                self.camera.abort_acquisition()
                
                self.finalize(cxn, context)
                raise Exception ("Did not get all kinetic images from camera")
            images = self.camera.get_acquired_data(repetitions)
            self.camera.abort_acquisition()
            x_pixels = int( (self.image_region[3] - self.image_region[2] + 1.) / (self.image_region[0]) )
            y_pixels = int(self.image_region[5] - self.image_region[4] + 1.) / (self.image_region[1])
            images = numpy.reshape(images, (repetitions, y_pixels, x_pixels))
            readouts, confidences = self.fitter.state_detection(images)
            if readout_mode == 'excitations':
                ion_state = 1 - readouts.mean(axis = 0)
            elif readout_mode == 'num_excited':
                states = self.get_states(readouts)
                ion_state = [states[0], states[1] + states[2], states[3]] # [SS, SD + DS, DD]
            elif readout_mode == 'states': # 
                ion_state = self.get_states(readouts) # measure in the SS, SD, DS, DD basis
            #useful for debugging, saving the images
#             numpy.save('readout {}'.format(int(time.time())), images)
            self.save_confidences(confidences)
        return ion_state, readouts
    
    def get_states(self, readouts):
        SS = numpy.array([1, 1])
        SD = numpy.array([1, 0])
        DS = numpy.array([0, 1])
        DD = numpy.array([0, 0])
        
        numSS = 0
        numSD = 0
        numDS = 0
        numDD = 0
        for readout in readouts:
            if numpy.array_equal(readout, SS): numSS += 1
            elif numpy.array_equal(readout, SD): numSD += 1
            elif numpy.array_equal(readout, DS): numDS += 1
            elif numpy.array_equal(readout, DD): numDD += 1
        N = float(len(readouts))
        return [numSS/N, numSD/N, numDS/N, numDD/N ]
    

    def count_dark(self, readouts):
        import IPython
        #thresholds = self.parameters.StateReadout.threshold_list
        threshold_list = self.parameters.StateReadout.threshold_list
        thresholds=[int(x) for x in threshold_list.split(',')]
        print "working with the string format"
        #thresholds = thresholds[1]
        #thresholds.append(0)
        thresholds = sorted(thresholds)
        print numpy.array(readouts)
        num_ions = len(thresholds)
        print thresholds
        binned = numpy.histogram(readouts, bins=[0]+thresholds + [5000])[0]
        #IPython.embed()
        #print binned
        N = float(len(readouts))
        binned = binned/N
        mean = numpy.dot(binned, range(num_ions+1)) # avg number of ions dark
        return mean, binned
        

    @property
    def output_size(self):
        if self.use_camera:
            return int(self.parameters.IonsOnCamera.ion_number)
        else:
            return 1
    
    def finalize(self, cxn, context):
        if self.use_camera:
            #if used the camera, return it to the original settings
            self.camera.set_trigger_mode(self.initial_trigger_mode)
            self.camera.set_exposure_time(self.initial_exposure)
            self.camera.set_image_region(self.initial_region)
            if self.camera_initially_live_display:
                self.camera.start_live_display()
               
    def save_data(self, readouts):
        #save the current readouts
        iters = numpy.ones_like(readouts) * self.readout_save_iteration
        self.dv.add(numpy.vstack((iters, readouts)).transpose(), context = self.readout_save_context)
        self.readout_save_iteration += 1
        self.total_readouts.extend(readouts)
        if (len(self.total_readouts) >= 500):
            hist, bins = numpy.histogram(self.total_readouts, 50)
            self.dv.cd(self.save_directory ,True, context = self.histogram_save_context)
            self.dv.new('Histogram {}'.format(self.datasetNameAppend),[('Counts', 'Arb')],[('Occurence','Arb','Arb')], context = self.histogram_save_context )
            self.dv.add(numpy.vstack((bins[0:-1],hist)).transpose(), context = self.histogram_save_context )
            self.dv.add_parameter('Histogram729', True, context = self.histogram_save_context )
            self.total_readouts = []
    
    def save_confidences(self, confidences):
        '''
        saves confidences readings for the camera state detection
        '''
        self.total_camera_confidences.extend(confidences)
        if (len(self.total_camera_confidences) >= 300):
            hist, bins = numpy.histogram(self.total_camera_confidences, 30)
            self.dv.cd(self.save_directory ,True, context = self.histogram_save_context)
            self.dv.new('Histogram Camera {}'.format(self.datasetNameAppend),[('Counts', 'Arb')],[('Occurence','Arb','Arb')], context = self.histogram_save_context )
            self.dv.add(numpy.vstack((bins[0:-1],hist)).transpose(), context = self.histogram_save_context )
            self.dv.add_parameter('HistogramCameraConfidence', True, context = self.histogram_save_context )
            self.total_camera_confidences = []
