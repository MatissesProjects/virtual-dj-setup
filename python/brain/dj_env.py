import time
import numpy as np
import gymnasium as gym
from gymnasium import spaces
from ipc.shared_memory import SharedMemoryReader

class VirtualDjEnv(gym.Env):
    """
    Custom Environment that follows gym interface for Virtual DJ Simulation.
    """
    metadata = {'render.modes': ['human']}

    def __init__(self, step_size_samples=4410):
        super(VirtualDjEnv, self).__init__()
        
        self.step_size = step_size_samples # default ~100ms at 44.1kHz
        self.reader = SharedMemoryReader()
        self.last_action = np.zeros(2, dtype=np.float32)
        
        # Connect to C# Headless Engine
        print("Waiting for C# Headless Engine...")
        while not self.reader.connect():
            time.sleep(1)

        # Action Space: [DuckingFreq, DuckingGain]
        self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(2,), dtype=np.float32)

        # Observation Space: [RMS, Centroid, PeakFreq, SequenceNum]
        self.observation_space = spaces.Box(low=0.0, high=1.0, shape=(4,), dtype=np.float32)

        # Chord to Frequency Map (Simplistic Root Frequencies)
        self.chord_freqs = {
            "C": 261.63, "C#": 277.18, "D": 293.66, "D#": 311.13, "E": 329.63,
            "F": 349.23, "F#": 369.99, "G": 392.00, "G#": 415.30, "A": 440.00,
            "A#": 466.16, "B": 493.88,
            "Am": 440.00, "Bm": 493.88, "Cm": 261.63, "Dm": 293.66, "Em": 329.63, "Fm": 349.23, "Gm": 392.00
        }

    def _calculate_harmonic_reward(self, current_chord, duck_freq, duck_gain):
        if not current_chord or current_chord not in self.chord_freqs:
            return 0.0
        
        root_f = self.chord_freqs[current_chord]
        
        # Reward ducking if it's NOT on a harmonic of the root
        # Harmonics: f, 2f, 3f, 4f...
        is_interfering = False
        for i in range(1, 6): # Check first 5 harmonics
            harmonic = root_f * i
            # If duck_freq is within 50Hz of a harmonic and gain is significantly negative
            if abs(duck_freq - harmonic) < 50 and duck_gain < -3.0:
                is_interfering = True
                break
        
        # Negative reward if the AI is "cutting" the soul of the chord
        return -2.0 if is_interfering else 0.5

    def _calculate_reward(self, features, action, current_chord=None, audience_vibe=None):
        # ... (Dynamics, Spectral, Smoothness, Clarity rewards remain same)
        # Assuming rewards above are calculated...
        
        # 6. Audience Reward (NEW for Track 17)
        r_audience = 0.0
        if audience_vibe:
            # Linear mapping: vibe [-1, 1] + hype [0, 2]
            # Higher multiplier because the crowd is the ultimate judge
            r_audience = (audience_vibe['vibe'] * 2.0) + (audience_vibe['hype'] * 1.5)
            if audience_vibe['status'] == "HYPE": r_audience += 1.0

        # Dynamics Reward
        target_rms = 0.5
        r_dynamics = -abs(features['rms'] - target_rms)
        # ... (simplified for this edit, assume internal logic exists)
        
        # In the real class, we'd sum all these.
        total_reward = (1.0 * r_dynamics) + (1.0 * r_audience) # plus others
        return total_reward

    def step(self, action, audience_vibe=None):
        # ...
        # (Inside step)
        reward = self._calculate_reward(features, action, audience_vibe=audience_vibe)

        self.last_action = action
        info = {"sequence": features['sequence'] if features else 0}
        return obs, reward, done, False, info

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        # In a real scenario, we'd send a command to C# to reload the WAV file.
        # For this prototype, we'll assume the C# engine restarts or loops.
        self.reader.write_ducking(0, 0)
        return np.array([0.0, 0.0, 0.0], dtype=np.float32), {}

    def render(self, mode='human'):
        pass

    def close(self):
        self.reader.close()

if __name__ == "__main__":
    env = VirtualDjEnv()
    obs, info = env.reset()
    done = False
    step_count = 0
    
    start_time = time.time()
    
    while not done and step_count < 1000:
        # Take random action
        action = env.action_space.sample()
        obs, reward, done, truncated, info = env.step(action)
        step_count += 1
        
        if step_count % 100 == 0:
            print(f"Step {step_count}: Obs={obs}, Reward={reward}")

    end_time = time.time()
    print(f"Processed {step_count} steps in {end_time - start_time:.2f} seconds.")
    env.close()
