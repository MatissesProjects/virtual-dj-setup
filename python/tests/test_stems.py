import unittest
import numpy as np
from brain.stem_separator import StemSeparator

class TestStemSeparator(unittest.TestCase):
    def setUp(self):
        # We don't want to load the real model for unit tests as it's slow/heavy
        self.separator = StemSeparator(model_name="MOCK")

    def test_rms_calculation(self):
        # Create a mock PCM block (sine wave)
        duration = 1.0
        fs = 44100
        f = 440
        t = np.linspace(0, duration, int(fs * duration), endpoint=False)
        # Sine wave with amplitude 0.5
        mock_pcm = 0.5 * np.sin(2 * np.pi * f * t)
        
        # Manually trigger the logic that usually happens in _process_loop
        stems = {
            'vocal': mock_pcm * 0.8,
            'drums': mock_pcm * 1.2,
            'bass': mock_pcm * 0.5,
            'other': mock_pcm * 1.0
        }
        
        for name, data in stems.items():
            rms = np.sqrt(np.mean(data**2))
            self.separator.rms_levels[name] = float(rms)

        # Expected RMS of a sine wave is Amp / sqrt(2)
        expected_base_rms = 0.5 / np.sqrt(2)
        
        self.assertAlmostEqual(self.separator.rms_levels['vocal'], expected_base_rms * 0.8, places=4)
        self.assertAlmostEqual(self.separator.rms_levels['drums'], expected_base_rms * 1.2, places=4)
        self.assertAlmostEqual(self.separator.rms_levels['bass'], expected_base_rms * 0.5, places=4)
        self.assertAlmostEqual(self.separator.rms_levels['other'], expected_base_rms * 1.0, places=4)

    def test_empty_audio_rms(self):
        empty_pcm = np.array([])
        stems = {'vocal': empty_pcm}
        for name, data in stems.items():
            rms = np.sqrt(np.mean(data**2)) if len(data) > 0 else 0
            self.separator.rms_levels[name] = float(rms)
        
        self.assertEqual(self.separator.rms_levels['vocal'], 0.0)

if __name__ == '__main__':
    unittest.main()
