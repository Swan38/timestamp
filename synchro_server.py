import socket
import time
from functools import partial
import threading

from connection import PORT, SIZE, encode_timestamp

HOSTNAME = socket.gethostname()
SERVER_ADDRESS = socket.gethostbyname(HOSTNAME)

def respond(conn):
    with conn:
        while True:
            try:
                data = conn.recv(SIZE)
                if data is None:
                    break
                conn.sendall(encode_timestamp(time.time()))
            except ConnectionAbortedError as error:
                break

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((SERVER_ADDRESS, PORT))
    s.listen()
    while True:
        conn, addr = s.accept()
        print(f"Connected by {addr}")
        threading.Thread(target=partial(respond, conn), daemon=True).start()
