from socket import socket
from threading import Thread
from board import Board
from util import CONNECTION
import time


class Game(Thread):
    def __init__(self, p1, p2):
        super().__init__()
        self.players = [p1, p2]
        for player in self.players:
            player.send('Both players connected, game starting.'.encode())
        self.board = Board()

    def run(self):
        marks = ['x', 'o']
        for m, p in zip(marks, self.players):
            p.send(m.encode())
        time.sleep(0.5)
        for turn in range(9):
            print(f'move #{turn}')
            if self.board.winner() is not None:
                break
            for player in self.players:
                player.send(repr(self.board).encode())
            turn &= 1
            while True:
                try:
                    move = self.players[turn].recv(1024).decode()
                    self.board[tuple(map(int, move))] = marks[turn]
                except Exception as e:
                    print(e)
                else:
                    break

        for player in self.players:
            player.send(repr(self.board).encode())
            time.sleep(0.5)
            player.send('game over'.encode())
        time.sleep(0.5)
        winner = self.board.winner()
        if winner is None:
            for player in self.players:
                player.send('the game was a draw'.encode())
        else:
            self.players[winner != 'x'].send('you won'.encode())
            self.players[winner == 'x'].send('you lost'.encode())

class Server:
    def __init__(self):
        self.server = socket()
        self.server.bind(CONNECTION)
        self.server.listen()
        self.pending = {}

    def start(self):
        while True:
            conn, _ = self.server.accept()
            game_code = conn.recv(1024).decode()
            if game_code in self.pending:
                conn.send('Game found, connecting.'.encode())
                time.sleep(1.0)
                Game(self.pending[game_code], conn).start()
                del self.pending[game_code]
            else:
                self.pending[game_code] = conn
                conn.send('Game created, waiting for opponent to join.'.encode())


if __name__ == '__main__':
    server = Server()
    server.start()