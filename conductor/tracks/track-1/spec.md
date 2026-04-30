# Specification: Project Scaffolding & MVP Audio Capture

## Overview
This track focuses on the foundational setup. We need a C# solution that can capture audio from the system (browser/YouTube/Spotify) and a Python environment ready for future AI work.

## Requirements
1.  **C# Project Structure:**
    -   A .NET 8.0 Console application (or library + host).
    -   Integration of NAudio.
    -   Basic WASAPI Loopback capture implementation.
2.  **Python Environment:**
    -   A `python/` directory with a virtual environment or `pyproject.toml`/`requirements.txt`.
3.  **Basic Verification:**
    -   Print RMS levels of the captured audio to the console to prove it works.

## Success Criteria
- [x] C# solution builds and runs.
- [x] Audio capture starts without errors.
- [x] RMS levels are printed to the console in real-time.
- [x] Python environment is initialized.
