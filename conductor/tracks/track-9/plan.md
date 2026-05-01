# Implementation Plan: The MMF Power Move & Neural Bridge

## Phase 1: Robust Synchronization
- [x] Implement `SynchronizedSharedMemory.cs` using a ping-pong buffer strategy. (Implemented Lock-Byte sync in SharedMemoryService)
- [x] Add a "Sequence Number" or "Write Lock" byte to the header.
- [x] Implement the corresponding reader in Python using `mmap` with lock-aware reading.

## Phase 2: High-Bandwidth Feature Extraction
- [x] Update `DspPipeline.cs` to calculate and export full 1024-bin FFT magnitudes.
- [x] Map the MMF to a large enough segment (~8KB per frame).
- [ ] Create `SpectrogramGenerator.py` in Python to verify the stream.

## Phase 3: Vector Automation (The Ghost Fader)
- [x] Define `AutomationCurve` struct (Start, End, Type, Duration). (Implemented as target/duration in C#)
- [x] Implement `SplineInterpolator.cs` in the C# engine.
- [x] Update `IntentExecutor` to send Curves instead of stepped values.

## Phase 4: Neural Onset (Light Sync)
- [ ] Implement a simple energy-based onset detector in C#.
- [ ] Write `IsPeak` boolean to MMF.
- [ ] Create `LightSync.py` mockup to verify near-zero latency.
