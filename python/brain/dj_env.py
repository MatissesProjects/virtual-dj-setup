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
        
        # Connect to C# Headless Host
        print("Waiting for C# Headless Engine...")
        while not self.reader.connect():
            time.sleep(1)

        # Action Space: [DuckingFreq (0-20000Hz), DuckingGain (-24 to 0 dB)]
        # Normalized for RL agent to [-1, 1]
        self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(2,), dtype=np.float32)

        # Observation Space: [RMS, Centroid, PeakFreq]
        self.observation_space = spaces.Box(low=0.0, high=1.0, shape=(3,), dtype=np.float32)

    def step(self, action):
        # 1. Apply Action (Denormalize)
        target_freq = ((action[0] + 1) / 2) * 20000.0  # 0 to 20k Hz
        target_gain = ((action[1] + 1) / 2) * 24.0 - 24.0 # -24 to 0 dB
        
        self.reader.write_ducking(target_freq, target_gain)

        # 2. Step the Environment
        self.reader.write_step_command(self.step_size)
        
        # 3. Wait for C# to finish processing
        while not self.reader.is_step_completed():
            time.sleep(0.001)

        # 4. Read new state
        features = self.reader.read_features()
        done = self.reader.read_is_done()

        if features is None:
            # Fallback if tearing occurred exactly on read (rare with lock)
            obs = np.array([0.0, 0.0, 0.0], dtype=np.float32)
            reward = 0.0
        else:
            # Normalize observation
            obs = np.array([
                min(1.0, features['rms']),
                min(1.0, features['centroid'] / 10000.0),
                min(1.0, features['peak'] / 10000.0)
            ], dtype=np.float32)
            
            # Simple Reward: Penalize extremely high RMS (clashing)
            reward = 1.0 if features['rms'] < 0.8 else -1.0

        info = {}
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
