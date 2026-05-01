# Specification: Generative "Bridge" Transitions

## Overview
Enable the AI to compose "musical glue" between tracks. This track implements the "Transformer Bridge"—a generative system that synthesizes a 4-8 bar musical sequence to seamlessly transition between two tracks that are rhythmically or harmonically incompatible.

## Requirements
1.  **Symbolic Track Analysis (Python):**
    -   Extract rhythmic and harmonic "anchors" (Key, Scale, Tempo, Kick Pattern) from the end of Track A and the start of Track B.
2.  **Transformer-Based Bridge Synthesis:**
    -   Implement or integrate a MIDI-based transformer (e.g., a variant of **MIDI-GPT**) for symbolic infilling.
    -   The model must generate a sequence that "interpolates" from Track A's characteristics to Track B's characteristics.
3.  **Real-time Synthesis & Playback:**
    -   Convert the generated MIDI bridge into PCM audio using a lightweight synthesizer (e.g., FluidSynth or a pre-trained **MT-MusicLDM** audio generator).
    -   Stream the bridge audio back to the C# engine via the `NetworkAudioBridge`.
4.  **Macro Intent Integration:**
    -   Trigger the bridge generation via a new `GENERATE_BRIDGE` intent.
    -   The C# engine must seamlessly transition from Deck A -> Bridge -> Deck B.

## Success Criteria
- [ ] AI generates a 4-bar bridge that matches the tempo of both source and target tracks.
- [ ] Harmonic transitions feel "natural" (avoiding dissonance during the bridge).
- [ ] End-to-end generation and playback start within <2 seconds of the intent trigger.
