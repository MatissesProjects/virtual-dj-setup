import time
import json
import threading
import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from ipc.shared_memory import SharedMemoryReader
from ipc.intent_emitter import IntentEmitter, IntentType
from brain.trend_analyzer import TrendAnalyzer
from brain.chord_predictor import ChordPredictor
from logger.state_action_logger import StateActionLogger

# Sync with C# playlist
PLAYLIST = [
    {"title": "Get Lucky", "artist": "Daft Punk"},
    {"title": "Blinding Lights", "artist": "The Weeknd"},
    {"title": "Levitating", "artist": "Dua Lipa"}
]

# Web Server for UI
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

connected_websockets = set()
latest_data = {"vibe": "IDLE", "authority": "AI", "rms": -60, "centroid": 0, "chords": []}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_websockets.add(websocket)
    try:
        while True:
            # Send latest data at 20Hz
            await websocket.send_json(latest_data)
            await asyncio.sleep(0.05)
    except Exception:
        pass
    finally:
        connected_websockets.remove(websocket)

@app.post("/takeover")
async def takeover():
    # In a real scenario, this would send a special TCP command to C#
    print("\n[UI] Manual Override requested via Dashboard.")
    return {"status": "ok"}

@app.post("/yield")
async def yield_control():
    print("\n[UI] Yield to AI requested via Dashboard.")
    return {"status": "ok"}

def run_web_server():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="error")

def main():
    threading.Thread(target=run_web_server, daemon=True).start()
    
    reader = SharedMemoryReader()
    emitter = IntentEmitter()
    analyzer = TrendAnalyzer(window_size=60)
    chord_predictor = ChordPredictor()
    logger = StateActionLogger()
    
    print("Waiting for C# engine...")
    while not reader.connect():
        time.sleep(1)

    current_intent = IntentType.IDLE
    current_song_index = -1
    current_chords = []

    try:
        print("System Live! Chord Retrieval & Predictive Mixing Active.")
        while True:
            features = reader.read_features()
            if features:
                # Update Playlist Context
                if features['song_index'] != current_song_index:
                    current_song_index = features['song_index']
                    if 0 <= current_song_index < len(PLAYLIST):
                        song = PLAYLIST[current_song_index]
                        print(f"\n[PLAYLIST] New Song: {song['title']} - {song['artist']}")
                        current_chords = chord_predictor.get_chords(song['title'], song['artist'])
                        print(f"[AI] Fetched Chords: {current_chords}")

                authority = "AI" if features['authority'] == 0 else "HUMAN"
                
                # Update latest data for WebSocket broadcast
                latest_data["rms"] = 20 * (features['rms'] + 0.000001)
                latest_data["centroid"] = features['centroid']
                latest_data["authority"] = authority
                latest_data["vibe"] = current_intent.name
                latest_data["chords"] = current_chords

                if features['authority'] == 1:
                    logger.log(features, {"width": 1.0, "ratio": 4.0})
                    print(f"\r[SHADOW MODE] Logging... RMS: {features['rms']:.4f}    ", end="")
                else:
                    # AI MODE: Analyze trends
                    analyzer.add_frame(features)
                    trends = analyzer.analyze()
                    
                    if trends:
                        if trends['rms_slope'] > 0.05:
                            if current_intent != IntentType.CREATE_TENSION:
                                emitter.emit(IntentType.CREATE_TENSION)
                                current_intent = IntentType.CREATE_TENSION
                        elif current_intent == IntentType.CREATE_TENSION and trends['rms_slope'] < -0.1:
                            emitter.emit(IntentType.EXECUTE_DROP)
                            current_intent = IntentType.IDLE

                    print(f"\rVibe: {current_intent.name: <20} | Auth: {authority} | Chords: {str(current_chords)[:20]}...    ", end="")
            
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        reader.close()
        logger.close()

if __name__ == "__main__":
    main()
