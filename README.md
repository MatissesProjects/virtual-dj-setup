# 🎧 Virtual DJ Setup: AI-Collaborative Mixing Engine

A high-performance, real-time DJ system that bridges C# digital signal processing (DSP) with Python-based neural intelligence. Designed for live broadcast and autonomous mixing.

## 🚀 The "Power Move" Architecture

This project utilizes **Memory-Mapped Files (MMF)** with a **Lock-Free Ring Buffer** to achieve single-digit microsecond latency between the audio engine and the AI layer.

- **Audio Engine (C#):** Low-level WASAPI capture, professional DSP chain (Dynamics, Stereo Width, M/S Matrix), and sample-accurate automation.
- **Intelligence Layer (Python):** Real-time spectral analysis, predictive trend detection, and Reinforcement Learning (RL) using Gymnasium.
- **Human-in-the-Loop:** Bi-directional "Shadow Mode" where the AI learns from human manual overrides in real-time.

---

## ✨ Key Features

### 1. Neural Feature Extraction
Treats audio as an image. C# streams high-resolution **1024-bin FFT arrays** 60 times a second to Python, enabling CNN-based semantic understanding (e.g., detecting vocals vs. drums).

### 2. Spline-Based "Ghost Faders"
Eliminates "zipper noise." The AI sends mathematical Bezier curve coordinates, and the C# engine executes smooth, sample-accurate parameter ramps internally.

### 3. Semantic Audio Ducking
Intelligent, frequency-specific sidechaining. The AI detects frequency clashes (e.g., Deck A vocals masking Deck B synths) and applies surgical EQ dips to carve out space automatically.

### 4. The Hyperbolic Time Chamber
A **Headless Simulation Gym**. Decouples the DSP engine from the system clock to train RL agents at 100x real-time speed using standard `gymnasium` environments.

### 5. Shadow Mode & Authority
A bi-directional control system. The AI yields instantly to human MIDI/Keyboard input and logs the state-action pairs to a SQLite database for behavioral cloning.

---

## 🛠️ Tech Stack

- **Core:** C# (.NET 8.0) + NAudio
- **Intelligence:** Python 3.10+ + PyTorch + Gymnasium
- **IPC:** Memory-Mapped Files (Shared RAM)
- **UI:** Vue 3 + WebSockets + Tailwind-ish CSS
- **LLM:** Ollama (Llama 3 / Qwen) for local chord prediction

---

## 🏃 How to Run

### 1. Requirements
- Windows (for WASAPI/MMF support)
- [.NET 8.0 SDK](https://dotnet.microsoft.com/download/dotnet/8.0)
- [Python 3.10+](https://www.python.org/)
- [Ollama](https://ollama.com/) (running locally)

### 2. Live Mode (Real-time)
1. **Start the Engine:**
   ```powershell
   dotnet run --project src/VirtualDj.Engine/VirtualDj.Engine.csproj
   ```
2. **Start the Brain:**
   ```powershell
   cd python
   pip install -r requirements.txt
   python main.py
   ```
3. **Open Dashboard:** Open `ui/index.html` in your browser.

### 3. Sim Mode (RL Training)
```powershell
# Headless Engine
dotnet run --project src/VirtualDj.Engine/VirtualDj.Engine.csproj -- --headless "path/to/track.wav"

# Gymnasium Env
python python/brain/dj_env.py
```

---

## 📋 Roadmap
- [x] WASAPI Loopback Capture
- [x] Lock-Free Ring Buffer IPC
- [x] Semantic Ducking (Dynamic EQ)
- [x] Shadow Mode Behavioral Logging
- [x] Gymnasium Simulation Environment
- [ ] Multi-Deck Crossfader Logic
- [ ] CNN-based Spectrogram Analysis
- [ ] DMX/Light Sync Integration

---
*Built for the next generation of AI-augmented performances.* 🎹🔥
