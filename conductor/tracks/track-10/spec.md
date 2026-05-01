# Specification: Virtual Decks & Time-Stretching

## Overview
To manipulate tempo without changing pitch (Time-Stretching) or change both (Playback Speed), we must transition from a "Pass-through" model to a "Buffered Deck" model.

## Requirements
1.  **Circular Audio Buffering:**
    -   Implement a high-performance `CircularAudioBuffer` to store ~5-10 seconds of captured PCM data.
2.  **Time-Stretching Engine:**
    -   Implement a WSOLA (Waveform Similarity Overlap-Add) algorithm for high-quality tempo changes (±20%) without pitch artifacts.
3.  **Playback Speed Control:**
    -   Enable a "Vinyl Style" speed control that modifies both tempo and pitch simultaneously.
4.  **Output Routing:**
    -   Add a `PlaybackService` using NAudio `WasapiOut` to play back the modified buffer.
5.  **Synchronization:**
    -   Ensure the Intelligence Layer can control the `Tempo` and `PlaybackRate` via MMF.

## Success Criteria
- [ ] Audio is successfully buffered and replayed with minimal latency.
- [ ] Tempo can be modified in real-time (e.g., 120BPM to 125BPM) without pitch shift.
- [ ] No audio glitches or artifacts during speed transitions.
