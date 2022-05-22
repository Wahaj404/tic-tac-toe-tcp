from socket import socket
from threading import Thread
from time import sleep

from board import Board
from util import CONNECTION, recv, send


class Game(Thread):
    marks = ('x', 'o')
    delay_gap = 0.5

    def __init__(self, x: socket, o: socket):
        super().__init__()

        self.players = (x, o)
        for player in self.players:
            send(player, 'Both players connected, game starting.')

        self.board = Board()

    def run(self):
        self._send_marks()
        self._game_loop()
        self._send_results(self.board.winner())
        self._close_connections()

    def _send_marks(self):
        for player, mark in zip(self.players, self.marks):
            send(player, mark, self.delay_gap)

    def _game_loop(self):
        turn = 0
        while not self.board.finished():
            for player in self.players:
                send(player, repr(self.board))
            self.board[map(int, recv(self.players[turn]))] = self.marks[turn]
            turn = (turn + 1) & 1

        for player in self.players:
            send(player, repr(self.board), self.delay_gap)
            send(player, 'game over')

    def _send_results(self, winner: str):
        if winner is None:
            for player in self.players:
                send(player, 'the game was a draw')
        else:
            send(self.players[winner != 'x'], 'you won')
            send(self.players[winner == 'x'], 'you lost')

    def _close_connections(self):
        for player in self.players:
            player.close()


class Server:
    def __init__(self):
        self.server = socket()
        self.server.bind(CONNECTION)
        self.server.listen()

    def listen(self):
        pending = {}
        while True:
            conn, _ = self.server.accept()
            game_code = recv(conn)
            if game_code in pending:
                send(conn, 'Game found, connecting.')
                sleep(1.0)
                Game(pending.pop(game_code), conn).start()
            else:
                pending[game_code] = conn
                send(conn, 'Game created, waiting for opponent to join.')


if __name__ == '__main__':
    server = Server()
    server.listen()
