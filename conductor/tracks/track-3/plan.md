# Implementation Plan: Python Intelligence Layer & Shared Memory IPC

## Phase 1: C# Shared Memory Implementation
- [x] Create `SharedMemoryService.cs`.
- [x] Implement binary serialization for `FeatureFrame`.
- [x] Update `Program.cs` to write features to memory.

## Phase 2: Python IPC & Consumer
- [x] Create `python/ipc/shared_memory.py` using `mmap`.
- [x] Implement deserialization matching the C# binary format.
- [x] Create `python/main.py` to test the connection.

## Phase 3: Validation & Logging
- [x] Verify data integrity across the IPC boundary.
- [ ] Implement basic state logging in Python (SQLite shell).
