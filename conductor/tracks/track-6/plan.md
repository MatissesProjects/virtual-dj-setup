# Implementation Plan: Manual Override & Shadow Mode

## Phase 1: Authority Management
- [x] Add `ControlAuthority` enum and state to `DspPipeline.cs`.
- [x] Update `IntentExecutor` to check authority before applying macros.
- [x] Update `SharedMemoryService` to include the `ControlAuthority` flag.

## Phase 2: Action Vector & Logging
- [x] Create `python/logger/state_action_logger.py` using SQLite.
- [x] Define the Action Vector schema in Python.
- [x] Implement the "Shadow Mode" logic in `python/main.py`.

## Phase 3: Validation
- [x] Simulate manual overrides and verify logging starts.
- [x] Inspect the SQLite database to ensure data is being captured correctly.
