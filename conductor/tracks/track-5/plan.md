# Implementation Plan: Predictive Mixing & Intent Schema

## Phase 1: Intent Schema & IPC Back-channel
- [x] Define `IntentType` enum in both C# and Python.
- [x] Setup ZeroMQ (or simple TCP sockets) for command transmission.
- [x] Implement `IntentListener` in C#.

## Phase 2: Python Predictive Logic
- [x] Implement `TrendAnalyzer.py` to track historical features.
- [x] Create simple rules or a small model to map trends to intents.
- [x] Implement the `IntentEmitter` in Python.

## Phase 3: C# Macro Execution
- [x] Create `IntentExecutor.cs`.
- [x] Implement ramping logic for Compressor/Limiter/Width/EQ.
- [x] Test the full loop: Audio Trend -> Python Intent -> C# DSP Macro.
