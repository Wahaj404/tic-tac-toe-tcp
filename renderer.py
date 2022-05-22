from functools import partial
from operator import contains
from queue import Queue
from tkinter import BOTH, Button, DISABLED, Label, NORMAL, simpledialog, Tk
from threading import Thread

from client import Client

turn = False
colors = {"x": "white", "o": "red", " ": "papaya whip"}


class ClientThread(Thread):
    def __init__(self, buttons, top_text, bottom_text, moves):
        super().__init__()

        game_code = simpledialog.askstring(
            title="Tic-Tac-Toe", prompt="Enter your game code: "
        )
        self._client = Client(game_code)

        self._buttons = buttons
        self._bottom_text = bottom_text
        self._moves = moves

        top_text.config(text=f"Game code: {game_code}")

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
        return self._client.show_board()

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
            self._bottom_text.config(text=txt, fg="green" if "won" in txt else "red")
            raise SystemExit()


def mark(moves, i, j):
    global turn
    if turn:
        moves.put((i, j))


def make_button(frame, moves, i, j):
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


def font(size: int):
    return ("arial", size, "bold")


if __name__ == "__main__":
    root = Tk()
    root.title("Tic-Tac-Toe")

    def make_label(row):
        lbl = Label(font=font(20), bg="black", fg="white", width=30)
        lbl.grid(row=row, column=0, columnspan=3)
        return lbl

    moves = Queue()
    buttons = [[make_button(root, moves, i, j) for j in range(3)] for i in range(3)]

    clientThread = ClientThread(buttons, make_label(0), make_label(4), moves)
    clientThread.start()

    root.mainloop()
