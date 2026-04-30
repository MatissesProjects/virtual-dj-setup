# Implementation Plan: Chord Retrieval & Playlist Management

## Phase 1: Playlist & Basic Lookup
- [x] Create `PlaylistManager.cs` in C#.
- [ ] Implement a simple Hooktheory client in Python (or C#).
- [x] Update `SharedMemoryService` to include `CurrentSongId` or similar metadata.

## Phase 2: Local AI Chord Prediction
- [x] Implement a `ChordPredictor` in Python using a local LLM (e.g., Llama 3 via Ollama) to "guess" chords for common songs.
- [ ] (Optional) Integrate a lightweight audio-to-chord model (like Basic Pitch or a pre-trained CNN).

## Phase 3: Intelligence Integration
- [x] Update `python/brain/trend_analyzer.py` to accept chord context.
- [ ] Implement a "Harmonic Tension" metric based on chord progressions.
- [x] Refine `CREATE_TENSION` trigger based on upcoming chord changes (e.g., approaching a V7 chord).
