# Specification: The MMF Power Move & Neural Bridge

## Overview
Transitioning from simple numeric features to a "Computer Vision for Audio" approach. This requires a synchronized, high-bandwidth MMF bridge that eliminates the "tearing" problem and supports massive data transfer (full FFT arrays) and mathematical automation curves (splines).

## Requirements
1.  **Memory Synchronization:**
    -   Implement a multi-buffer system (ping-pong) or utilize **Named Semaphores/Mutexes** to ensure Python never reads while C# is writing.
2.  **Neural Feature Stream:**
    -   Expand the MMF layout to include a 1024/2048-bin **FFT Magnitude Array**.
    -   Python should reconstruct this into a spectrogram for local CNN analysis.
3.  **Vector Automation (Splines):**
    -   Define a `SplineAutomation` struct in the MMF to receive [TargetValue, DurationSamples, CurveTension].
    -   The C# engine must interpolate this sample-by-sample to prevent zipper noise.
4.  **Transient Flags:**
    -   Add a high-speed "Trigger Byte" for onset detection (Kick/Snare) for external sync.

## Success Criteria
- [ ] Full FFT arrays are received in Python without data corruption.
- [ ] Synchronization primitives prevent data tearing at high refresh rates.
- [ ] C# executes smooth Bezier-based fades based on a single MMF command.
- [ ] Latency remains in the single-digit microsecond range.
