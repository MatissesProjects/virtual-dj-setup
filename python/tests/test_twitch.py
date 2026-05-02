import unittest
import asyncio
from brain.audience_listener import AudienceListener

class MockAuthor:
    def __init__(self, name):
        self.name = name

class MockMessage:
    def __init__(self, content, author_name):
        self.content = content
        self.author = MockAuthor(author_name)
        self.echo = False

class TestAudienceListener(unittest.TestCase):
    def setUp(self):
        self.listener = AudienceListener() # Defaults to simulator mode

    def test_sentiment_and_ema(self):
        # Test positive sentiment
        self.listener.simulate_chat("POG CHAMP THIS IS FIRE")
        vibe_pog = self.listener.vibe_score
        self.assertGreater(vibe_pog, 0)
        
        # Test negative sentiment dragging it down
        self.listener.simulate_chat("this is mid and boring ResidentSleeper")
        vibe_mid = self.listener.vibe_score
        self.assertLess(vibe_mid, vibe_pog)

    def test_loyalty_tracking(self):
        msg1 = MockMessage("hello", "user1")
        msg2 = MockMessage("world", "user1")
        msg3 = MockMessage("test", "user2")
        
        # Simulate message events (ignoring async for this unit test of logic)
        for msg in [msg1, msg2, msg3]:
            user = msg.author.name
            self.listener.loyalty_map[user] = self.listener.loyalty_map.get(user, 0) + 1
        
        report = self.listener.get_vibe_report()
        top_fans = dict(report['top_fans'])
        
        self.assertEqual(top_fans['user1'], 2)
        self.assertEqual(top_fans['user2'], 1)

    def test_commands_logic(self):
        # Test request addition
        self.listener.requests.append({"user": "user1", "track": "Daft Punk"})
        report = self.listener.get_vibe_report()
        self.assertEqual(len(report['requests']), 1)
        self.assertEqual(report['requests'][0]['track'], "Daft Punk")
        
        # Test voting
        self.listener.votes['next'] += 1
        report = self.listener.get_vibe_report()
        self.assertEqual(report['votes']['next'], 1)

if __name__ == '__main__':
    unittest.main()
