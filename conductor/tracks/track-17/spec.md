# Specification: Multi-Modal Audience Vibe Modeling

## Overview
Connect the AI's performance to the crowd. This track implements a Twitch integration layer that ingests real-time chat data, calculates sentiment and "hype" scores, and feeds this data into the RL agent's reward loop. This allows the AI to learn which transitions and tracks the audience actually enjoys.

## Requirements
1.  **Twitch Chat Ingestion (Python):**
    -   Use `TwitchIO` (asyncio-based) to connect to a specified Twitch channel.
    -   Handle IRC connection, rate-limiting, and reconnects automatically.
2.  **Real-time Sentiment Analysis:**
    -   Utilize the `VADER` sentiment analyzer (optimized for social media/slang/emojis).
    -   Generate a polarity score `[-1.0 to 1.0]` for every incoming message.
3.  **Hype & Emote Metrics:**
    -   Track "Chat Velocity" (messages per second).
    -   Identify "Emote Bursts" (density of emotes like `PogChamp`, `LUL`, `Kreygasm`) as a proxy for engagement.
4.  **Audience Reward Signal:**
    -   Calculate a smoothed `CrowdVibeScore` using an Exponential Moving Average (EMA).
    -   Feed this score into the `DjEnv` (Gym environment) as a dense reward signal.
5.  **UI Feedback:**
    -   Stream the live "Vibe Meter" to the Vue dashboard.

## Success Criteria
- [ ] Python bot successfully connects and prints Twitch messages to the console.
- [ ] Sentiment analysis correctly identifies "Hype" vs. "Boredom" in test strings.
- [ ] The `CrowdVibeScore` is visible and updating on the Vue dashboard in real-time.
- [ ] RL agent reward increases during positive sentiment bursts.
