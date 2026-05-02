import asyncio
from playwright.async_api import async_playwright
import threading

class YouTubeDeck:
    """
    A virtual 'deck' powered by a Playwright-controlled browser instance playing YouTube.
    """
    def __init__(self, name):
        self.name = name
        self.browser = None
        self.page = None
        self.playwright = None
        self.is_playing = False
        self.current_url = None
        self._loop = None
        self._thread = None

    def start_in_thread(self):
        """Starts the browser event loop in a background thread."""
        self._thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self._thread.start()

    def _run_event_loop(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._launch_browser())
        self._loop.run_forever()

    async def _launch_browser(self):
        self.playwright = await async_playwright().start()
        # We use a persistent context to potentially save cookies/consent
        self.browser = await self.playwright.chromium.launch(
            headless=False, # Set to False so we can see the 'decks'
            args=["--autoplay-policy=no-user-gesture-required"]
        )
        self.page = await self.browser.new_page()
        print(f"[YOUTUBE-DECK] {self.name} initialized.")

    def load_track(self, url):
        """Loads a YouTube URL."""
        if self._loop:
            asyncio.run_coroutine_threadsafe(self._async_load_track(url), self._loop)

    async def _async_load_track(self, url):
        print(f"[YOUTUBE-DECK] {self.name} loading: {url}")
        self.current_url = url
        await self.page.goto(url)
        # Wait for the play button or try to autoplay
        try:
            # YouTube sometimes needs a click or just plays due to autoplay policy
            await self.page.click('button.ytp-play-button', timeout=5000)
            self.is_playing = True
        except:
            # Already playing or failed to find button
            pass

    def toggle_play(self):
        if self._loop:
            asyncio.run_coroutine_threadsafe(self._async_toggle_play(), self._loop)

    async def _async_toggle_play(self):
        await self.page.keyboard.press('k') # YouTube shortcut for play/pause
        self.is_playing = not self.is_playing
        print(f"[YOUTUBE-DECK] {self.name} {'Playing' if self.is_playing else 'Paused'}")

    def set_tempo(self, rate):
        """Sets playback rate (0.25 to 2.0)."""
        if self._loop:
            asyncio.run_coroutine_threadsafe(self._async_set_tempo(rate), self._loop)

    async def _async_set_tempo(self, rate):
        # Use JavaScript to set the video playback rate
        await self.page.evaluate(f"document.querySelector('video').playbackRate = {rate}")
        print(f"[YOUTUBE-DECK] {self.name} Tempo set to: {rate}x")

    def stop(self):
        if self._loop:
            self._loop.stop()
        if self.playwright:
            asyncio.run_coroutine_threadsafe(self.playwright.stop(), self._loop)
