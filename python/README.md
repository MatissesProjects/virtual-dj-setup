# Virtual DJ Intelligence Layer

This directory contains the Python-based intelligence layer for the Virtual DJ system.

## Setup
1. Create a virtual environment: `python -m venv venv`
2. Activate it: `.\venv\Scripts\activate` (Windows)
3. Install dependencies: `pip install -r requirements.txt`

## Components
- `brain/`: RL models and inference logic.
- `ipc/`: Communication logic with the C# engine.
- `logger/`: State-action logging to SQLite.
