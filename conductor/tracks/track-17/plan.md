# Implementation Plan: Multi-Modal Audience Vibe Modeling

## Phase 1: Twitch Ingestion & Sentiment
- [x] Install `twitchio`, `vaderSentiment`, and `nltk`.
- [x] Create `python/brain/audience_listener.py` to handle the Twitch connection.
- [x] Implement `SentimentAnalyzer` using VADER. (Added custom Twitch slang lexicon)
- [x] Test sentiment scoring on mock Twitch chat logs.

## Phase 2: Engagement Modeling & Rewards
- [x] Implement `HypeTracker` to calculate message velocity and emote density.
- [x] Create the `CrowdVibeScore` aggregator with EMA smoothing.
- [x] Update `python/brain/dj_env.py` to accept the audience vibe as a reward input.

## Phase 3: Dashboard Integration & Verification
- [x] Hook `audience_listener.py` into the main `python/main.py` loop.
- [x] Update the Vue UI with a "Crowd Vibe Meter" (Progress bar + Hype status).
- [x] Test the full loop: Mock Chat -> Sentiment -> RL Reward -> Mix Change.
