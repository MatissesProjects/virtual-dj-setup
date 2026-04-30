# Implementation Plan: Hardware/MIDI Integration & Vue UI

## Phase 1: MIDI & Manual Authority
- [ ] Implement `MidiService.cs` in C#.
- [ ] Map CC messages to `DspPipeline` parameters.
- [ ] Verify `ForceManualOverride` is triggered by MIDI.

## Phase 2: Python Web Services
- [ ] Add `fastapi` and `uvicorn` to `requirements.txt`.
- [ ] Implement a WebSocket endpoint in `python/main.py` or a dedicated service.
- [ ] Broadcast Feature Frames and Vibe State.

## Phase 3: Vue Dashboard
- [ ] Scaffold Vue 3 app in `ui/`.
- [ ] Implement real-time charts for Spectral data.
- [ ] Add controls for manual override and AI takeover.
