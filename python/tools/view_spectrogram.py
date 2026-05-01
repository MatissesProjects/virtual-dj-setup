import sys
import os
import time
import numpy as np
import matplotlib.pyplot as plt

# Add parent directory to path to import brain and ipc
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from ipc.shared_memory import SharedMemoryReader
from brain.spectrogram_builder import SpectrogramBuilder

def main():
    print("Starting Spectrogram Viewer...")
    reader = SharedMemoryReader()
    if not reader.connect():
        print("Failed to connect to shared memory. Is the C# engine running?")
        return

    builder = SpectrogramBuilder(history_length=128)
    
    # Set up plotting
    plt.ion()
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # We transpose to have frequency on Y axis and time on X axis
    spec = builder.get_normalized_spectrogram().T
    im = ax.imshow(spec, aspect='auto', origin='lower', cmap='magma', vmin=0, vmax=1)
    
    ax.set_title("Real-time Spectrogram (1024 Bins)")
    ax.set_ylabel("Frequency Bin")
    ax.set_xlabel("Time (Frames)")
    plt.colorbar(im, label="Normalized Magnitude (Log Scale)")

    last_update = time.time()
    
    try:
        while True:
            features = reader.read_features()
            if features:
                builder.add_frame(features['fft'])
                
                # Update plot at ~20Hz to save CPU
                if time.time() - last_update > 0.05:
                    im.set_data(builder.get_normalized_spectrogram().T)
                    fig.canvas.draw()
                    fig.canvas.flush_events()
                    last_update = time.time()
            else:
                time.sleep(0.01)
    except KeyboardInterrupt:
        print("\nStopping viewer...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        reader.close()
        plt.close()

if __name__ == "__main__":
    main()
