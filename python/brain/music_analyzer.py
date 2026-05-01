import librosa
import numpy as np
import os

class MusicAnalyzer:
    """
    Analyzes audio tracks to extract symbolic anchors (Key, Scale, Tempo, Kick Pattern).
    Provides context for generative bridge synthesis.
    """
    def __init__(self):
        print("[ANALYZER] Initializing Music Analyzer...")

    def analyze_track(self, file_path):
        """
        Performs a full analysis of a track.
        Returns a dictionary of anchors.
        """
        if not os.path.exists(file_path):
            print(f"[ANALYZER] Error: File {file_path} not found.")
            return None

        print(f"[ANALYZER] Analyzing: {os.path.basename(file_path)}...")
        
        # Load audio (downsampled for faster analysis)
        y, sr = librosa.load(file_path, sr=22050, duration=120) # Analyze first 2 mins
        
        # 1. Tempo & Beat Tracking
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        
        # 2. Key & Scale Detection
        # Using chromagram to estimate key
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        key_index = self._estimate_key(chroma)
        key_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        detected_key = key_names[key_index % 12]
        is_minor = key_index >= 12
        scale_type = "Minor" if is_minor else "Major"

        # 3. Kick Pattern Estimation (Simplified)
        # Look for low-frequency energy peaks aligned with beats
        low_y = librosa.effects.preemphasis(y, coef=0.5) # Focus on low end? Not exactly.
        # Better: use spectral flux on low bands
        kick_pattern = self._estimate_kick_pattern(y, sr, beat_frames)

        results = {
            "title": os.path.basename(file_path),
            "tempo": float(tempo),
            "key": detected_key,
            "scale": scale_type,
            "kick_density": float(np.mean(kick_pattern))
        }
        
        # Generate a descriptive prompt for AI synthesis
        results["style_prompt"] = self._generate_style_prompt(results)
        
        print(f"[ANALYZER] Result: {results['tempo']:.1f} BPM | {results['key']} {results['scale']}")
        return results

    def _generate_style_prompt(self, r):
        """Creates a text prompt for MusicGen based on analysis."""
        return f"A high-quality electronic music track at {r['tempo']:.0f} BPM in the key of {r['key']} {r['scale']}. " \
               f"Focus on a clean kick pattern with moderate energy."

    def _estimate_key(self, chroma):
        """
        Simple key estimation using Krumhansl-Schmuckler profiles.
        Returns an index (0-11 for Major, 12-23 for Minor).
        """
        # Averages over time
        chroma_avg = np.mean(chroma, axis=1)
        
        # Key profiles
        major_profile = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
        minor_profile = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
        
        correlations = []
        for i in range(12):
            # Rotate profiles
            shifted_major = np.roll(major_profile, i)
            shifted_minor = np.roll(minor_profile, i)
            correlations.append(np.corrcoef(chroma_avg, shifted_major)[0, 1])
            correlations.append(np.corrcoef(chroma_avg, shifted_minor)[0, 1])
            
        return np.argmax(correlations)

    def _estimate_kick_pattern(self, y, sr, beat_frames):
        """
        Estimates the probability of a kick on each beat.
        """
        # Get low-frequency energy
        S = np.abs(librosa.stft(y))
        low_energy = np.mean(S[:10, :], axis=0) # First 10 bins (~<200Hz)
        
        # Normalize
        if np.max(low_energy) > 0:
            low_energy /= np.max(low_energy)
            
        # Sample at beat frames
        kick_probs = low_energy[beat_frames]
        return kick_probs

if __name__ == "__main__":
    # Test on a dummy path or local file if provided
    analyzer = MusicAnalyzer()
    # results = analyzer.analyze_track("sample.mp3")
