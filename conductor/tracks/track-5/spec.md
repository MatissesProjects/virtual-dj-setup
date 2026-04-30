# Specification: Predictive Mixing & Intent Schema

## Overview
The goal is to prevent the AI from making erratic, granular changes. Instead, it should select a high-level **Intent** (e.g., `CREATE_TENSION`), and the C# engine (or a middleware layer) should execute the corresponding DSP macro.

## Requirements
1.  **Intent Schema:**
    -   Define a JSON/binary schema for intents: `IDLE`, `CREATE_TENSION`, `EXECUTE_DROP`, `SMOOTH_BLEND`, `CLEAN_CUT`.
2.  **Predictive Model (Skeleton):**
    -   Implement a basic time-series buffer in Python to evaluate audio trends (e.g., "RMS is climbing steadily over 5 seconds").
    -   Trigger intents based on trend analysis.
3.  **Command IPC:**
    -   Establish a back-channel (gRPC or ZeroMQ) for Python to send intents to C#.
4.  **Intent Executor (C#):**
    -   Implement a state machine in C# that receives intents and ramps DSP parameters (e.g., ramping a High-Pass filter when `CREATE_TENSION` is active).

## Success Criteria
- [x] Python correctly identifies structural trends in the audio.
- [x] Intents are transmitted to C# with low latency.
- [x] C# executes smooth parameter ramps in response to high-level intents.
