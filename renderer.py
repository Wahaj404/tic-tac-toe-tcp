from functools import partial
from tkinter import *
import tkinter.simpledialog as simpledialog
from client import Client
from threading import Thread
from board import Board
from queue import Queue

turn = False

class ClientThread(Thread):
    def __init__(self, buttons, label, q):
        super().__init__()      
        game_code = simpledialog.askstring(title="Tic-Tac-Toe", prompt='Enter your game code: ')
        self.client = Client(game_code)
        self.buttons = buttons
        self.label = label
        self.q = q

    def run(self):
        global turn
        for msg in self.client.handshake():
            self.label.config(text=msg)
        self.render(self.get_board())
        if self.client.mark == 'x':
            for _ in range(5):
                self.label.config(text='Your turn')
                turn = True
                i, j = self.q.get()
                self.send_move(i, j)
                turn = False
                self.render(self.get_board())
                self.label.config(text="Opponent's turn")
                self.render(self.get_board())
        else:            
            for _ in range(4):
                self.label.config(text="Opponent's turn")
                self.render(self.get_board())
                self.label.config(text='Your turn')
                turn = True
                i, j = self.q.get()
                turn = False
                self.send_move(i, j)
                self.render(self.get_board())
            self.label.config(text="Opponent's turn")
            self.render(self.get_board())

    def send_move(self, i, j):
        self.client._send(f'{i}{j}')

    def get_board(self):
        return self.client._show_board()


    def render(self, state : Board):
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].config(text=state[i, j], state=NORMAL if state[i, j] == ' ' else DISABLED)
        if state.finished():
            self.label.config(text=self.get_board())
            raise SystemExit()


def mark(i, j, q):
    global turn
    if turn and q.qsize() == 0: 
        q.put((i, j))


def make_button(frame, i, j, q):
    button = Button(frame, padx=1, bg='papaya whip', width=3, text='   ', font=('arial', 60, 'bold'), relief='sunken', bd=10)
    button.config(command=partial(mark, i, j, q))
    button.grid(row=i, column=j)
    return button

q = Queue()
root = Tk()
root.title('Tic-Tac-Toe')
buttons = [[make_button(root, i, j, q) for j in range(3)] for i in range(3)]
label = Label(text='', font=('arial', 20, 'bold'))
label.grid(row=3, column=0, columnspan=3)
clientThread = ClientThread(buttons, label, q)
clientThread.start()
root.mainloop()
clientThread.join()