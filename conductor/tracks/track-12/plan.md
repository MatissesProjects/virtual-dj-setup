# Implementation Plan: The Hyperbolic Time Chamber (Simulation Gym)

## Phase 1: Headless Mode (C#)
- [ ] Add `HeadlessHost.cs` for offline audio processing.
- [ ] Parse CLI arguments in `Program.cs` to trigger headless mode and load WAV files.
- [ ] Ensure `DspPipeline` can be ticked manually without a real-time soundcard clock.

## Phase 2: Step-based Synchronization (IPC)
- [ ] Expand MMF protocol with a `StepCommand` byte (Python tells C# to advance).
- [ ] Expand MMF protocol with a `StepSize` field (How many samples to process before pausing).
- [ ] Ensure C# waits for Python's "go" signal before processing the next block.

## Phase 3: Gymnasium Environment (Python)
- [ ] `pip install gymnasium`
- [ ] Create `dj_env.py` inheriting from `gymnasium.Env`.
- [ ] Implement `step()`, `reset()`, and `render()` methods.
- [ ] Implement a basic heuristic reward function (e.g., negative reward for clipping/clashing).
