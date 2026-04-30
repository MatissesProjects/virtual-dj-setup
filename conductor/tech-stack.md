# Tech Stack: Virtual DJ Setup

## Audio Engine (Core)
- **Language:** C# (.NET 8.0+)
- **Library:** NAudio (WASAPI, MIDI, DSP)
- **Threading:** SPSC (Single Producer/Single Consumer) Lock-free queues
- **IPC:** Memory-Mapped Files (Shared Memory) for raw data; gRPC or ZeroMQ for control messages.

## Intelligence Layer (The Brain)
- **Language:** Python
- **Frameworks:** PyTorch or TensorFlow (for RL and Inference)
- **Database:** SQLite (for time-series state-action logging)
- **Communication:** Local sockets/IPC to C# engine.

## Frontend (Control & Viz)
- **Framework:** Vue.js (as mentioned in the idea)
- **Protocol:** WebSockets (from Python backend or direct to C#)

## Infrastructure
- **OS:** Windows (Primary target due to WASAPI)
- **Source Control:** Git
