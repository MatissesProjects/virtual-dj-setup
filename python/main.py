import time
from ipc.shared_memory import SharedMemoryReader

def main():
    reader = SharedMemoryReader()
    
    print("Waiting for C# engine...")
    while not reader.connect():
        time.sleep(1)

    try:
        print("Reading features... Press Ctrl+C to stop.")
        while True:
            features = reader.read_features()
            if features:
                # Basic intelligence placeholder
                vibe = "Chilling"
                if features['rms'] > 0.1:
                    vibe = "Energy Climbing"
                if features['centroid'] > 5000:
                    vibe = "High Frequency Dominant"
                
                print(f"\rVibe: {vibe: <25} | RMS: {features['rms']:.4f} | Peak: {features['peak']:.0f} Hz", end="")
            
            time.sleep(0.05) # 20Hz refresh
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        reader.close()

if __name__ == "__main__":
    main()
