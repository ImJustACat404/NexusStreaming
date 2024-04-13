import pyaudio

# Set up PyAudio
CHUNK = 1024  # Number of frames per buffer
FORMAT = pyaudio.paInt16  # Format of audio samples (16-bit PCM (pulse-code modulation))
CHANNELS = 1  # Number of audio channels (1 for left, one for right)
RATE = 44100  # number of samples per second (30kHz) original value by chatgpt was 44.1


class AudioStream:
    def __init__(self):
        global FORMAT, CHANNELS, RATE, CHUNK
        # Create a PyAudio stream for output
        self.pa_obj = pyaudio.PyAudio()
        self.output_stream = self.pa_obj.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True,
                                              frames_per_buffer=CHUNK)

    def close(self):
        self.output_stream.stop_stream()
        self.output_stream.close()

    def terminate(self):
        self.close()
        self.pa_obj.terminate()

    def play_audio(self, audio_bytes):
        self.output_stream.write(audio_bytes)
