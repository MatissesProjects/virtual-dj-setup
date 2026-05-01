import mmap
import struct
import time
from datetime import datetime

class SharedMemoryReader:
    def __init__(self, map_name="VirtualDjFeatures", buffer_size=16448): # 64 + (4160 * 4) = 16704 bytes
        self.map_name = map_name
        self.fft_bin_count = 1024
        
        # Ring Buffer Constants matching C#
        self.buffer_slots = 4
        self.header_size = 64
        self.slot_size = self.header_size + (self.fft_bin_count * 4)
        self.state_offset = 0
        self.slots_offset = 64
        self.buffer_size = self.slots_offset + (self.slot_size * self.buffer_slots)
        
        self.mm = None
        self.last_read_seq = -1

    def connect(self):
        try:
            self.mm = mmap.mmap(0, self.buffer_size, self.map_name)
            print(f"Connected to Shared Memory: {self.map_name}")
            return True
        except FileNotFoundError:
            print("Shared memory not found. Is the C# engine running?")
            return False

    def read_features(self):
        if not self.mm:
            return None
        
        # 1. Read the atomic WritePointer to know which slot is safe to read
        self.mm.seek(self.state_offset)
        # Read WritePtr(0), Done(4), StepCmd(8), StepSize(12), DuckF(16), DuckG(20), XFader(24)
        state_header = self.mm.read(28)
        write_ptr, is_done, step_cmd, step_size, duck_f, duck_g, xfader = struct.unpack('i i i i f f f', state_header)
        
        if write_ptr < 0 or write_ptr >= self.buffer_slots:
            return None # Uninitialized or corrupted pointer

        # 2. Calculate offset for the current complete slot
        slot_offset = self.slots_offset + (write_ptr * self.slot_size)
        
        # Read Data Slot Header (40 bytes used currently)
        self.mm.seek(slot_offset)
        data_header = self.mm.read(40)
        
        try:
            # i: seq, f: rms, f: centroid, f: peak, i: auth, i: song, q: ticks, i: peak_flag
            res = struct.unpack('i fff ii q i', data_header)
            seq, rms, centroid, peak, auth, song, ticks, peak_flag = res
            
            # Prevent double reading the same frame
            if seq == self.last_read_seq:
                return None
            self.last_read_seq = seq

            # Read FFT Data 
            self.mm.seek(slot_offset + 64)
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
                "fft": list(fft_array),
                "xfader": xfader
            }
        except struct.error:
            return None

    def write_xfader(self, position):
        if not self.mm:
            return
        self.mm.seek(self.state_offset + 24)
        self.mm.write(struct.pack('f', float(position)))

    def write_ducking(self, frequency, gain_db):
        if not self.mm:
            return
        self.mm.seek(self.state_offset + 16)
        self.mm.write(struct.pack('ff', float(frequency), float(gain_db)))

    def write_stem_volumes(self, vocal_vol, drums_vol, bass_vol, other_vol):
        if not self.mm:
            return
        # Storing at offset 28, 32, 36, 40 (inside the 64-byte State Header)
        self.mm.seek(self.state_offset + 28)
        self.mm.write(struct.pack('ffff', float(vocal_vol), float(drums_vol), float(bass_vol), float(other_vol)))

    # Gym Synchronization Methods
    def write_step_command(self, step_size):
        if not self.mm:
            return
        self.mm.seek(self.state_offset + 8)
        self.mm.write(struct.pack('ii', 1, int(step_size)))

    def is_step_completed(self):
        if not self.mm:
            return True
        self.mm.seek(self.state_offset + 8)
        command = struct.unpack('i', self.mm.read(4))[0]
        return command == 0

    def read_is_done(self):
        if not self.mm:
            return True
        self.mm.seek(self.state_offset + 4)
        is_done = struct.unpack('i', self.mm.read(4))[0]
        return is_done == 1

    def close(self):
        if self.mm:
            self.mm.close()
