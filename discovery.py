import socket
from typing import Union
from multiprocessing.pool import ThreadPool

from connection import PORT

def get_server_address() -> Union[str, None]:
    def _test_address(address: str) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            # print(f"Testing adress {address}")
            try:
                s.connect((address, PORT))
            except (TimeoutError, ConnectionError) as error:
                return False
            return True

    pool = ThreadPool(processes=254)

    addresses = [f"192.168.137.{i}" for i in range(1, 255)]
    results = pool.map(_test_address, addresses)

    if True in results:
        return addresses[results.index(True)]
    else:
        return None

if __name__ == "__main__":
    print(f"The server address is {get_server_address()}")
