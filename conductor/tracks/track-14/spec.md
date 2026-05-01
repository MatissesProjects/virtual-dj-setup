# Specification: CNN-based Spectrogram Analysis

## Overview
The goal is to enable the AI to "see" the music. By stacking FFT frames into a 2D spectrogram, we can use computer vision techniques (CNNs) to classify sections of the track.

## Requirements
1.  **Spectrogram Reconstruction (Python):**
    -   Buffer the incoming 1024-bin FFT arrays over time (e.g., a rolling window of 128 frames).
    -   Convert this buffer into a 2D NumPy array (the "image").
2.  **CNN Model Integration:**
    -   Implement a lightweight CNN (using PyTorch or TensorFlow/Keras) or integrate a pre-trained model (e.g., a simplified YAMNet or custom classifier).
    -   The model should output probabilities for classes: `Vocal`, `Drums`, `Other`.
3.  **Real-time Inference:**
    -   Run inference every ~250ms without blocking the main IPC loop.
    -   Expose the classification results (e.g., `is_vocal: true`) to the `TrendAnalyzer`.
4.  **UI Feedback:**
    -   Optionally stream the reconstructed spectrogram to the Vue UI for visualization.

## Success Criteria
- [ ] Python reconstructs a valid 1024x128 spectrogram from shared memory.
- [ ] CNN successfully identifies vocal sections with >80% accuracy in local tests.
- [ ] Inference runs with <50ms latency.
