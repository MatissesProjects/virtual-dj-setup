# Implementation Plan: Semantic Audio Ducking (Dynamic Masking)

## Phase 1: Engine Refactoring & Dynamic EQ
- [ ] Create `VirtualDeck.cs` to encapsulate Buffer, DspPipeline, and Playback.
- [ ] Implement `DynamicEqNode.cs` (Biquad Peaking Filter).
- [ ] Update `IntentExecutor` to support frequency-specific commands.

## Phase 2: Python Masking Analysis
- [ ] Update `SharedMemoryReader` to handle data from multiple decks.
- [ ] Implement `ClashDetector.py` to compare FFT arrays.
- [ ] Implement the logic to select the "Leader" and "Follower" decks.

## Phase 3: Live Integration
- [ ] Wire the `ClashDetector` to the `IntentEmitter`.
- [ ] Test with a vocal track on Deck A and a synth track on Deck B.
- [ ] Visualize the EQ dips in the Vue UI.
