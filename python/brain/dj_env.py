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

    def _calculate_reward(self, features, action, current_chord=None):
        # 1. Dynamics Reward (Target RMS ~0.5)
        # Penalize clipping (>0.9) and silence (<0.05)
        target_rms = 0.5
        r_dynamics = -abs(features['rms'] - target_rms)
        if features['rms'] > 0.9: r_dynamics -= 5.0 # Heavy penalty for clipping
        if features['rms'] < 0.05: r_dynamics -= 2.0 # Penalty for dead air

        # 2. Spectral Balance Reward
        # Target a "pleasant" centroid range (e.g., 2kHz to 5kHz)
        target_centroid = 3500.0
        r_spectral = -abs(features['centroid'] - target_centroid) / 10000.0

        # 3. Smoothness Reward
        # Penalize large changes in action to prevent jitter
        r_smoothness = -np.linalg.norm(action - self.last_action)

        # 4. Clarity Reward (Neural/FFT based)
        # Reward ducking when peaks are detected
        # If is_peak is true, and ducking gain is negative, give bonus
        r_clarity = 0.0
        if features['is_peak'] and action[1] < 0:
            r_clarity = 1.0 # Successful response to transient

        # 5. Harmonic Alignment Reward
        # For simplicity in headless, we'll assume a chord based on song_index
        # (Real training would cycle through chords)
        mock_chords = ["Am", "C", "G", "F"]
        current_chord = mock_chords[features['song_index'] % len(mock_chords)]
        target_freq = ((action[0] + 1) / 2) * 20000.0
        target_gain = ((action[1] + 1) / 2) * 24.0 - 24.0
        r_harmonic = self._calculate_harmonic_reward(current_chord, target_freq, target_gain)

        total_reward = (1.0 * r_dynamics) + (0.5 * r_spectral) + (0.2 * r_smoothness) + (1.0 * r_clarity) + (1.5 * r_harmonic)
        return total_reward

    def step(self, action):
        # 1. Apply Action (Denormalize)
        target_freq = ((action[0] + 1) / 2) * 20000.0
        target_gain = ((action[1] + 1) / 2) * 24.0 - 24.0
        
        self.reader.write_ducking(target_freq, target_gain)

        # 2. Step the Environment
        self.reader.write_step_command(self.step_size)
        
        while not self.reader.is_step_completed():
            time.sleep(0.001)

        # 3. Read new state
        features = self.reader.read_features()
        done = self.reader.read_is_done()

        if features is None:
            obs = np.array([0.0, 0.0, 0.0, 0.0], dtype=np.float32)
            reward = 0.0
        else:
            obs = np.array([
                min(1.0, features['rms']),
                min(1.0, features['centroid'] / 10000.0),
                min(1.0, features['peak'] / 10000.0),
                (features['sequence'] % 1000) / 1000.0 # Time context
            ], dtype=np.float32)
            
            reward = self._calculate_reward(features, action)

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
