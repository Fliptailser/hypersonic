#####################################################################
#
# audio.py
#
# Copyright (c) 2015, Eran Egozy
#
# Released under the MIT License (http://opensource.org/licenses/MIT)
#
#####################################################################

import pyaudio
import numpy as np
import core
import time
from ConfigParser import ConfigParser

kSampleRate = 44100

class Audio(object):
    def __init__(self, num_channels, listen_func = None, input_func = None):
        super(Audio, self).__init__()

        assert(num_channels == 1 or num_channels == 2)
        self.num_channels = num_channels
        self.listen_func = listen_func
        self.input_func = input_func
        self.audio = pyaudio.PyAudio()

        out_dev, in_dev, buffer_size, sample_rate = self._get_parameters()

        # override sample rate if needed...
        if sample_rate:
            global kSampleRate
            kSampleRate = sample_rate

        self.stream = self.audio.open(format = pyaudio.paFloat32,
                                      channels = num_channels,
                                      frames_per_buffer = buffer_size,
                                      rate = kSampleRate,
                                      output = True,
                                      input = input_func != None,
                                      output_device_index = out_dev,
                                      input_device_index = in_dev)

        self.generator = None
        self.cpu_time = 0
        core.register_terminate_func(self.close)

    def close(self) :
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

    # set a generator. The generator must support the method
    # generate(num_frames, num_channels), which returns a numpy array with the correct
    # number of samples: num_frames * num_channels.
    def set_generator(self, gen) :
        self.generator = gen

    # return cpu time calcuating audio time in milliseconds
    def get_cpu_load(self) :
        return 1000 * self.cpu_time

    # must call this every frame.
    def on_update(self):
        t_start = time.time()

        # Ask the generator to generate some audio samples.
        num_frames = self.stream.get_write_available() # number of frames to supply
        if self.generator and num_frames != 0:
            (data, continue_flag) = self.generator.generate(num_frames, self.num_channels)
            if data.dtype != np.float32:
                data = data.astype(np.float32)
            self.stream.write(data.tostring())
            if self.listen_func:
                self.listen_func(data, self.num_channels)
            if not continue_flag:
                self.generator = None

        # get input audio if desired
        if self.input_func:
            try:
                num_frames = self.stream.get_read_available() # number of frames to ask for
                data_str = self.stream.read(num_frames)
                data_np = np.fromstring(data_str, dtype=np.float32)
                self.input_func(data_np, self.num_channels)
            except IOError, e:
                print e

        dt = time.time() - t_start
        a = 0.9
        self.cpu_time = a * self.cpu_time + (1-a) * dt


    # return parameter values for output device idx, input device idx, and
    # buffer size
    def _get_parameters(self):
        # default values
        out_dev = None
        in_dev = None
        buf_size = 1024
        sample_rate = None

        # First, try loading config params from configuration file.
        try:
            config = ConfigParser()
            config.read(('../common/config.cfg', 'config.cfg'))
            out_dev = config.getint('audio', 'outputdevice')
            print 'using config file output device:', out_dev
            in_dev = config.getint('audio', 'inputdevice')
            print 'using config file input device:', in_dev
            buf_size = config.getint('audio', 'buffersize')
            print 'using config file buffer size:', buf_size
            sample_rate = config.getint('audio', 'samplerate')
            print 'using config file buffer size:', sample_rate
        except Exception, e:
            pass

        # for Windows, we want to find the ASIO host API and associated devices
        if out_dev == None:
            cnt = self.audio.get_host_api_count()
            for i in range(cnt):
                api = self.audio.get_host_api_info_by_index(i)
                if api['type'] == pyaudio.paASIO:
                    host_api_idx = i
                    out_dev = api['defaultOutputDevice']
                    in_dev = api['defaultInputDevice']
                    print 'Found ASIO host', host_api_idx
                    print '  using output device', out_dev
                    print '  using input device', in_dev

        return out_dev, in_dev, buf_size, sample_rate

def print_audio_devices():
    audio = pyaudio.PyAudio()
    cnt = audio.get_host_api_count()
    print 'Audio APIs available.'
    print 'idx outDev inDev name'
    for i in range(cnt):
        api = audio.get_host_api_info_by_index(i)
        params = (i, api['defaultOutputDevice'], api['defaultInputDevice'], api['name'])
        print "%2d: %2d      %2d   %s" % params

    print '\nAudio Devices available.'
    print 'idx SRate outCh outLat inCh inLat name'
    cnt = audio.get_device_count()
    for i in range(cnt):
        dev = audio.get_device_info_by_index(i)
        params = (i, dev['defaultSampleRate'],
                     dev['maxOutputChannels'], dev['defaultHighOutputLatency'],
                     dev['maxInputChannels'], dev['defaultHighInputLatency'],
                     dev['name'])
        print "%2d: %d %d     %.3f  %d    %.3f %s" % params
    audio.terminate()

if __name__ == "__main__":
    print_audio_devices()
