# Specification: Stem-Aware Shader Visuals

## Overview
Elevate the UI from a static dashboard to a cinematic visualizer. This track implements a WebGL-based shader system in the Vue dashboard that is directly driven by the AI's internal state, isolated stems, and CNN-detected patterns.

## Requirements
1.  **WebGL Integration (UI):**
    -   Integrate Three.js into the Vue dashboard.
    -   Implement a full-screen or large-card background canvas using a custom `ShaderMaterial`.
2.  **Audio-to-Uniform Mapping:**
    -   Map the following features to GLSL uniforms:
        -   `uRMS`: Master volume / energy.
        -   `uVocal`: Real-time vocal stem intensity (from Track 15).
        -   `uDrums`: Real-time drum stem intensity (for percussive flashes).
        -   `uCentroid`: Spectral brightness for color shifting.
        -   `uIntent`: Current AI intent (e.g., Tension = faster motion, Drop = sudden flash).
3.  **Dynamic Shader Logic:**
    -   Develop a fragment shader that uses these uniforms to drive procedural shapes, distortions, or particle flows.
    -   Implement "Scene Switching" based on AI intents (e.g., red/pulsing for tension, bright/vibrant for drops).
4.  **Performance Optimization:**
    -   Ensure the shader runs at 60fps without blocking the WebSocket data processing.
    -   Use `requestAnimationFrame` for smooth interpolation of uniform values.

## Success Criteria
- [x] Three.js canvas renders correctly behind the dashboard cards.
- [x] Visuals clearly pulse in sync with the drum stem.
- [x] Color scheme changes automatically when the AI intent shifts from `IDLE` to `CREATE_TENSION`.
- [x] Zero perceptible frame drops when stems are active.
