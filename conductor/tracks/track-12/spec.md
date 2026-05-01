# Specification: The Hyperbolic Time Chamber (Simulation Gym)

## Overview
Live training of Reinforcement Learning (RL) agents on audio is prohibitively slow because audio runs in real-time (1 second of audio = 1 second of compute). To evolve mixing policies quickly, the engine must process audio offline and interface with Python as an RL Environment.

## Requirements
1.  **Headless Mode (C#):**
    -   Add a `--headless` CLI flag to the C# engine.
    -   Bypass `WasapiCaptureService` and `WasapiOut`.
    -   Read raw WAV files directly into memory and process blocks through the `DspPipeline` in a tight `while` loop (no `Thread.Sleep`).
2.  **Environment Sync (IPC):**
    -   Update the MMF protocol so Python can "step" the C# engine by a set number of frames.
    -   Python sends an action, tells C# to advance X milliseconds, and waits for C# to write the new observation back.
3.  **Gymnasium Wrapper (Python):**
    -   Create `VirtualDjEnv(gymnasium.Env)` in Python.
    -   Define the Observation Space: A normalized vector of RMS, Centroid, Chords, etc.
    -   Define the Action Space: Continuous actions for Width, Compression Ratio, Ducking parameters.
    -   Define a Reward Function (e.g., penalize high-energy clashes, reward smooth transitions).

## Success Criteria
- [x] C# engine processes a 3-minute song in seconds (10x+ speed).
- [x] Python can step the C# engine deterministically.
- [x] The system exposes a standard `gymnasium` API for RL algorithms (PPO, SAC).
