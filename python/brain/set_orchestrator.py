import time
import threading
from ipc.intent_emitter import IntentType

class SetOrchestrator:
    """
    Manages the 'DJ Set' logic: automated transitions, track loading, and tempo matching.
    """
    def __init__(self, deck_a, deck_b, emitter):
        self.deck_a = deck_a
        self.deck_b = deck_b
        self.emitter = emitter
        self.is_running = False
        self.current_deck_idx = 0 # 0 for A, 1 for B
        self.playlist = []
        self.current_track_idx = -1
        
        self.transition_duration = 10 # Seconds
        self._thread = None

    def start_set(self, initial_playlist):
        self.playlist = initial_playlist
        self.is_running = True
        self._thread = threading.Thread(target=self._orchestration_loop, daemon=True)
        self._thread.start()
        print("[ORCHESTRATOR] DJ Set started.")

    def _orchestration_loop(self):
        """
        Monitor playback state and trigger transitions.
        """
        while self.is_running:
            # 1. Check if we need to load the first track
            if self.current_track_idx == -1 and len(self.playlist) > 0:
                self._load_next_track()
                time.sleep(5) # Give it time to load
            
            # 2. Logic for 'End of Track' detection
            # NOTE: For now, we use a simple timer or wait for manual trigger.
            # Real implementation would use Playwright to read 'currentTime' vs 'duration'.
            
            # 3. Handle Transitions (Demo logic: transition every 2 mins for prototype)
            # time.sleep(120) 
            # self.trigger_transition()
            
            time.sleep(1)

    def _load_next_track(self):
        self.current_track_idx += 1
        if self.current_track_idx < len(self.playlist):
            url = self.playlist[self.current_track_idx]
            deck = self.deck_a if self.current_deck_idx == 0 else self.deck_b
            print(f"[ORCHESTRATOR] Loading next track into {deck.name}: {url}")
            deck.load_track(url)
        else:
            print("[ORCHESTRATOR] End of playlist reached.")
            self.is_running = False

    def trigger_transition(self):
        """Executes a smooth blend to the other deck."""
        target_deck_idx = 1 - self.current_deck_idx
        print(f"[ORCHESTRATOR] Triggering transition to Deck {'B' if target_deck_idx == 1 else 'A'}")
        
        # 1. Load next track into the 'idle' deck
        next_track_url = self.playlist[(self.current_track_idx + 1) % len(self.playlist)]
        idle_deck = self.deck_b if target_deck_idx == 1 else self.deck_a
        idle_deck.load_track(next_track_url)
        
        # 2. Emit Intent to C# for Smooth Blend
        self.emitter.emit(IntentType.SMOOTH_BLEND)
        
        # 3. Update local state after transition
        self.current_deck_idx = target_deck_idx
        self.current_track_idx += 1
        
    def stop_set(self):
        self.is_running = False
        print("[ORCHESTRATOR] DJ Set stopped.")
