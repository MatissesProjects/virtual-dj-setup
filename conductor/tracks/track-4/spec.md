# Specification: Professional DSP Chain (Dynamics & Stereo)

## Overview
Raw capture is insufficient for a professional sound. This track adds the "glue" and "polish" nodes to the C# signal flow.

## Requirements
1.  **Dynamics Processing:**
    -   **Compressor:** Implement an RMS-based compressor (LA-2A style) with adjustable Threshold, Ratio, Attack, and Release.
    -   **Limiter:** Implement a Look-ahead Brickwall Limiter to ensure the master output never clips (Peak < 0dBFS).
2.  **Stereo Field Management:**
    -   **M/S Matrix:** Implement Mid/Side encoding and decoding.
    -   **M/S EQ:** Allow independent equalization of the Mid (center/punch) and Side (width/ambient) signals.
3.  **Control Integration:**
    -   Expose parameters (Threshold, Gain, EQ bands) so they can be controlled via the Intelligence Layer later.

## Success Criteria
- [ ] Audio passes through the compressor without artifacts.
- [ ] Limiter successfully prevents clipping on aggressive gain boosts.
- [ ] M/S processing allows widening or narrowing the stereo image.
- [ ] Performance remains real-time (no significant latency increase).
