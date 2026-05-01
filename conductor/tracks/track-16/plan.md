# Implementation Plan: Generative "Bridge" Transitions

## Phase 1: Symbolic Anchor Extraction
- [ ] Create `python/brain/music_analyzer.py` to detect Key/Scale/Tempo anchors.
- [ ] Implement symbolic representation of "Song End" and "Song Start" contexts.
- [ ] Verify anchor extraction on existing playlist tracks.

## Phase 2: Transformer Model Implementation
- [ ] Design/Integrate a lightweight MIDI Transformer for sequence infilling.
- [ ] Implement `bridge_generator.py` with style-interpolation parameters (Energy, Complexity).
- [ ] Test bridge generation quality in isolation (saving to .mid files).

## Phase 3: Synthesis & Real-time Integration
- [ ] Integrate a PCM synthesizer (e.g., `pretty_midi` with FluidSynth) into the Python pipeline.
- [ ] Update `IntentExecutor.cs` and `MasterMixer.cs` to handle the `BridgeDeck`.
- [ ] Test the full A -> AI Bridge -> B transition loop.
