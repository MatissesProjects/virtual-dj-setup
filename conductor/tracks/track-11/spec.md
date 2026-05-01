# Specification: Semantic Audio Ducking (Dynamic Masking)

## Overview
When two audio sources overlap, they compete for the same frequency space. This track implements "Semantic Ducking" using Dynamic EQ to ensure clarity in the mix.

## Requirements
1.  **Dynamic EQ Node (C#):**
    -   Implement a Biquad filter (Peaking/Bell) with a real-time adjustable `Gain` parameter.
    -   Allow external control of the center frequency and Q-factor.
2.  **Frequency Analysis (Python):**
    -   Analyze the high-resolution FFT data from two virtual decks (or Deck A vs. Master).
    -   Identify "Frequency Clashes" (areas where both signals have high energy).
3.  **Intelligent Ducking Control:**
    -   Python sends specific EQ dip commands back to C# (e.g., "Dip 2.5kHz on Deck B by 6dB").
    -   The dip should only activate when the "Leader" (e.g., Deck A vocals) is active.
4.  **Multi-Deck Support:**
    -   Refactor the engine to support at least two discrete `VirtualDeck` objects.

## Success Criteria
- [ ] Two audio sources can play simultaneously without "muddiness".
- [ ] A dip is automatically applied to a specific frequency range when a clash is detected.
- [ ] No audible clicks or pops during dynamic EQ adjustments.
