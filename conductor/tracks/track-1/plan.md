# Implementation Plan: Project Scaffolding & MVP Audio Capture

## Phase 1: Repository Scaffolding
- [x] Create `src/` directory for C# code.
- [x] Initialize .NET Solution and Project (`VirtualDjEngine`).
- [x] Add `NAudio` NuGet package.
- [x] Create `python/` directory.
- [x] Initialize Python environment (venv + requirements).

## Phase 2: MVP Audio Capture
- [x] Implement `WasapiCaptureService` in C#.
- [x] Configure `WasapiLoopbackCapture`.
- [x] Implement a simple `DataAvailable` handler to calculate RMS.
- [x] Wire up a console host to start/stop the capture.

## Phase 3: Validation
- [ ] Run the engine and verify audio levels are being printed.
- [ ] Check for any latency or buffer issues in this initial phase.
