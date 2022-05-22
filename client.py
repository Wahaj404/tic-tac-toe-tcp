from socket import socket
from board import Board
from util import CONNECTION

class Client:
    def __init__(self, game_code):
        self._conn = socket()
        self._conn.connect(CONNECTION)
        self._send(game_code)

    def _recv(self) -> str:
        msg = self._conn.recv(1024).decode()
        print(f'{msg=}')
        return msg

    def _send(self, msg):
        self._conn.send(msg.encode())

    def _show_board(self) -> Board | str:
        msg = self._recv()
        return self._recv() if msg == 'game over' else Board(msg)


    def handshake(self):
        yield self._recv() # game created or game found
        yield self._recv() # both players connected
        self.mark = self._recv()
