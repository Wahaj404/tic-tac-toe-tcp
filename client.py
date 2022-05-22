from socket import socket
from board import Board
from util import PORT


class Client:
    def __init__(self):
        self.conn = socket()
        self.conn.connect(('localhost', PORT))

    def _recv(self):
        return self.conn.recv(1024).decode()

    def _send(self, msg):
        self.conn.send(msg.encode())

    def _show_board(self):
        msg = self._recv()
        if msg == 'game over':
            print(self._recv())
            return True
        else:
            print(Board(msg))
            return False

    def start(self):
        game_code = input('Enter your game code: ')
        self._send(game_code)
        print(self._recv())
        print(self._recv())
        mark = self._recv()
        if mark == 'x':
            self._show_board()
            for _ in range(5):
                move = input('move: ')
                self._send(move)

                if self._show_board():
                    return

                if self._show_board():
                    return
        else:
            self._show_board()
            for _ in range(4):
                if self._show_board():
                    return

                move = input('move: ')
                self._send(move)

                if self._show_board():
                    return


client = Client()
client.start()
