# Specification: Chord Retrieval & Playlist Management

## Overview
To improve the AI's "musicality," it needs to know the harmonic structure (chords) of the songs it is mixing. This track adds a playlist manager and a chord lookup service.

## Requirements
1.  **Playlist Management:**
    -   Store a list of songs (Artist, Title).
    -   Ability to track the "Current Song" and "Next Song".
2.  **Chord Retrieval Service:**
    -   **Provider 1 (External):** Hooktheory API integration to fetch chords by song title/artist.
    -   **Provider 2 (Local AI):** Interface to a local LLM or specialized chord recognition model to "predict" or extract chords if the external lookup fails.
3.  **Data Integration:**
    -   Stream the current song's chord progression to the Python intelligence layer.
    -   Update the Intelligence Layer to use chord context for tension prediction.

## Success Criteria
- [x] A playlist can be loaded and managed.
- [x] Chords are successfully retrieved for a given song title.
- [x] The Python brain receives the current chord information via IPC.
- [x] Predictive mixing logic uses chord transitions to trigger intents.
