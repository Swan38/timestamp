import socket
import time
import pandas as pd
from datetime import datetime
import win32api

from connection import PORT, SIZE, decode_timestamp
from discovery import get_server_address

TOLERANCE_MS = 1

HOST = None
while True:
    HOST = get_server_address()
    if HOST is None:
        print("Server not found")
        time.sleep(1)
    else:
        break

print(f"Server address: {HOST}:{PORT}")

def measure_server_offset_second(*, number_of_measure: int = 150) -> float:
    measures: pd.DataFrame = pd.DataFrame(columns=("elapsed_time", "server_offset_seconds"))

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        for _ in range(number_of_measure):
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

    return server_offset_seconds

def correct_time_offset(measured_offset_seconds: float, overshoot_seconds: float = 0):
    applied_offset_seconds = measured_offset_seconds + overshoot_seconds - win32api.GetTimeZoneInformation()[0]*3600
    corrected_time = datetime.fromtimestamp(time.time() + applied_offset_seconds)
    win32api.SetSystemTime(corrected_time.year, corrected_time.month, corrected_time.weekday(), corrected_time.day,
                           corrected_time.hour, corrected_time.minute, corrected_time.second,
                           int(corrected_time.microsecond/1000))

if __name__ == "__main__":
    server_offset_seconds = measure_server_offset_second(number_of_measure=250)
    correct_time_offset(server_offset_seconds)

    computation_time_offset = 0

    for i in range(150):
        left_offset = measure_server_offset_second()
        if abs(left_offset) < TOLERANCE_MS / 1000:
            print(f"Goal reached (±{TOLERANCE_MS:.2f} ms) in {i + 1} occurences.")
            break
        elif left_offset > 0:
            computation_time_offset += .002
        else:
            computation_time_offset -= .002
        print(f"Goal not reached, computation time -> {computation_time_offset}")
        # computation_time_offset = pd.concat([computation_time_offset, pd.Series(left_offset)])
        correct_time_offset(left_offset, computation_time_offset)

    # print("Final offset is ")

    # y_n = input("Do you want to update this computer system's time? (y/n): ")

    # if y_n == "y":
    #     offset_s = server_offset_seconds - win32api.GetTimeZoneInformation()[0]*3600 + .007
    #     corrected_time = datetime.fromtimestamp(time.time() + offset_s)
    #     win32api.SetSystemTime(corrected_time.year, corrected_time.month, corrected_time.weekday(), corrected_time.day,
    #                            corrected_time.hour, corrected_time.minute, corrected_time.second,
    #                            int(corrected_time.microsecond/1000))
