# Implementation Plan: Virtual Decks & Time-Stretching

## Phase 1: Buffering & Playback
- [ ] Implement `CircularAudioBuffer.cs` (Thread-safe read/write).
- [ ] Implement `DeckPlaybackService.cs` (WasapiOut integration).
- [ ] Route `WasapiCaptureService` -> `CircularAudioBuffer` -> `WasapiOut`.

## Phase 2: Tempo Manipulation (WSOLA)
- [ ] Implement `WsolaNode.cs` for time-stretching.
- [ ] Implement `ResamplerNode.cs` (or use NAudio's) for playback speed changes.
- [ ] Add `Tempo` and `Pitch` parameters to `DspPipeline`.

## Phase 3: Integration & Control
- [ ] Update MMF to accept `Tempo` and `PlaybackSpeed` commands.
- [ ] Update the Vue UI with a "Tempo Slider".
- [ ] Verify the "Ghost Fader" can automate tempo transitions.
