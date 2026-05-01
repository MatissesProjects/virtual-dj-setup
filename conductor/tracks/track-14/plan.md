# Implementation Plan: CNN-based Spectrogram Analysis

## Phase 1: Spectrogram Generation
- [x] Create `python/brain/spectrogram_builder.py` to manage the rolling FFT buffer.
- [x] Implement a `get_spectrogram()` method that returns a normalized 2D NumPy array.
- [x] Add visualization script `python/tools/view_spectrogram.py` to verify data integrity.

## Phase 2: CNN Model Implementation
- [x] Design a simple 3-layer CNN architecture optimized for 1D/2D audio features.
- [x] Integrate the model into `python/brain/audio_classifier.py`. (Added Dropout for generalization)
- [x] Implement training infrastructure (`train_audio_cnn.py`) with support for synthetic and real data.
- [x] Create data collection utility (`collect_data.py`) to gather real labeled samples.
- [ ] (Optional) Load a pre-trained "Stem Detection" or "Vocal Detection" model.

## Phase 3: Real-time Integration
- [x] Hook `audio_classifier.py` into the main `python/main.py` loop.
- [x] Add CNN classification display to the Vue UI dashboard.
- [ ] Update `SharedMemoryReader` if additional metadata is needed.
- [x] Test real-time classification on various audio tracks. (System integrated)
