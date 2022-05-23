from functools import partial
from queue import Queue
from tkinter import Button, DISABLED, Label, NORMAL, messagebox, simpledialog, Tk
from threading import Thread
from typing import Tuple

from client import Client


turn = False
colors = {"x": "white", "o": "red", " ": "black"}


class ClientThread(Thread):
    def __init__(
        self,
        host: str,
        port: int,
        buttons: list[list[Button]],
        top_text: Label,
        bottom_text: Label,
        moves: Queue[Tuple[int, int]],
    ):
        super().__init__()
        self._client = Client(host, port)

        self._game_code = simpledialog.askstring(
            title="Tic-Tac-Toe", prompt="Enter your game code: "
        )
        top_text.config(text=f"Game code: {self._game_code}")

        self._buttons = buttons
        self._bottom_text = bottom_text
        self._top_text = top_text
        self._moves = moves

    def run(self):
        for msg in self._client.handshake(self._game_code):
            self._bottom_text.config(text=msg)

        self._turn = 1
        self._total_turns = 5

        if self._client.mark != "x":
            self._total_turns -= 1
            global colors
            colors["x"], colors["o"] = colors["o"], colors["x"]

        self._render()

        turns = (self._my_turn, self._opp_turn)
        for i in range(self._client.mark != "x", 9 + (self._client.mark != "x")):
            turns[i & 1]()

    def _my_turn(self):
        self._top_text.config(
            text=f"Turn #{self._turn} Remaining: {self._total_turns - self._turn}"
        )
        self._bottom_text.config(text="Your turn")
        self._turn += 1

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

    while True:
        try:
            addr = simpledialog.askstring("Connection", "Enter IP address of server: ")
            host, port = addr.split(":")
            clientThread = ClientThread(
                host, int(port), buttons, make_label(0), make_label(4), moves
            )
            clientThread.start()
        except:
            messagebox.showerror(
                "Connection error",
                f"Could not connect with a server at {addr}\nTry a different host and port",
            )
        else:
            break

    root.mainloop()
