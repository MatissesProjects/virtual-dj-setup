import asyncio
from twitchio.ext import commands
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import numpy as np
import time
import threading

class AudienceListener(commands.Bot):
    """
    Ingests real-time Twitch chat and calculates audience sentiment/hype.
    Acts as a bridge between the crowd and the AI's reward loop.
    """
    def __init__(self, token=None, initial_channels=None):
        # Simulator Mode if no token provided
        self.simulator_mode = token is None
        self.analyzer = SentimentIntensityAnalyzer()
        
        # Add Twitch Slang to VADER
        twitch_slang = {
            'pog': 3.0,
            'pogchamp': 3.5,
            'fire': 3.0,
            'lit': 2.5,
            'hype': 2.5,
            'lfg': 2.0,
            'skip': -2.5,
            'mid': -1.5,
            'garbage': -3.0,
            'residentsleeper': -3.0,
            'lul': 1.5,
            'kreygasm': 3.0
        }
        self.analyzer.lexicon.update(twitch_slang)
        
        # Engagement Metrics
        self.vibe_score = 0.0 # Smoothed sentiment [-1.0, 1.0]
        self.hype_level = 0.0 # Velocity [0.0, 1.0+]
        self.alpha = 0.5 # Higher alpha for testing responsiveness
        
        self.loyalty_map = {} # user_id -> engagement_score
        self.requests = [] # track request queue
        self.votes = {"next": 0, "skip": 0}
        
        self.message_count = 0
        self.last_reset = time.time()
        
        if not self.simulator_mode:
            super().__init__(token=token, prefix='!', initial_channels=initial_channels)
            print(f"[VIBE] Initializing Twitch Listener on {initial_channels}...")
        else:
            print("[VIBE] Initializing in Simulator Mode (No Twitch Token).")

    async def event_message(self, message):
        if message.echo: return
        
        # 1. User Loyalty Tracking
        user = message.author.name
        self.loyalty_map[user] = self.loyalty_map.get(user, 0) + 1
        
        # 2. Process Commands
        if message.content.startswith('!'):
            await self.handle_commands(message)
        else:
            self._process_text(message.content)

    @commands.command(name='request')
    async def request_command(self, ctx, *, track_name):
        """Allows users to request tracks."""
        self.requests.append({"user": ctx.author.name, "track": track_name})
        # If in simulator mode, ctx.send might fail, so we check
        if not self.simulator_mode:
            await ctx.send(f"@{ctx.author.name}, request for '{track_name}' added to queue!")
        print(f"[TWITCH] Request: {track_name} by {ctx.author.name}")

    @commands.command(name='vote')
    async def vote_command(self, ctx, choice):
        """Vote for 'next' or 'skip'."""
        if choice in self.votes:
            self.votes[choice] += 1
            if not self.simulator_mode:
                await ctx.send(f"Vote cast for {choice}!")
            
    def _process_text(self, text):
        """Processes a single line of chat text for sentiment and velocity."""
        # 1. Sentiment Analysis
        scores = self.analyzer.polarity_scores(text)
        compound = scores['compound']
        
        # 2. EMA Smoothing
        self.vibe_score = (self.alpha * compound) + (1 - self.alpha) * self.vibe_score
        
        # 3. Velocity tracking
        self.message_count += 1
        
        # Print for local debugging
        # print(f"[RAW] {text[:20]}... | Score: {compound:+.2f}")

    def get_vibe_report(self):
        """Returns the current audience state for the RL loop."""
        # Calculate velocity (messages per 5 seconds)
        now = time.time()
        elapsed = now - self.last_reset
        if elapsed >= 5.0:
            self.hype_level = self.message_count / elapsed
            self.message_count = 0
            self.last_reset = now
            
        return {
            "vibe": float(self.vibe_score),
            "hype": float(self.hype_level),
            "status": "HYPE" if self.hype_level > 1.5 else "CHILL" if self.vibe_score > 0.2 else "NEUTRAL",
            "requests": self.requests[-3:], # Show last 3 requests
            "votes": self.votes,
            "top_fans": sorted(self.loyalty_map.items(), key=lambda x: x[1], reverse=True)[:3]
        }

    def simulate_chat(self, text):
        """Manually inject chat for testing/simulator mode."""
        self._process_text(text)

    def run_in_thread(self):
        """Starts the bot in a dedicated background thread."""
        if self.simulator_mode:
            print("[VIBE] Simulator running. Use simulate_chat() to inject data.")
            return
            
        loop = asyncio.new_event_loop()
        threading.Thread(target=self._run_bot, args=(loop,), daemon=True).start()

    def _run_bot(self, loop):
        asyncio.set_event_loop(loop)
        self.run()

if __name__ == "__main__":
    # Test Script
    listener = AudienceListener()
    test_messages = [
        "THIS TRACK IS FIRE!!! PogChamp",
        "love this transition, so smooth",
        "meh, skip this one",
        "ResidentSleeper",
        "POGGGGGG",
        "Woooow nice chords"
    ]
    
    print("Testing Sentiment Analyzer...")
    for msg in test_messages:
        listener.simulate_chat(msg)
        report = listener.get_vibe_report()
        print(f"Msg: {msg: <30} | Vibe: {report['vibe']:+.2f} | Status: {report['status']}")
        time.sleep(0.5)
