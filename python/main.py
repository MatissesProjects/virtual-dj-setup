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
from brain.clash_detector import ClashDetector
from brain.spectrogram_builder import SpectrogramBuilder
from brain.audio_classifier import AudioClassifier
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
latest_data = {"vibe": "IDLE", "authority": "AI", "rms": -60, "centroid": 0, "chords": [], "ducking": {"freq": 0, "gain": 0}, "xfader": 0.5, "classification": {"class": "Unknown", "confidence": 0}}

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

@app.post("/crossfade")
async def crossfade(position: float):
    # This will be picked up by the main loop
    latest_data["xfader"] = position
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
    clash_detector = ClashDetector()
    spec_builders = {0: SpectrogramBuilder(), 1: SpectrogramBuilder()}
    classifier = AudioClassifier()
    logger = StateActionLogger()
    
    # Track latest classification per deck
    deck_classifications = {0: {"class": "Unknown", "confidence": 0}, 1: {"class": "Unknown", "confidence": 0}}
    
    print("Waiting for C# engine...")
    while not reader.connect():
        time.sleep(1)

    current_intent = IntentType.IDLE
    current_song_index = -1
    current_chords = []
    inference_counter = 0

    try:
        print("System Live! Multi-Deck CNN Analysis Active.")
        while True:
            features = reader.read_features()
            if features:
                deck_idx = features.get('song_index', 0) # This is now deck_index
                
                # Sync XFader from UI to C#
                reader.write_xfader(latest_data["xfader"])

                # Update Spectrogram for the specific deck
                if deck_idx in spec_builders:
                    spec_builders[deck_idx].add_frame(features['fft'])
                
                # Run CNN Inference every 30 frames
                inference_counter += 1
                if inference_counter >= 30:
                    inference_counter = 0
                    for idx, builder in spec_builders.items():
                        cnn_input = builder.get_cnn_input()
                        deck_classifications[idx] = classifier.predict(cnn_input)
                    
                    # For UI display, prioritize the one with higher confidence or active deck
                    # For now, just show the one with highest vocal confidence or Deck A
                    latest_data["classification"] = deck_classifications[0] 

                # Update Playlist Context (Only if it's Deck A for simplicity)
                if deck_idx == 0 and features['song_index'] != current_song_index:
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
                # latest_data["xfader"] = features['xfader'] # Optionally read back

                if features['authority'] == 1:
                    logger.log(features, {"width": 1.0, "ratio": 4.0})
                    print(f"\r[SHADOW MODE] Logging... RMS: {features['rms']:.4f}    ", end="")
                else:
                    # AI MODE: Analyze trends
                    analyzer.add_frame(features)
                    trends = analyzer.analyze()
                    
                    # High-bandwidth verification: calculate max FFT bin
                    max_fft = max(features['fft']) if features['fft'] else 0
                    
                    if trends:
                        if trends['rms_slope'] > 0.05:
                            if current_intent != IntentType.CREATE_TENSION:
                                emitter.emit(IntentType.CREATE_TENSION)
                                current_intent = IntentType.CREATE_TENSION
                        elif current_intent == IntentType.CREATE_TENSION and trends['rms_slope'] < -0.1:
                            emitter.emit(IntentType.EXECUTE_DROP)
                            current_intent = IntentType.IDLE

                    print(f"\rVibe: {current_intent.name: <15} | FFT Max: {max_fft:.2f} | Ducking: {latest_data['ducking']['freq']:.0f}Hz    ", end="")
            
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        reader.close()
        logger.close()

if __name__ == "__main__":
    main()
