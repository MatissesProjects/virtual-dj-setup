# Implementation Plan: Hardware/MIDI Integration & Vue UI

## Phase 1: MIDI & Manual Authority
- [x] Implement `MidiService.cs` in C#.
- [x] Map CC messages to `DspPipeline` parameters.
- [x] Verify `ForceManualOverride` is triggered by MIDI.

## Phase 2: Python Web Services
- [x] Add `fastapi` and `uvicorn` to `requirements.txt`.
- [x] Implement a WebSocket endpoint in `python/main.py` or a dedicated service.
- [x] Broadcast Feature Frames and Vibe State.

## Phase 3: Vue Dashboard
- [x] Scaffold Vue 3 app in `ui/`.
- [x] Implement real-time charts for Spectral data.
- [x] Add controls for manual override and AI takeover.
