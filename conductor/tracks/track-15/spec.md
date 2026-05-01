# Specification: Low-Latency Stem Separation

## Overview
Transform the audio engine from a stereo mixer into a stem-aware performance rig. This track implements the "Neural Bridge"—a high-bandwidth IPC pipeline that sends raw audio to Python for real-time separation and receives four discrete stems back for independent processing.

## Requirements
1.  **High-Speed Audio IPC (C# <-> Python):**
    -   Use Memory-Mapped Files (MMF) to stream raw 44.1kHz PCM data.
    -   Implement a double-buffering scheme to prevent read/write tearing.
2.  **Neural De-mixing Engine (Python):**
    -   Integrate a causal, low-latency model (e.g., **HS-TasNet** or **ONNX-Distilled HTDemucs**).
    -   Target <100ms processing latency per 1024-sample block.
3.  **Stem-Aware Mixing Bus (C#):**
    -   Create `StemDeck` objects that can receive and sum the four incoming streams.
    -   Expose Gain/EQ/FX controls for each stem independently in the UI.

## Success Criteria
- [ ] Round-trip latency (C# -> Python -> C#) is <150ms.
- [ ] AI can successfully isolate vocals from a track with minimal audible artifacts.
- [ ] Each stem (Vocals, Drums, Bass, Other) can be muted/soloed in the Vue dashboard.
