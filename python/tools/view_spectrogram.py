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
    print("Starting Multi-Deck Spectrogram Viewer...")
    reader = SharedMemoryReader()
    if not reader.connect():
        print("Failed to connect to shared memory. Is the C# engine running?")
        return

    # One builder per deck
    builders = {0: SpectrogramBuilder(history_length=128), 1: SpectrogramBuilder(history_length=128)}
    
    # Set up plotting with two subplots
    plt.ion()
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))
    
    spec_a = builders[0].get_normalized_spectrogram().T
    im1 = ax1.imshow(spec_a, aspect='auto', origin='lower', cmap='magma', vmin=0, vmax=1)
    ax1.set_title("Deck A Spectrogram")
    
    spec_b = builders[1].get_normalized_spectrogram().T
    im2 = ax2.imshow(spec_b, aspect='auto', origin='lower', cmap='viridis', vmin=0, vmax=1)
    ax2.set_title("Deck B Spectrogram")
    
    for ax in [ax1, ax2]:
        ax.set_ylabel("Frequency Bin")
        ax.set_xlabel("Time (Frames)")

    last_update = time.time()
    
    try:
        while True:
            features = reader.read_features()
            if features:
                deck_idx = features.get('song_index', 0)
                if deck_idx in builders:
                    builders[deck_idx].add_frame(features['fft'])
                
                # Update plot at ~20Hz
                if time.time() - last_update > 0.05:
                    im1.set_data(builders[0].get_normalized_spectrogram().T)
                    im2.set_data(builders[1].get_normalized_spectrogram().T)
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
