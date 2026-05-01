import sys
import os
import time
import numpy as np

# Add parent directory to path to import brain and ipc
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from ipc.shared_memory import SharedMemoryReader
from brain.spectrogram_builder import SpectrogramBuilder

def main():
    print("--- Audio Data Collector ---")
    print("Press 'V' for Vocals, 'D' for Drums, 'O' for Other to save a sample.")
    print("Press 'Q' to quit.")

    reader = SharedMemoryReader()
    if not reader.connect():
        print("Failed to connect to shared memory.")
        return

    builder = SpectrogramBuilder(history_length=128)
    save_dir = "python/brain/data"
    os.makedirs(save_dir, exist_ok=True)

    import msvcrt # Windows-specific for non-blocking key press

    try:
        while True:
            features = reader.read_features()
            if features:
                builder.add_frame(features['fft'])
                
            if msvcrt.kbhit():
                key = msvcrt.getch().decode('utf-8').lower()
                
                label = None
                if key == 'v': label = "vocals"
                elif key == 'd': label = "drums"
                elif key == 'o': label = "other"
                elif key == 'q': break
                
                if label:
                    timestamp = int(time.time())
                    filename = f"{label}_{timestamp}.npy"
                    filepath = os.path.join(save_dir, filename)
                    
                    # Save the normalized spectrogram
                    spec = builder.get_normalized_spectrogram()
                    np.save(filepath, spec)
                    print(f"Saved {label} sample to {filepath}")
            
            time.sleep(0.01)
    except KeyboardInterrupt:
        pass
    finally:
        reader.close()

if __name__ == "__main__":
    main()
