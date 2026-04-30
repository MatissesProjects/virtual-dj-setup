import time
from ipc.shared_memory import SharedMemoryReader
from ipc.intent_emitter import IntentEmitter, IntentType
from brain.trend_analyzer import TrendAnalyzer

def main():
    reader = SharedMemoryReader()
    emitter = IntentEmitter()
    analyzer = TrendAnalyzer(window_size=60) # ~3 seconds
    
    print("Waiting for C# engine...")
    while not reader.connect():
        time.sleep(1)

    last_intent_time = 0
    current_intent = IntentType.IDLE

    try:
        print("Running Intelligence Layer... Press Ctrl+C to stop.")
        while True:
            features = reader.read_features()
            if features:
                analyzer.add_frame(features)
                trends = analyzer.analyze()

                if trends:
                    # Simple rule-based predictive logic
                    # If RMS and Centroid are both climbing, we are likely approaching a drop/transition
                    if trends['rms_slope'] > 0.05 and trends['centroid_slope'] > 500:
                        if current_intent != IntentType.CREATE_TENSION:
                            print("\n[AI] Predicting structural change -> CREATING TENSION")
                            emitter.emit(IntentType.CREATE_TENSION)
                            current_intent = IntentType.CREATE_TENSION
                            last_intent_time = time.time()
                    
                    # If RMS drops suddenly after a tension period, it might be the drop or a cut
                    elif current_intent == IntentType.CREATE_TENSION and trends['rms_slope'] < -0.1:
                        print("\n[AI] Transition detected -> EXECUTING DROP / CLEANING UP")
                        emitter.emit(IntentType.EXECUTE_DROP)
                        current_intent = IntentType.IDLE
                        last_intent_time = time.time()

                # Basic status display
                print(f"\rVibe: {current_intent.name: <20} | RMS: {features['rms']:.4f} | Centroid: {features['centroid']:.0f} Hz", end="")
            
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        reader.close()

if __name__ == "__main__":
    main()
