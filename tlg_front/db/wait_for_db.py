import os
import socket
import time

if __name__ == "__main__":
    port = int(os.environ["POSTGRES_PORT_CONTAINER"])  # 5432
    host = os.environ["POSTGRES_HOST"]  # db
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            s.connect((host, port))
            s.close()
            break
        except socket.error as ex:
            time.sleep(1)
