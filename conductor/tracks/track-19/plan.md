# Implementation Plan: Playwright YouTube Decks

## Phase 1: Environment & Class (Completed)
- [x] Install `playwright` and browsers.
- [x] Implement `YouTubeDeck` with background threading.
- [x] Support `load_track` and `toggle_play`.

## Phase 2: Backend Integration (Completed)
- [x] Update `python/main.py` to initialize two decks.
- [x] Add `/load_track` API endpoint.
- [x] Ensure decks start their own browser instances.

## Phase 3: UI Controls (Completed)
- [x] Add "YouTube Decks Automation" card to the dashboard.
- [x] Implement URL input and "LOAD DECK" buttons.
- [x] Verify browser instances spawn and play audio.

## Phase 4: AI Selection (Upcoming)
- [ ] Implement AI logic to auto-select and load URLs based on Twitch requests.
- [ ] Support beat-syncing logic by adjusting `playbackRate`.
