# Implementation Plan: Professional DSP Chain (Dynamics & Stereo)

## Phase 1: Dynamics Nodes
- [x] Implement `CompressorNode.cs` (RMS detection, gain reduction).
- [x] Implement `LimiterNode.cs` (Simple look-ahead or hard clipper).
- [x] Add dynamics to the `DspPipeline`.

## Phase 2: Stereo & M/S
- [x] Implement `MsMatrix.cs` (L/R -> M/S and M/S -> L/R).
- [x] Implement `StereoWidthNode.cs` (Gain control on the Side signal).
- [x] Integrate M/S routing into the pipeline.

## Phase 3: Validation
- [x] Visual verification of gain reduction in the console.
- [ ] Listen/Test with high-dynamic range audio to ensure the "glue" effect.
