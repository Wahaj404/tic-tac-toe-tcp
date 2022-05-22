from socket import socket

from board import Board
from util import CONNECTION, recv, send


class Client:
    def __init__(self, game_code: str):
        self._conn = socket()
        self._conn.connect(CONNECTION)
        self.send(game_code)

    def send(self, msg: str):
        send(self._conn, msg)

    def board(self):
        msg = recv(self._conn)
        return recv(self._conn) if msg == "game over" else Board(msg)

    def handshake(self):
        yield recv(self._conn)  # game created or found
        yield recv(self._conn)  # both players connected
        self.mark = recv(self._conn)
