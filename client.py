from socket import socket

from board import Board
from util import recv, send


class Client:
    def __init__(self, host: str, port: int):
        self._conn = socket()
        self._conn.connect((host, port))

    def send(self, msg: str):
        send(self._conn, msg)

    def board(self):
        msg = recv(self._conn)
        return recv(self._conn) if msg == "game over" else Board(msg)

    def handshake(self, game_code: str):
        self.send(game_code)
        yield recv(self._conn)  # game created or found
        yield recv(self._conn)  # both players connected
        self.mark = recv(self._conn)
