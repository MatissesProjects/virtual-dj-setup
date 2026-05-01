# Implementation Plan: Multi-Deck Crossfader Logic

## Phase 1: Multi-Deck Audio Routing
- [x] Refactor `Program.cs` to manage `DeckA` and `DeckB`.
- [x] Create a `MasterMixer.cs` to sum the outputs of both decks.
- [x] Ensure WASAPI capture can feed both decks (or separate inputs if available).

## Phase 2: Crossfader Node
- [x] Implement `Crossfader.cs` with Gain calculation logic.
- [x] Implement Linear and Equal Power (cos/sin) curves.
- [x] Integrate the `Crossfader` into the `MasterMixer`.

## Phase 3: AI & UI Control
- [x] Add `CrossfaderPosition` to `SharedMemoryService` and Python reader.
- [ ] Add `AUTO_CROSSFADE` intent to `IntentType` enum. (Deferred to future automation track)
- [x] Update Vue UI with a horizontal crossfader slider.
- [x] Test AI-triggered smooth transitions between Deck A and Deck B.
