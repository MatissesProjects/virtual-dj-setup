# Track 15: Low-Latency Stem Separation (Neural De-mixing)

## Overview
Enable the AI to manipulate individual components of a track (Vocals, Drums, Bass) in real-time. This moves beyond simple EQ cutting to surgical "de-mixing," allowing for mashups and transitions where the vocals of one track play over the instrumental of another with high fidelity.

## Requirements
- Integrate a low-latency stem separation model (e.g., a distilled Demucs or Spleeter-based U-Net).
- Process separation in a dedicated Python background thread.
- Expose separated stem buffers back to the C# engine for independent DSP (EQ, FX).

## Documents
- [Specification](./spec.md)
- [Implementation Plan](./plan.md)
