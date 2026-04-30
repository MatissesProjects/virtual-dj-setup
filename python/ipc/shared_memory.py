import mmap
import struct
import time
from datetime import datetime

class SharedMemoryReader:
    def __init__(self, map_name="VirtualDjFeatures", buffer_size=8192):
        self.map_name = map_name
        self.buffer_size = buffer_size
        self.mm = None
        self.fft_bin_count = 1024

    def connect(self):
        try:
            # On Windows, mmap.mmap(0, size, tagname)
            self.mm = mmap.mmap(0, self.buffer_size, self.map_name)
            print(f"Connected to Shared Memory: {self.map_name}")
            return True
        except FileNotFoundError:
            print("Shared memory not found. Is the C# engine running?")
            return False

    def read_features(self):
        if not self.mm:
            return None
        
        self.mm.seek(0)
        
        # Read Header (40 bytes)
        header_data = self.mm.read(40)
        try:
            # i: seq, i: lock, f: rms, f: centroid, f: peak, i: auth, i: song, q: ticks, i: peak_flag
            seq, lock, rms, centroid, peak, auth, song, ticks, peak_flag = struct.unpack('i i fff i i q i', header_data)
            
            # If C# is currently writing, skip this frame to prevent tearing
            if lock == 1:
                return None

            # Read FFT Data (1024 floats = 4096 bytes)
            fft_data = self.mm.read(self.fft_bin_count * 4)
            fft_array = struct.unpack(f'{self.fft_bin_count}f', fft_data)

            return {
                "sequence": seq,
                "rms": rms,
                "centroid": centroid,
                "peak": peak,
                "authority": auth,
                "song_index": song,
                "ticks": ticks,
                "is_peak": peak_flag == 1,
                "fft": list(fft_array)
            }
        except struct.error:
            return None

    def close(self):
        if self.mm:
            self.mm.close()
