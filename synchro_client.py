import socket
import time
import pandas as pd
from datetime import datetime
import win32api

from connection import PORT, SIZE, decode_timestamp
from discovery import get_server_address

HOST = None
while True:
    HOST = get_server_address()
    if HOST is None:
        print("Server not found")
        time.sleep(1)
    else:
        break

print(f"Server address: {HOST}:{PORT}")

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

y_n = input("Do you want to update this computer system's time? (y/n): ")

if y_n == "y":
    offset_s = server_offset_seconds - win32api.GetTimeZoneInformation()[0]*3600
    corrected_time = datetime.fromtimestamp(time.time() + offset_s)
    win32api.SetSystemTime(corrected_time.year, corrected_time.month, corrected_time.weekday(), corrected_time.day,
                           corrected_time.hour, corrected_time.minute, corrected_time.second,
                           int(corrected_time.microsecond/1000))
