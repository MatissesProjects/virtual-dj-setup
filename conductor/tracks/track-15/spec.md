# Specification: Low-Latency Stem Separation

## Overview
Transform the audio engine from a stereo mixer into a stem-aware performance rig. This track implements the "Neural Bridge"—a high-bandwidth IPC pipeline that sends raw audio to Python for real-time separation and receives four discrete stems back for independent processing.

## Requirements
1.  **Distributed Audio IPC (C# <-> Remote Python):**
    -   Support both Local (MMF) and Remote (TCP/ZeroMQ) streaming modes.
    -   Implement high-performance PCM serialization for network transport.
    -   Add a "Remote AI IP" configuration to the engine.
2.  **Neural De-mixing Engine (Remote Python):**
    -   Integrate a causal, low-latency model (e.g., **HS-TasNet** or **ONNX-Distilled HTDemucs**).
    -   Optimize for multi-node setups where Python runs on a dedicated GPU server.
3.  **Jitter & Latency Management:**
    -   Implement a small jitter buffer in C# to handle network fluctuations during remote processing.
4.  **Stem-Aware Mixing Bus (C#):**
    -   Create `StemDeck` objects that can receive and sum the four incoming streams.
    -   Expose Gain/EQ/FX controls for each stem independently in the UI.

## Success Criteria
- [x] Round-trip latency (C# -> Python -> C#) is <150ms.
- [x] AI can successfully isolate vocals from a track with minimal audible artifacts.
- [x] Each stem (Vocals, Drums, Bass, Other) can be muted/soloed in the Vue dashboard.
