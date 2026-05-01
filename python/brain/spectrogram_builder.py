import numpy as np
from collections import deque

class SpectrogramBuilder:
    """
    Manages a rolling window of FFT frames to construct a 2D spectrogram.
    Optimized for feeding into a CNN.
    """
    def __init__(self, bin_count=1024, history_length=128):
        self.bin_count = bin_count
        self.history_length = history_length
        # Initialize with zeros
        self.buffer = deque(maxlen=history_length)
        for _ in range(history_length):
            self.buffer.append(np.zeros(bin_count))

    def add_frame(self, fft_frame):
        """
        Adds a new FFT frame.
        fft_frame: list or numpy array of length bin_count
        """
        if len(fft_frame) != self.bin_count:
            # Handle mismatch if necessary (e.g., interpolate or pad)
            if len(fft_frame) > self.bin_count:
                fft_frame = fft_frame[:self.bin_count]
            else:
                fft_frame = np.pad(fft_frame, (0, self.bin_count - len(fft_frame)))
        
        self.buffer.append(np.array(fft_frame))

    def get_spectrogram(self):
        """
        Returns the current spectrogram as a 2D numpy array.
        Shape: (history_length, bin_count)
        """
        return np.array(self.buffer)

    def get_normalized_spectrogram(self, method="log"):
        """
        Returns a normalized 2D numpy array suitable for CNN input.
        Shape: (history_length, bin_count)
        """
        spec = self.get_spectrogram()
        
        if method == "log":
            # Audio is naturally logarithmic
            spec = np.log1p(spec * 1000) # Scale up before log to preserve detail
            max_val = np.max(spec)
            if max_val > 0:
                spec = spec / max_val
        elif method == "minmax":
            max_val = np.max(spec)
            min_val = np.min(spec)
            if max_val > min_val:
                spec = (spec - min_val) / (max_val - min_val)
                
        return spec

    def get_cnn_input(self):
        """
        Returns the spectrogram shaped for CNN (batch, channel, height, width).
        Shape: (1, 1, history_length, bin_count)
        """
        spec = self.get_normalized_spectrogram()
        return spec.reshape(1, 1, self.history_length, self.bin_count)
