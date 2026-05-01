# Specification: Multi-Deck Crossfader Logic

## Overview
A crossfader is the heart of DJ mixing. This track adds the ability to blend two discrete audio streams (Deck A and Deck B) with sample-accurate precision and smooth transition curves.

## Requirements
1.  **Multi-Deck Infrastructure:**
    -   Fully instantiate and process two `VirtualDeck` objects in the C# engine.
    -   Ensure both decks capture independent streams (or mock streams for testing).
2.  **Crossfader Node (C#):**
    -   Implement a `Crossfader` class that takes two audio buffers and a `position` (0.0 to 1.0).
    -   Support **Linear** and **Equal Power** curves to prevent volume drops at the center (0.5).
3.  **Automation & Interpolation:**
    -   Use the `SplineInterpolator` to allow the AI to trigger smooth "8-bar" crossfades.
4.  **IPC & UI:**
    -   Expose `CrossfaderPosition` in the MMF for Python to monitor and control.
    -   Add a visual Crossfader slider to the Vue dashboard.

## Success Criteria
- [x] Audio from both Deck A and Deck B is mixed and played back correctly.
- [x] Moving the crossfader smoothly transitions between sources without glitches.
- [x] Equal Power curve maintains consistent loudness across the transition.
- [ ] AI can trigger a timed crossfade via the Intent channel. (Partial: UI control implemented)
