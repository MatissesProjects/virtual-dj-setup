import time
import json
import threading
from fastapi import FastAPI, WebSocket
from ipc.shared_memory import SharedMemoryReader
from ipc.intent_emitter import IntentEmitter, IntentType
from brain.trend_analyzer import TrendAnalyzer
from logger.state_action_logger import StateActionLogger

# Web Server for UI
app = FastAPI()
connected_websockets = set()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_websockets.add(websocket)
    try:
        while True:
            await websocket.receive_text()
    finally:
        connected_websockets.remove(websocket)

def run_web_server():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

def main():
    # Start Web Server in a separate thread
    threading.Thread(target=run_web_server, daemon=True).start()
    
    reader = SharedMemoryReader()
    emitter = IntentEmitter()
    analyzer = TrendAnalyzer(window_size=60) # ~3 seconds
    logger = StateActionLogger()
    
    print("Waiting for C# engine...")
    while not reader.connect():
        time.sleep(1)

    last_intent_time = 0
    current_intent = IntentType.IDLE

    try:
        print("Running Intelligence Layer & Web Server... Press Ctrl+C to stop.")
        while True:
            features = reader.read_features()
            if features:
                authority = "AI" if features['authority'] == 0 else "HUMAN"
                
                # Broadcast to UI
                if connected_websockets:
                    # Async broadcast simplified for main loop
                    # In a real app, we'd use a queue and an async loop
                    pass

                # SHADOW MODE: If Human is in control, log everything for learning
                if features['authority'] == 1:
                    logger.log(features, {"width": 1.0, "ratio": 4.0})
                    print(f"\r[SHADOW MODE] Logging Human Action... Vibe: {current_intent.name: <15}", end="")
                else:
                    # AI MODE: Analyze trends and emit intents
                    analyzer.add_frame(features)
                    trends = analyzer.analyze()

                    if trends:
                        if trends['rms_slope'] > 0.05 and trends['centroid_slope'] > 500:
                            if current_intent != IntentType.CREATE_TENSION:
                                print("\n[AI] Predicting structural change -> CREATING TENSION")
                                emitter.emit(IntentType.CREATE_TENSION)
                                current_intent = IntentType.CREATE_TENSION
                                last_intent_time = time.time()
                        elif current_intent == IntentType.CREATE_TENSION and trends['rms_slope'] < -0.1:
                            print("\n[AI] Transition detected -> EXECUTING DROP / CLEANING UP")
                            emitter.emit(IntentType.EXECUTE_DROP)
                            current_intent = IntentType.IDLE
                            last_intent_time = time.time()

                    print(f"\rVibe: {current_intent.name: <20} | Auth: {authority} | RMS: {features['rms']:.4f}", end="")
            
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        reader.close()
        logger.close()

if __name__ == "__main__":
    main()
