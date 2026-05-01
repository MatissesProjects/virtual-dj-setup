import numpy as np

class ClashDetector:
    def __init__(self, fft_size=1024, sample_rate=44100):
        self.fft_size = fft_size
        self.sample_rate = sample_rate
        self.bin_width = sample_rate / (fft_size * 2) # Since it's magnitude only

    def find_clashes(self, fft_a, fft_b):
        """
        Compares two FFT magnitude arrays and finds the strongest overlapping region.
        Returns (frequency_hz, clash_intensity)
        """
        # Element-wise product shows overlap strength
        clash_vector = np.array(fft_a) * np.array(fft_b)
        
        peak_bin = np.argmax(clash_vector)
        peak_freq = peak_bin * self.bin_width
        intensity = clash_vector[peak_bin]
        
        return peak_freq, intensity
