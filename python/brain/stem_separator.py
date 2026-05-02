import numpy as np
import threading
import time
import os
from audio_separator.separator import Separator
from ipc.audio_bridge import AudioBridge

class StemSeparator:
    """
    Real-time stem separation worker.
    Uses audio-separator to isolate Vocals, Drums, Bass, and Other.
    """
    def __init__(self, model_name="htdemucs_ft.yaml"): # High-quality 4-stem model
        print(f"[STEM] Initializing Separator with model: {model_name}...")
        self.separator = Separator()
        # Optimize for CPU/GPU depending on availability
        import torch
        if torch.cuda.is_available():
            print("[STEM] CUDA detected. Using CUDAExecutionProvider for ONNX.")
            self.separator.onnx_execution_provider = "CUDAExecutionProvider"
        else:
            print("[STEM] CUDA not detected. Using CPUExecutionProvider.")
            self.separator.onnx_execution_provider = "CPUExecutionProvider"
            
        self.model_name = model_name
        
        # In a real 2025 scenario, we'd use a causal, streaming-optimized model.
        # audio-separator handles the heavy lifting of model management.
        if model_name != "MOCK":
            self.separator.load_model(model_name)
        
        self.bridge = AudioBridge()
        self.is_running = False
        self._thread = None
        self.rms_levels = {
            'vocal': 0.0,
            'drums': 0.0,
            'bass': 0.0,
            'other': 0.0
        }

    def start(self):
        if not self.bridge.connect():
            print("[STEM] Failed to connect to Audio Bridge. C# engine must be running.")
            return False
        
        self.is_running = True
        self._thread = threading.Thread(target=self._process_loop, daemon=True)
        self._thread.start()
        print("[STEM] Separation thread started.")
        return True

    def _process_loop(self):
        """
        Continuously reads raw audio from C#, separates it, and writes stems back.
        """
        while self.is_running:
            raw_pcm = self.bridge.read_input()
            
            if raw_pcm is not None:
                start_time = time.time()
                
                # audio-separator typically expects a file path, but we can pass 
                # a numpy array if we use its internal separation methods.
                # For this prototype, we mock the separation logic to verify the IPC bridge,
                # as full HTDemucs inference on 1024 samples is too heavy for a single loop.
                # Real implementation would use a sliding window/buffer.
                
                # MOCK: Pass-through separation for latency testing
                stems = {
                    'vocal': raw_pcm * 0.8,
                    'drums': raw_pcm * 1.2,
                    'bass': raw_pcm * 0.5,
                    'other': raw_pcm * 1.0
                }
                
                # Calculate real-time intensity for visualizer
                for name, data in stems.items():
                    # RMS calculation
                    rms = np.sqrt(np.mean(data**2)) if len(data) > 0 else 0
                    # Convert to approximate dB scale or just keep linear for shader
                    self.rms_levels[name] = float(rms)

                self.bridge.write_stems(stems)
                
                elapsed = (time.time() - start_time) * 1000
                # print(f"\r[STEM] Block Processed: {elapsed:.2f}ms    ", end="")
            else:
                time.sleep(0.005) # Wait for next audio block

    def stop(self):
        self.is_running = False
        if self._thread:
            self._thread.join()
        self.bridge.close()

if __name__ == "__main__":
    # Standalone test mode
    worker = StemSeparator()
    if worker.start():
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            worker.stop()
