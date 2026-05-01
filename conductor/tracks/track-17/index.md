# Track 17: Multi-Modal Audience Vibe Modeling (Twitch Sentiment)

## Overview
Integrate the audience into the AI's reward loop. By analyzing Twitch chat velocity, sentiment, and emote density, the AI can quantify the "vibe" and adjust its mixing policy to maximize engagement.

## Requirements
- Connect to Twitch IRC to ingest real-time chat data.
- Use a lightweight NLP model to calculate sentiment and "hype" scores.
- Feed the `CrowdVibeScore` into the RL agent's reward function.

## Documents
- [Specification](./spec.md)
- [Implementation Plan](./plan.md)
