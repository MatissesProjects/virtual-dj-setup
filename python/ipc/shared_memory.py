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
        
        # Read Header (Expanded to 64 bytes for growth)
        header_data = self.mm.read(64)
        try:
            # i: seq, i: lock, f: rms, f: centroid, f: peak, i: auth, i: song, q: ticks, i: peak_flag, f: duck_f, f: duck_g
            res = struct.unpack('ii fff ii q i ff', header_data[:52])
            seq, lock, rms, centroid, peak, auth, song, ticks, peak_flag, duck_f, duck_g = res
            
            if lock == 1:
                return None

            # Read FFT Data (Starts at offset 64)
            self.mm.seek(64)
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

    def write_ducking(self, frequency, gain_db):
        if not self.mm:
            return
        
        # Ducking frequency at offset 40, gain at 44
        self.mm.seek(40)
        self.mm.write(struct.pack('ff', float(frequency), float(gain_db)))

    # Gym Synchronization Methods
    def write_step_command(self, step_size):
        if not self.mm:
            return
        # command=1 at offset 48, step_size at 52
        self.mm.seek(48)
        self.mm.write(struct.pack('ii', 1, int(step_size)))

    def is_step_completed(self):
        if not self.mm:
            return True
        self.mm.seek(48)
        command = struct.unpack('i', self.mm.read(4))[0]
        return command == 0

    def read_is_done(self):
        if not self.mm:
            return True
        self.mm.seek(56)
        is_done = struct.unpack('i', self.mm.read(4))[0]
        return is_done == 1

    def close(self):
        if self.mm:
            self.mm.close()
