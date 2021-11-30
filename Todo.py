import tkinter as tk
import sqlite3
from enum import IntEnum
from tkinter.constants import NO


class Model:
    DBNAME: str = './db/todolist.db'
    TABLENAME: str = 'todolist'

    class Status(IntEnum):
        TODO = 0
        FINISHED = 1

    def __init__(self) -> None:
        self.__open_database()
        self.__create_table()

    def __open_database(self) -> None:
        """ Open database connection and get cursor.
        """

        self.conn: sqlite3.Connection = sqlite3.connect(Model.DBNAME)
        self.cur: sqlite3.Cursor = self.conn.cursor()

    def close_database(self) -> None:
        """ Close database connection.
        """

        self.conn.close()

    def __create_table(self) -> None:
        """ Create todolist table if not exists.
        """

        self.cur.execute(f'''
                        CREATE TABLE IF NOT EXISTS {Model.TABLENAME}(
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            status INTEGER CHECK(status={Model.Status.TODO} OR status={Model.Status.FINISHED})
                        )''')

    def add_task(self, name: str) -> None:
        """ Add task to todolist table.

        Args:
            name(str): task name

        Returns:
            None

        """

        sql: str = f'INSERT INTO {Model.TABLENAME}(name, status) VALUES(?, {Model.Status.TODO})'

        self.cur.execute(sql, (name,))
        self.conn.commit()

    def finish_task(self, name: str) -> None:
        """ Change task status from todo to finished.

        Args:
            name(str): task name

        Returns:
            None

        """

        sql: str = f'UPDATE {Model.TABLENAME} SET status={Model.Status.FINISHED} WHERE name=?'

        self.cur.execute(sql, (name,))
        self.conn.commit()

    def get_todo(self) -> list:
        """ Return todo tasklist.

        Returns:
            todo_list(list): todo tasklist

        """

        todo_list: list = []
        sql: str = f'SELECT name FROM {Model.TABLENAME} WHERE status={Model.Status.TODO}'

        for row in self.cur.execute(sql):
            todo_list.append(row[0])

        return todo_list

    def get_finished(self) -> list:
        """ Return finished tasklist.

        Returns:
            finished_list(list): finished tasklist

        """

        finished_list: list = []
        sql: str = f'SELECT name FROM {Model.TABLENAME} WHERE status={Model.Status.FINISHED}'

        for row in self.cur.execute(sql):
            finished_list.append(row[0])

        return finished_list


class View(tk.Frame):

    def __init__(self, master=None) -> None:
        super().__init__(master)
        self.master = master

        self.master.title('TodoList')
        self.master.minsize(width=400, height=300)

        self.pack()
        self.create_widgets()

    def create_widgets(self):
        """ Create tkinter widgets.
        """

        title_label = tk.Label(self, text='TodoList')
        title_label.pack()

        # ---add task entry related---
        add_task_frame = tk.Frame(self)
        add_task_frame.pack()

        self.task_entry = tk.Entry(add_task_frame)
        self.task_entry.pack(side=tk.LEFT)
        self.add_task_button = tk.Button(add_task_frame, text='追加')
        self.add_task_button.pack(side=tk.LEFT)
        # ----------------------------

        # ---todolist related---
        todo_frame = tk.Frame(self)
        todo_frame.pack(side=tk.LEFT)

        todo_label = tk.Label(todo_frame, text='未完了')
        todo_label.pack()

        self.todo_listbox = tk.Listbox(todo_frame)
        self.todo_listbox.pack()
        # ----------------------

        # ---finishedlist related---
        finished_frame = tk.Frame(self)
        finished_frame.pack(side=tk.LEFT)

        finished_label = tk.Label(finished_frame, text='完了済み')
        finished_label.pack()

        self.finished_listbox = tk.Listbox(finished_frame)
        self.finished_listbox.pack()
        # --------------------------

    def set_todo_listbox(self, todo_list: list) -> None:
        """ Set todo_listbox value.

        Args:
            todo_list(list): todo tasklist

        """

        var = tk.StringVar(value=todo_list)
        self.todo_listbox.config(listvariable=var)

    def set_finished_listbox(self, finished_list: list) -> None:
        """ Set finished_listbox value.

        Args:
            finished_list(list): finished tasklist

        """
        var = tk.StringVar(value=finished_list)
        self.finished_listbox.config(listvariable=var)


class Controller:
    def __init__(self, win) -> None:
        self.model = Model()
        self.view = View(win)

        self.view.set_todo_listbox(self.model.get_todo())
        self.view.set_finished_listbox(self.model.get_finished())

        self.view.add_task_button['command'] = self.__add_task_button_clicked
        self.view.todo_listbox.bind(
            '<Double-Button-1>', self.__todo_listbox_doubleclick)

    def __add_task_button_clicked(self) -> None:
        """ Add task and set todo listbox value.
        """
        self.model.add_task(self.view.task_entry.get())
        self.view.set_todo_listbox(self.model.get_todo())

        self.view.task_entry.delete(0, tk.END)

    def __todo_listbox_doubleclick(self, event) -> None:
        """ Change task status and set todo and finished listbox values.
        """
        idx = self.view.todo_listbox.curselection()

        if idx:
            name = self.view.todo_listbox.get(idx)
            self.model.finish_task(name)

            self.view.set_todo_listbox(self.model.get_todo())
            self.view.set_finished_listbox(self.model.get_finished())
