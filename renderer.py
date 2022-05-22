from functools import partial
from queue import Queue
from tkinter import Button, DISABLED, Label, NORMAL, simpledialog, Tk
from threading import Thread
from typing import Tuple

from client import Client


turn = False
colors = {"x": "white", "o": "red", " ": "black"}


class ClientThread(Thread):
    def __init__(
        self,
        buttons: list[list[Button]],
        top_text: Label,
        bottom_text: Label,
        moves: Queue[Tuple[int, int]],
    ):
        super().__init__()

        game_code = simpledialog.askstring(
            title="Tic-Tac-Toe", prompt="Enter your game code: "
        )
        self._client = Client(game_code)

        top_text.config(text=f"Game code: {game_code}")

        self._buttons = buttons
        self._bottom_text = bottom_text
        self._top_text = top_text
        self._moves = moves


    def run(self):
        for msg in self._client.handshake():
            self._bottom_text.config(text=msg)

        if self._client.mark != "x":
            global colors
            colors["x"], colors["o"] = colors["o"], colors["x"]

        self._render()

        turns = (self._my_turn, self._opp_turn)
        for i in range(self._client.mark != "x", 9 + (self._client.mark != "x")):
            turns[i & 1]()

    def _my_turn(self):
        self._bottom_text.config(text="Your turn")

        global turn
        turn = True
        i, j = self._moves.get()
        turn = False

        self._send_move(i, j)
        self._render()

    def _opp_turn(self):
        self._bottom_text.config(text="Opponent's turn")
        self._render()

    def _send_move(self, i, j):
        self._client.send(f"{i}{j}")

    def _get_board(self):
        return self._client.board()

    def _render(self):
        board = self._get_board()
        global colors
        for i in range(3):
            for j in range(3):
                self._buttons[i][j].config(
                    text=board[i, j],
                    state=NORMAL if board[i, j] == " " else DISABLED,
                    disabledforeground=colors[board[i, j]],
                )

        if board.finished():
            txt = self._get_board()
            fg = "green" if "won" in txt else "red"
            self._bottom_text.config(text=txt, fg=fg)
            self._top_text.config(text="Game over", fg=fg)
            raise SystemExit()


def mark(moves: Queue[Tuple[int, int]], i: int, j: int):
    global turn
    if turn:
        moves.put((i, j))


def make_button(frame: Tk, moves: Queue[Tuple[int, int]], i: int, j: int):
    button = Button(
        frame,
        padx=1,
        bg="black",
        width=3,
        text=" ",
        font=font(60),
        relief="sunken",
        bd=10,
    )
    button.config(command=partial(mark, moves, i, j))
    button.grid(row=i + 1, column=j)
    return button


def make_label(row: int):
    lbl = Label(font=font(20), bg="black", fg="white", width=30)
    lbl.grid(row=row, column=0, columnspan=3)
    return lbl


def font(size: int):
    return ("arial", size, "bold")


if __name__ == "__main__":
    root = Tk()
    root.title("Tic-Tac-Toe")

    moves = Queue()
    buttons = [[make_button(root, moves, i, j) for j in range(3)] for i in range(3)]

    clientThread = ClientThread(buttons, make_label(0), make_label(4), moves)
    clientThread.start()

    root.mainloop()
