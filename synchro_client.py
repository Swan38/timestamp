import socket
import time
from datetime import datetime
import pandas as pd

from connection import PORT, SIZE, decode_timestamp

HOST = "192.168.137.1"  # The server's hostname or IP address

measures: pd.DataFrame = pd.DataFrame(columns=("elapsed_time", "server_offset_seconds"))

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    for _ in range(200):
        send_time = time.time()
        s.sendall(b"A")
        bin_server_time = s.recv(SIZE)
        recv_time = time.time()
        server_time = decode_timestamp(bin_server_time)
        duration = recv_time - send_time
        server_offset = server_time - ((send_time + recv_time)/2)

        # print(f"Duration synchro (→⏱️ ←): f{duration*100:.2f} ms")
        # print("Server time:", datetime.fromtimestamp(server_time))
        # print("Server offset:", server_offset)
        # print("")

        measures.loc[len(measures.index)] = (duration, server_offset)

# print(measures)
# print(measures.describe())

best_measures = measures[measures["elapsed_time"] <= measures["elapsed_time"].median()]

# print(best_measures)
# print(best_measures.describe())

server_offset_seconds = best_measures["server_offset_seconds"].mean()

print(f"server_offset_seconds = {server_offset_seconds*1000:.3f} ± {best_measures['server_offset_seconds'].std()*1000:.3f} ms")
