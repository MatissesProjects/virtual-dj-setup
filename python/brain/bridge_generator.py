import requests
import os
import time
import numpy as np
import soundfile as sf
import io

class BridgeGenerator:
    """
    Client for the AudioSequencer Remote AI Server.
    Generates high-fidelity musical bridges using MusicGen.
    """
    def __init__(self, server_url="http://localhost:5000"):
        self.server_url = server_url
        print(f"[BRIDGE] Initializing Generator (Target: {server_url})...")

    def generate_bridge(self, anchor_a, anchor_b, duration_sec=8):
        """
        Calls the AudioSequencer server to generate a bridge.
        """
        print(f"[BRIDGE] Requesting bridge synthesis from {anchor_a['key']} to {anchor_b['key']}...")
        
        # 1. Construct a morphing prompt
        # We want to blend characteristics.
        prompt = f"A musical transition between two songs. " \
                 f"Source: {anchor_a['style_prompt']}. " \
                 f"Target: {anchor_b['style_prompt']}. " \
                 f"Smoothly morphing energy and harmony."
        
        payload = {
            "prompt": prompt,
            "duration": duration_sec
        }
        
        try:
            # Using the /generate endpoint identified in AudioSequencer
            response = requests.post(f"{self.server_url}/generate", json=payload, timeout=120)
            
            if response.status_code == 200:
                # Server returns a WAV file
                audio_data, samplerate = sf.read(io.BytesIO(response.content))
                print(f"[BRIDGE] Successfully generated {len(audio_data)} samples.")
                return {
                    "audio": audio_data.astype(np.float32),
                    "samplerate": samplerate,
                    "prompt": prompt
                }
            else:
                print(f"[BRIDGE] Error: Server returned status {response.status_code}")
                return None
        except Exception as e:
            print(f"[BRIDGE] Error connecting to AudioSequencer: {e}")
            return self._fallback_generation(anchor_a, anchor_b, duration_sec)

    def _fallback_generation(self, a, b, duration):
        """Minimal fallback if server is down."""
        print("[BRIDGE] Using local fallback synthesis.")
        # Just generate a rising frequency sweep for testing
        sr = 44100
        t = np.linspace(0, duration, int(duration * sr))
        # Logarithmic sweep
        sweep = np.sin(2 * np.pi * np.exp(np.linspace(np.log(440), np.log(880), len(t))) * t)
        return {
            "audio": sweep.astype(np.float32),
            "samplerate": sr,
            "prompt": "Local Sweep Fallback"
        }

if __name__ == "__main__":
    gen = BridgeGenerator()
    a = {"key": "C", "style_prompt": "Minimal Techno at 124 BPM"}
    b = {"key": "G", "style_prompt": "Deep House at 128 BPM"}
    # bridge = gen.generate_bridge(a, b, duration_sec=4)
