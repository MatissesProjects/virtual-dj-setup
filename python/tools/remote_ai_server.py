import socket
import struct
import numpy as np
import threading
from brain.stem_separator import StemSeparator

class RemoteAIServer:
    """
    A high-performance TCP server that receives raw audio from a C# engine,
    processes it through the StemSeparator, and sends stems back.
    Allows offloading heavy AI tasks to a different machine on the LAN.
    """
    def __init__(self, host='0.0.0.0', port=7777):
        self.host = host
        self.port = port
        self.separator = StemSeparator()
        self.is_running = False
        self.current_bridge_pcm = None
        self.bridge_offset = 0
        self._lock = threading.Lock()

    def set_bridge_pcm(self, pcm):
        with self._lock:
            self.current_bridge_pcm = pcm
            self.bridge_offset = 0
            print(f"[REMOTE AI] New bridge PCM loaded ({len(pcm)} samples).")

    def start(self):
        self.is_running = True
        
        # Start Management Port (8888) to receive bridge PCM from DJ machine
        threading.Thread(target=self._run_management_server, daemon=True).start()

        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.bind((self.host, self.port))
        server_sock.listen(5)
        print(f"[REMOTE AI] Server listening on {self.host}:{self.port}")

        try:
            while self.is_running:
                client_sock, addr = server_sock.accept()
                print(f"[REMOTE AI] Accepted connection from {addr}")
                threading.Thread(target=self.handle_client, args=(client_sock,), daemon=True).start()
        except KeyboardInterrupt:
            self.stop()

    def _run_management_server(self):
        """Listens for bridge PCM data from the DJ machine."""
        mgmt_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        mgmt_sock.bind((self.host, 8888))
        mgmt_sock.listen(1)
        while self.is_running:
            client, addr = mgmt_sock.accept()
            try:
                # Read size then PCM
                header = client.recv(4)
                if header:
                    size = struct.unpack('i', header)[0]
                    data = b""
                    while len(data) < size:
                        chunk = client.recv(size - len(data))
                        if not chunk: break
                        data += chunk
                    pcm = np.frombuffer(data, dtype=np.float32)
                    self.set_bridge_pcm(pcm)
            except: pass
            finally: client.close()

    def handle_client(self, sock):
        try:
            while self.is_running:
                # 1. Read header (4 bytes size)
                header = sock.recv(4)
                if not header: break
                
                size = struct.unpack('i', header)[0]
                
                # 2. Read PCM data
                data = b""
                while len(data) < size:
                    chunk = sock.recv(size - len(data))
                    if not chunk: break
                    data += chunk
                
                if len(data) < size: break
                
                raw_pcm = np.frombuffer(data, dtype=np.float32)
                
                # 3. Process Stems (Mock for verification)
                stems = {
                    1: raw_pcm * 0.8, # Vocal
                    2: raw_pcm * 1.2, # Drums
                    3: raw_pcm * 0.5, # Bass
                    4: raw_pcm * 1.0  # Other
                }
                
                # New: Handle Bridge Synthesis (Stream 5)
                with self._lock:
                    if self.current_bridge_pcm is not None:
                        end = self.bridge_offset + len(raw_pcm)
                        if end > len(self.current_bridge_pcm):
                            bridge_block = self.current_bridge_pcm[self.bridge_offset:]
                            bridge_block = np.pad(bridge_block, (0, len(raw_pcm) - len(bridge_block)))
                            self.current_bridge_pcm = None 
                            self.bridge_offset = 0
                        else:
                            bridge_block = self.current_bridge_pcm[self.bridge_offset:end]
                            self.bridge_offset = end
                        stems[5] = bridge_block
                    else:
                        stems[5] = np.zeros_like(raw_pcm)
                
                # 4. Send Stems Back
                for idx, stem_data in stems.items():
                    stem_bytes = stem_data.tobytes()
                    # Header: [stemIndex] [dataSize]
                    sock.sendall(struct.pack('ii', idx, len(stem_bytes)))
                    sock.sendall(stem_bytes)
                    
        except Exception as e:
            print(f"[REMOTE AI] Client disconnected: {e}")
        finally:
            sock.close()

    def stop(self):
        self.is_running = False

if __name__ == "__main__":
    server = RemoteAIServer()
    server.start()
