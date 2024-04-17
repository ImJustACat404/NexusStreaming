__author__ = "Ido Senn"

import pyaudio

# Set up PyAudio
CHUNK = 1024  # A chunk is a small, manageable piece of audio data, the number of frames per buffer.
# This is the size of the audio chunk to be read/written at a time. (e.g. 1024 bytes)

FORMAT = pyaudio.paInt16  # Format of audio samples (16-bit PCM (pulse-code modulation))
CHANNELS = 1  # Number of audio channels (1 = mono)
RATE = 44100  # number of samples per second (44.1kHz, CD quality)


class AudioStream:
    def __init__(self):
        global FORMAT, CHANNELS, RATE, CHUNK
        # Create a PyAudio stream for input (microphone)
        self.pa_obj = pyaudio.PyAudio()
        self.input_stream = self.pa_obj.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True,
                                             frames_per_buffer=CHUNK)

    def close(self):
        """
        A function that closes the stream
        """
        self.input_stream.stop_stream()
        self.input_stream.close()

    def terminate(self):
        """
        A function that closes the stream and pyaudio
        """
        self.close()
        self.pa_obj.terminate()

    def get_current_audio(self):
        """
        A function that returns all the available audio frames from the streams
        :return: audio frames
        :rtype: bytes
        """
        frames = self.input_stream.get_read_available()
        input_data = self.input_stream.read(frames)
        return input_data
