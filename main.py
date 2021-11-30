import Todo as td
import tkinter as tk

win = tk.Tk()
tdctrl = td.Controller(win)
win.resizable(width=False, height=False)
win.mainloop()
