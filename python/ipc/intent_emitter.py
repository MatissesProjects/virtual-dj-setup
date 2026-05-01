import socket
import struct
from enum import IntEnum

class IntentType(IntEnum):
    IDLE = 0
    CREATE_TENSION = 1
    EXECUTE_DROP = 2
    SMOOTH_BLEND = 3
    CLEAN_CUT = 4
    APPLY_DUCKING = 5

class IntentEmitter:
    def __init__(self, host='127.0.0.1', port=5555):
        self.host = host
        self.port = port

    def emit(self, intent_type):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.port))
                # Pack intent as 4-byte integer (little endian)
                s.sendall(struct.pack('<i', int(intent_type)))
                return True
        except ConnectionRefusedError:
            print(f"Failed to connect to C# engine at {self.host}:{self.port}")
            return False
        except Exception as e:
            print(f"Intent Emission Error: {e}")
            return False
