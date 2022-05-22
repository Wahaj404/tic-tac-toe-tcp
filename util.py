from socket import socket
from time import sleep

PORT = 4015
CONNECTION = ("localhost", PORT)


def send(conn: socket, msg: str, delay: float = 0.0):
    conn.send(msg.encode())
    sleep(delay)


def recv(conn: socket):
    return conn.recv(1024).decode()
