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
from pydantic import BaseModel
from brain.audio_classifier import AudioClassifier
from brain.stem_separator import StemSeparator
from brain.music_analyzer import MusicAnalyzer
from brain.bridge_generator import BridgeGenerator
from brain.audience_listener import AudienceListener
from brain.youtube_deck import YouTubeDeck
from brain.set_orchestrator import SetOrchestrator
from logger.state_action_logger import StateActionLogger

# Sync with C# playlist
PLAYLIST = [
    {"title": "Get Lucky", "artist": "Daft Punk"},
    {"title": "Blinding Lights", "artist": "The Weeknd"},
    {"title": "Levitating", "artist": "Dua Lipa"}
]

# Track 19: YouTube Automation
deck_a_browser = YouTubeDeck("Deck A")
deck_b_browser = YouTubeDeck("Deck B")
orchestrator = None # Global for main loop/API access

class SetStart(BaseModel):
    urls: list[str]

@app.post("/start_set")
async def start_set(start: SetStart):
    orchestrator.start_set(start.urls)
    return {"status": "ok"}

@app.post("/transition")
async def transition():
    orchestrator.trigger_transition()
    return {"status": "ok"}

# Web Server for UI
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

connected_websockets = set()
latest_data = {
    "vibe": "IDLE", "authority": "AI", "rms": -60, "centroid": 0, "chords": [], 
    "ducking": {"freq": 0, "gain": 0}, "xfader": 0.5, 
    "classification": {"class": "Unknown", "confidence": 0},
    "stems": {"vocal": 1.0, "drums": 1.0, "bass": 1.0, "other": 1.0},
    "crowd": {"vibe": 0.0, "hype": 0.0, "status": "NEUTRAL"}
}

class StemsUpdate(BaseModel):
    vocal: float
    drums: float
    bass: float
    other: float

class TrackLoad(BaseModel):
    deck: int
    url: str

@app.post("/load_track")
async def load_track(load: TrackLoad):
    if load.deck == 0:
        deck_a_browser.load_track(load.url)
    else:
        deck_b_browser.load_track(load.url)
    return {"status": "ok"}


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

@app.post("/stems")
async def update_stems(stems: StemsUpdate):
    latest_data["stems"]["vocal"] = stems.vocal
    latest_data["stems"]["drums"] = stems.drums
    latest_data["stems"]["bass"] = stems.bass
    latest_data["stems"]["other"] = stems.other
    return {"status": "ok"}

@app.post("/generate-bridge")
async def generate_bridge(duration: int = 8):
    print(f"\n[AI] Generative Bridge requested ({duration}s)...")
    # For prototype, use mock anchors. Real version analyzes PLAYLIST.
    anchor_a = {"key": "C", "style_prompt": "Deep House at 124 BPM"}
    anchor_b = {"key": "G", "style_prompt": "Melodic Techno at 128 BPM"}
    
    bridge = bridge_gen.generate_bridge(anchor_a, anchor_b, duration_sec=duration)
    
    if bridge:
        try:
            # Send to AI machine (or local server) via management port
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(('localhost', 8888)) 
                pcm_bytes = bridge['audio'].tobytes()
                s.sendall(struct.pack('i', len(pcm_bytes)))
                s.sendall(pcm_bytes)
            
            # Emit Intent to C# to activate the bridge deck
            emitter.emit(IntentType.GENERATE_BRIDGE)
            return {"status": "ok", "prompt": bridge['prompt']}
        except Exception as e:
            print(f"[BRIDGE] Error sending to server: {e}")
            return {"status": "error", "message": str(e)}
            
    return {"status": "failed"}

def run_web_server():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="error")

def main():
    threading.Thread(target=run_web_server, daemon=True).start()
    
    global emitter, bridge_gen
    reader = SharedMemoryReader()
    emitter = IntentEmitter()
    analyzer = TrendAnalyzer(window_size=60)
    chord_predictor = ChordPredictor()
    clash_detector = ClashDetector()
    spec_builders = {0: SpectrogramBuilder(), 1: SpectrogramBuilder()}
    classifier = AudioClassifier()
    
    bridge_gen = BridgeGenerator()
    audience = AudienceListener() # Simulator mode by default
    audience.run_in_thread()

    # Track 15: Stem Separation
    stem_worker = StemSeparator()
    stem_worker.start()

    # Track 19: YouTube Automation
    deck_a_browser.start_in_thread()
    deck_b_browser.start_in_thread()

    global orchestrator
    orchestrator = SetOrchestrator(deck_a_browser, deck_b_browser, emitter)

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
                
                # Sync Stems from UI to C#
                s = latest_data["stems"]
                reader.write_stem_volumes(s["vocal"], s["drums"], s["bass"], s["other"])

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
                latest_data["crowd"] = audience.get_vibe_report()
                latest_data["rms"] = 20 * (features['rms'] + 0.000001)
                latest_data["centroid"] = features['centroid']
                latest_data["authority"] = authority
                latest_data["vibe"] = current_intent.name
                latest_data["chords"] = current_chords
                latest_data["stems_rms"] = stem_worker.rms_levels
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
main()
