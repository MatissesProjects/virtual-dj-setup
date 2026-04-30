# Implementation Plan: Basic DSP Chain & Feature Extraction

## Phase 1: Buffering & FFT Setup
- [x] Implement `AudioBufferManager` to handle overlapping windows for FFT.
- [x] Integrate NAudio's FastFourierTransform.
- [x] Create a `DspPipeline` class to orchestrate processing.

## Phase 2: Feature Extraction
- [x] Implement `RmsProvider`.
- [x] Implement `SpectralCentroidProvider`.
- [x] Implement `PeakFrequencyProvider`.
- [x] Define `FeatureFrame` struct for data transfer.

## Phase 3: Integration & Testing
- [x] Wire the `DspPipeline` to the `WasapiCaptureService`.
- [x] Add a "Debug View" to Program.cs to show extracted features in real-time.
- [ ] Profile the DSP code to ensure minimal latency.
