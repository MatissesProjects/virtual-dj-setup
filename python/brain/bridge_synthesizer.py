import numpy as np
import scipy.signal as signal

class BridgeSynthesizer:
    """
    A lightweight additive synthesizer to convert symbolic MIDI bridges into raw PCM.
    Designed for real-time streaming back to the C# engine.
    """
    def __init__(self, sr=44100):
        self.sr = sr
        self.block_size = 1024

    def synthesize_bridge(self, bridge_data):
        """
        Converts a list of MIDI notes into a single continuous float32 buffer.
        """
        duration = bridge_data['duration_sec']
        total_samples = int(duration * self.sr)
        output = np.zeros(total_samples, dtype=np.float32)
        
        bpm = bridge_data['bpm']
        sec_per_beat = 60.0 / bpm
        
        for note in bridge_data['notes']:
            # Start and end in samples
            start_sample = int(note['time'] * sec_per_beat * self.sr)
            end_sample = start_sample + int(note['duration'] * sec_per_beat * self.sr)
            
            if start_sample >= total_samples: continue
            end_sample = min(end_sample, total_samples)
            
            # Frequency calculation (MIDI -> Hz)
            freq = 440.0 * (2.0 ** ((note['note'] - 69) / 12.0))
            
            # Generate wave (Sine + harmonics for "thickness")
            t = np.arange(end_sample - start_sample) / self.sr
            wave = 0.5 * np.sin(2 * np.pi * freq * t) # Fundamental
            wave += 0.2 * np.sin(2 * np.pi * (freq * 2) * t) # 1st Harmonic
            
            # Simple ADSR-like envelope (just linear fade in/out)
            env = np.ones_like(wave)
            fade_len = min(int(0.01 * self.sr), len(wave) // 2)
            if fade_len > 0:
                env[:fade_len] = np.linspace(0, 1, fade_len)
                env[-fade_len:] = np.linspace(1, 0, fade_len)
            
            # Mix in
            output[start_sample:end_sample] += (wave * env * (note['velocity'] / 127.0))
            
        # Hard limit to prevent clipping
        output = np.clip(output, -1.0, 1.0)
        return output

if __name__ == "__main__":
    synth = BridgeSynthesizer()
    bridge_data = {
        "bpm": 128,
        "duration_sec": 4.0,
        "notes": [
            {"note": 60, "velocity": 100, "time": 0, "duration": 1.0},
            {"note": 64, "velocity": 100, "time": 1, "duration": 1.0},
            {"note": 67, "velocity": 100, "time": 2, "duration": 2.0},
        ]
    }
    pcm = synth.synthesize_bridge(bridge_data)
    print(f"Synthesized {len(pcm)} samples ({len(pcm)/44100:.2f}s).")
