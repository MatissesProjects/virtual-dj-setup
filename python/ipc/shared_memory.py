import mmap
import struct
import time
from datetime import datetime

class SharedMemoryReader:
    def __init__(self, map_name="VirtualDjFeatures", buffer_size=1024):
        self.map_name = map_name
        self.buffer_size = buffer_size
        self.mm = None

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
        data = self.mm.read(20) # 4+4+4+8 bytes
        
        # Unpack: 3 floats (f) and 1 long long (q)
        # f: RMS, f: Centroid, f: Peak, q: Timestamp (Ticks)
        try:
            rms, centroid, peak, ticks = struct.unpack('fffq', data)
            return {
                "rms": rms,
                "centroid": centroid,
                "peak": peak,
                "ticks": ticks
            }
        except struct.error:
            return None

    def close(self):
        if self.mm:
            self.mm.close()
