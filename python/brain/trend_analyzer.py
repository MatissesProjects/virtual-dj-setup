import numpy as np
from collections import deque

class TrendAnalyzer:
    def __init__(self, window_size=100): # ~5 seconds at 20Hz
        self.window_size = window_size
        self.rms_history = deque(maxlen=window_size)
        self.centroid_history = deque(maxlen=window_size)

    def add_frame(self, features):
        self.rms_history.append(features['rms'])
        self.centroid_history.append(features['centroid'])

    def analyze(self):
        if len(self.rms_history) < self.window_size:
            return None

        # Calculate slopes using simple linear regression (or just start vs end)
        rms_slope = (np.mean(list(self.rms_history)[-10:]) - np.mean(list(self.rms_history)[:10]))
        centroid_slope = (np.mean(list(self.centroid_history)[-10:]) - np.mean(list(self.centroid_history)[:10]))

        return {
            "rms_slope": rms_slope,
            "centroid_slope": centroid_slope
        }
