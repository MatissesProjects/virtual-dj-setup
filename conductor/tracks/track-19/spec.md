# Specification: Playwright YouTube Decks

## Requirements
- [x] Integrate `playwright` into the Python backend.
- [x] Create a `YouTubeDeck` class to manage browser instances.
- [x] Support loading tracks by URL into discrete virtual decks (Deck A / Deck B).
- [x] Implement basic playback controls (Play/Pause, Tempo/Rate).
- [x] Expose controls via the Vue Dashboard.

## Technical Details
- **Engine:** Playwright (Chromium).
- **Audio Capture:** Relies on WASAPI Loopback (OS-level mixing).
- **Automation:** Support `playbackRate` adjustment via JS injection for tempo matching.
