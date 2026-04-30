# Specification: Python Intelligence Layer & Shared Memory IPC

## Overview
The C# engine extracts audio features, but the heavy lifting of mixing logic and AI inference happens in Python. To maintain microsecond latency, we use Shared Memory for streaming the `FeatureFrame` data.

## Requirements
1.  **C# IPC Side:**
    -   Implement `SharedMemoryService` using `MemoryMappedFile`.
    -   Serialize `FeatureFrame` into a binary format (or JSON for simplicity initially, but binary is preferred for performance).
2.  **Python IPC Side:**
    -   Use `mmap` to read the shared memory segment.
    -   Implement a consumer that reads features at high frequency.
3.  **Basic Intelligence Shell:**
    -   A Python script that prints the features received from C#.
    -   Basic logic to "suggest" an action based on features (e.g., "High spectral centroid detected - recommend EQ cut").

## Success Criteria
- [x] C# writes features to Shared Memory without blocking the audio thread.
- [x] Python reads and deserializes features correctly.
- [x] Latency between extraction and reception is minimal (verified by timestamps).
