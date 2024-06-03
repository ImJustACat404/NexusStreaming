__author__ = "Ido Senn"

import pyaudio

# Set up PyAudio
CHUNK = 1024  # A chunk is a small, manageable piece of audio data, the number of frames per buffer.
# This is the size of the audio chunk to be read/written at a time. (e.g. 1024 bytes)

FORMAT = pyaudio.paInt16  # Format of audio samples (16-bit PCM (pulse-code modulation))
CHANNELS = 1  # Number of audio channels (1 = mono)
RATE = 44100  # number of samples per second (44.1kHz)


class AudioStream:
    def __init__(self):
        global FORMAT, CHANNELS, RATE, CHUNK
        # Create a PyAudio stream for output
        self.pa_obj = pyaudio.PyAudio()
        self.output_stream = self.pa_obj.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True,
                                              frames_per_buffer=CHUNK)

    def close(self):
        """
        A function that closes the stream
        """
        self.output_stream.stop_stream()
        self.output_stream.close()

    def terminate(self):
        """
        A function that closes the stream and pyaudio, if a stream was created
        """
        try:
            # Try terminating the audio stream
            self.close()
            self.pa_obj.terminate()
        except Exception as e:
            # Audio stream was not created
            print(f"Did not terminate, because stream wasn't created anyway\nError: {e}")

    def play_audio(self, audio_bytes):
        """
        A function that plays given audio
        :param audio_bytes: The audio to play
        :type audio_bytes: bytes
        """
        self.output_stream.write(audio_bytes)
