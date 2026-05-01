# Implementation Plan: Low-Latency Stem Separation

## Phase 1: The High-Bandwidth IPC Bridge
- [x] Create `SharedAudioBridge.cs` in C# to manage raw PCM MMFs.
- [x] Implement `audio_ipc.py` in Python for high-speed PCM reading/writing. (Implemented as `audio_bridge.py`)
- [x] Verify 44.1kHz stereo round-trip with zero loss.

## Phase 2: Python De-mixing Implementation
- [x] Integrate the `audio-separator` library with an ONNX-optimized model.
- [x] Implement `stem_separator.py` with a thread-safe streaming buffer.
- [x] Benchmark latency and optimize for CPU/GPU utilization. (ONNX execution providers added)

## Phase 3: C# Stem Integration & UI
- [x] Refactor `MasterMixer.cs` to handle `StemDeck` routing. (Reconstructs buffer from stems)
- [x] Create `StemControl.vue` component for the dashboard. (Added vertical sliders for stems)
- [x] Test real-time mashup capabilities (e.g., Deck A Drums + Deck B Vocals).
