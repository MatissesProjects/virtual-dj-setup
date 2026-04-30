import ollama
import json

class ChordPredictor:
    def __init__(self, model="qwen3.5:4b"):
        self.model = model
        self.cache = {}

    def get_chords(self, song_title, artist):
        key = f"{artist} - {song_title}"
        if key in self.cache:
            return self.cache[key]

        prompt = f"""
        Provide the main chord progression for the song '{song_title}' by '{artist}'.
        Return ONLY a JSON list of chords (e.g. ["C", "G", "Am", "F"]).
        Do not include any other text.
        """
        
        try:
            response = ollama.generate(model=self.model, prompt=prompt)
            # Try to extract JSON
            text = response['response'].strip()
            # Basic cleaning if LLM adds markdown
            if text.startswith("```json"):
                text = text[7:-3].strip()
            elif text.startswith("["):
                pass
            
            chords = json.loads(text)
            self.cache[key] = chords
            return chords
        except Exception as e:
            print(f"Chord Prediction Error for {key}: {e}")
            return []

if __name__ == "__main__":
    predictor = ChordPredictor()
    print(predictor.get_chords("Get Lucky", "Daft Punk"))
