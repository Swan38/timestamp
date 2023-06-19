import sys

# HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)
SIZE = 8

BYTE_ORDER = "big"

def encode_timestamp(timestamp: float) -> bytes:
    timestamp_10_7: int = int(timestamp * (10**7))
    return timestamp_10_7.to_bytes(length=8, byteorder=BYTE_ORDER, signed=False)

def decode_timestamp(byte_timestamp: bytes) -> float:
    timestamp_10_7: int = int.from_bytes(byte_timestamp, byteorder=BYTE_ORDER, signed=False)
    return timestamp_10_7 / (10**7)
