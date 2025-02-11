# https://stackoverflow.com/a/29158947
from tkinter import *
import random
import time

root = Tk()
root.title = "Game"
root.resizable(0,0)
root.wm_attributes("-topmost", 1)

canvas = Canvas(root, width=500, height=400, bd=0, highlightthickness=0)
canvas.pack()

class Ball:
    def __init__(self, canvas, color):
        self.canvas = canvas
        self.id = canvas.create_oval(10, 10, 25, 25, fill=color)
        self.canvas.move(self.id, 245, 100)

        self.canvas.bind("<Button-1>", self.canvas_onclick)
        self.text_id = self.canvas.create_text(300, 200, anchor='se')
        self.canvas.itemconfig(self.text_id, text='hello')

    def canvas_onclick(self, event):
        self.canvas.itemconfig(
            self.text_id, 
            text="You clicked at ({}, {})".format(event.x, event.y)
        )

    def draw(self):
        self.canvas.move(self.id, 1, 1)
        self.canvas.after(50, self.draw)




ball = Ball(canvas, "blue")
ball.draw()  #Changed per Bryan Oakley's comment.
root.mainloop()