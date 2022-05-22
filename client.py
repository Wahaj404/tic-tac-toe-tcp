from socket import socket

from board import Board
from util import CONNECTION, recv, send


class Client:
    def __init__(self, game_code):
        self._conn = socket()
        self._conn.connect(CONNECTION)
        self.send(game_code)

    def _recv(self) -> str:
        return recv(self._conn)

    def send(self, msg):
        send(self._conn, msg)

    def show_board(self) -> Board | str:
        msg = self._recv()
        return self._recv() if msg == 'game over' else Board(msg)

    def handshake(self):
        yield self._recv()  # game created or found
        yield self._recv()  # both players connected
        self.mark = self._recv()
