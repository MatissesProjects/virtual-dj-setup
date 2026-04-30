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
        data = self.mm.read(24) # 4+4+4+4+8 bytes (RMS, Centroid, Peak, Authority, Ticks)
        
        # Unpack: 4 floats (f) and 1 long long (q)
        # Actually Authority is an int (i), so: fffiq
        try:
            rms, centroid, peak, authority, ticks = struct.unpack('fffiq', data)
            return {
                "rms": rms,
                "centroid": centroid,
                "peak": peak,
                "authority": authority, # 0 = AI, 1 = Human
                "ticks": ticks
            }
        except struct.error:
            return None

    def close(self):
        if self.mm:
            self.mm.close()
