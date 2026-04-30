# Specification: Hardware/MIDI Integration & Vue UI

## Overview
To provide a true professional DJ experience, we need tactile control and a rich visual interface.

## Requirements
1.  **MIDI Integration (C#):**
    -   Implement `MidiService` using NAudio.
    -   Map MIDI CC messages to DSP parameters (Width, Compression, EQ).
    -   Trigger `ForceManualOverride()` on any MIDI activity.
2.  **Web Backend (Python):**
    -   Integrate a WebSocket server (e.g., `FastAPI` or `websockets`) in Python.
    -   Broadcast real-time features and AI intent status to the frontend.
3.  **Vue Frontend:**
    -   Create a responsive Vue 3 dashboard.
    -   Visualize RMS, Spectral Centroid, and the active AI Vibe.
    -   Add virtual faders that can also trigger `ForceManualOverride()`.

## Success Criteria
- [x] Physical MIDI knob movement changes C# DSP parameters instantly.
- [x] Vue dashboard shows real-time frequency/vibe data from the Python brain.
- [x] Full end-to-end loop: MIDI -> C# -> Python (Shadow Mode) -> Vue (Viz).
