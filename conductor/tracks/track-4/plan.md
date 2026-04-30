# Implementation Plan: Professional DSP Chain (Dynamics & Stereo)

## Phase 1: Dynamics Nodes
- [ ] Implement `CompressorNode.cs` (RMS detection, gain reduction).
- [ ] Implement `LimiterNode.cs` (Simple look-ahead or hard clipper).
- [ ] Add dynamics to the `DspPipeline`.

## Phase 2: Stereo & M/S
- [ ] Implement `MsMatrix.cs` (L/R -> M/S and M/S -> L/R).
- [ ] Implement `StereoWidthNode.cs` (Gain control on the Side signal).
- [ ] Integrate M/S routing into the pipeline.

## Phase 3: Validation
- [ ] Visual verification of gain reduction in the console.
- [ ] Listen/Test with high-dynamic range audio to ensure the "glue" effect.
