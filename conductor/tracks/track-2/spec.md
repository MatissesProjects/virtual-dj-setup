# Specification: Basic DSP Chain & Feature Extraction

## Overview
To enable AI-driven mixing, the engine must extract features from the raw PCM data. This track covers the implementation of a basic DSP chain that performs frequency analysis and temporal feature extraction.

## Requirements
1.  **Buffered Processing:**
    -   Implement a buffering mechanism to handle chunks of audio for FFT analysis (e.g., 2048 samples).
2.  **FFT Implementation:**
    -   Use NAudio's FFT or a high-performance alternative (like MathNet.Numerics if needed, but NAudio is preferred for now).
3.  **Feature Extraction:**
    -   **RMS:** Temporal energy levels.
    -   **Spectral Centroid:** A measure of "brightness".
    -   **Peak Frequency:** Identifying the dominant frequency.
4.  **Feature Packaging:**
    -   Structure these features into a `FeatureFrame` that can be easily passed to IPC later.

## Success Criteria
- [x] Raw audio is successfully buffered and processed through an FFT.
- [x] Spectral Centroid calculation is accurate.
- [x] Performance remains within real-time constraints (low CPU overhead).
- [x] Features are logged or displayed for verification.
