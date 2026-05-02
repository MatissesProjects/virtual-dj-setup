# Implementation Plan: Stem-Aware Shader Visuals

## Phase 1: Three.js Scaffolding
- [x] Add `three` library via CDN to `ui/index.html`.
- [x] Create a `Visualizer.vue` component (or integrated Vue setup) to manage the canvas.
- [x] Implement a basic "Hello World" shader to verify the WebGL context.

## Phase 2: Reactive Uniform Pipeline
- [x] Extend the Vue `onmessage` handler to feed audio features into a reactive `uniforms` object.
- [x] Implement a `LERP` (Linear Interpolation) engine to smooth out the transition of uniform values between data frames.
- [x] Verify that `uDrums` flashes on percussive peaks.

## Phase 3: Stem-Aware Shader Art
- [x] Develop the final `fragment_shader.glsl`.
- [x] Implement "Stem Layering": e.g., vocals drive a central aura, drums drive background ripples, bass drives screen distortion.
- [x] Wire up the `GENERATE_BRIDGE` and `CREATE_TENSION` intents to global shader states (e.g., glitch effects).
