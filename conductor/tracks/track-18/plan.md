# Implementation Plan: Stem-Aware Shader Visuals

## Phase 1: Three.js Scaffolding
- [ ] Add `three` library via CDN to `ui/index.html`.
- [ ] Create a `Visualizer.vue` component (or integrated Vue setup) to manage the canvas.
- [ ] Implement a basic "Hello World" shader to verify the WebGL context.

## Phase 2: Reactive Uniform Pipeline
- [ ] Extend the Vue `onmessage` handler to feed audio features into a reactive `uniforms` object.
- [ ] Implement a `LERP` (Linear Interpolation) engine to smooth out the transition of uniform values between data frames.
- [ ] Verify that `uDrums` flashes on percussive peaks.

## Phase 3: Stem-Aware Shader Art
- [ ] Develop the final `fragment_shader.glsl`.
- [ ] Implement "Stem Layering": e.g., vocals drive a central aura, drums drive background ripples, bass drives screen distortion.
- [ ] Wire up the `GENERATE_BRIDGE` and `CREATE_TENSION` intents to global shader states (e.g., glitch effects).
