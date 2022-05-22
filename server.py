from socket import socket
from threading import Thread
from time import sleep

from board import Board
from util import CONNECTION, recv, send


class Game(Thread):
    _marks = ("x", "o")
    _delay_gap = 0.5

    def __init__(self, x: socket, o: socket):
        super().__init__()

        self._players = (x, o)
        for player in self._players:
            send(player, "Both players connected, game starting.")

        self._board = Board()

    def run(self):
        self._send_marks()
        self._game_loop()
        self._send_results(self._board.winner())
        self._close_connections()

    def _send_marks(self):
        for player, mark in zip(self._players, self._marks):
            send(player, mark, self._delay_gap)

    def _game_loop(self):
        turn = 0
        while not self._board.finished():
            for player in self._players:
                send(player, repr(self._board))
            self._board[map(int, recv(self._players[turn]))] = self._marks[turn]
            turn = (turn + 1) & 1

        for player in self._players:
            send(player, repr(self._board), self._delay_gap)
            send(player, "game over")

    def _send_results(self, winner: str | None):
        if winner is None:
            for player in self._players:
                send(player, "The game was a draw")
        else:
            send(self._players[winner != "x"], "you won")
            send(self._players[winner == "x"], "you lost")

    def _close_connections(self):
        for player in self._players:
            player.close()


class Server:
    def __init__(self):
        self._socket = socket()
        self._socket.bind(CONNECTION)
        self._socket.listen()

    def listen(self):
        pending = {}
        while True:
            conn, _ = self._socket.accept()
            game_code = recv(conn)
            if game_code in pending:
                send(conn, "Game found, connecting.")
                sleep(1.0)
                Game(pending.pop(game_code), conn).start()
            else:
                pending[game_code] = conn
                send(conn, "Waiting for opponent to join.")


if __name__ == "__main__":
    Server().listen()
