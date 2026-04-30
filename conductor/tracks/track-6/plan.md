# Implementation Plan: Manual Override & Shadow Mode

## Phase 1: Authority Management
- [ ] Add `ControlAuthority` enum and state to `DspPipeline.cs`.
- [ ] Update `IntentExecutor` to check authority before applying macros.
- [ ] Update `SharedMemoryService` to include the `ControlAuthority` flag.

## Phase 2: Action Vector & Logging
- [ ] Create `python/logger/state_action_logger.py` using SQLite.
- [ ] Define the Action Vector schema in Python.
- [ ] Implement the "Shadow Mode" logic in `python/main.py`.

## Phase 3: Validation
- [ ] Simulate manual overrides and verify logging starts.
- [ ] Inspect the SQLite database to ensure data is being captured correctly.
