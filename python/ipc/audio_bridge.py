import mmap
import struct
import numpy as np

class AudioBridge:
    """
    Python side of the high-bandwidth PCM bridge.
    Handles raw audio reading and writing for stem separation.
    """
    def __init__(self, map_name="VirtualDjAudioBridge"):
        self.block_size = 1024
        self.channels = 2
        self.header_size = 64
        self.audio_data_size = self.block_size * self.channels * 4 # float32
        
        self.stream_count = 5
        self.stream_size = self.header_size + self.audio_data_size
        self.total_buffer_size = self.stream_size * self.stream_count
        
        self.map_name = map_name
        self.mm = None
        self.last_input_seq = -1

    def connect(self):
        try:
            self.mm = mmap.mmap(0, self.total_buffer_size, self.map_name)
            print(f"[IPC] Connected to Audio Bridge: {self.map_name}")
            return True
        except FileNotFoundError:
            return False

    def read_input(self):
        """Reads the raw input stream from C#."""
        if not self.mm: return None
        
        # Check sequence number
        self.mm.seek(8) # Seq offset in stream 0
        seq = struct.unpack('i', self.mm.read(4))[0]
        
        if seq == self.last_input_seq:
            return None
        self.last_input_seq = seq
        
        # Read PCM data
        self.mm.seek(self.header_size)
        data = self.mm.read(self.audio_data_size)
        return np.frombuffer(data, dtype=np.float32)

    def write_stems(self, stems):
        """
        Writes processed stems back to shared memory.
        stems: Dictionary with keys 'vocal', 'drums', 'bass', 'other'
        """
        if not self.mm: return
        
        mapping = {'vocal': 1, 'drums': 2, 'bass': 3, 'other': 4}
        
        for name, idx in mapping.items():
            if name in stems:
                offset = idx * self.stream_size
                self.mm.seek(offset + self.header_size)
                self.mm.write(stems[name].tobytes())
                # Signal update with sequence
                self.mm.seek(offset + 8)
                self.mm.write(struct.pack('i', self.last_input_seq))

    def close(self):
        if self.mm:
            self.mm.close()
