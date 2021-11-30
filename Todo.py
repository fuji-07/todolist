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

    def finish_task(self, task_id: int) -> None:
        """ Change task status from todo to finished.

        Args:
            task_id(int): task id

        Returns:
            None

        """

        sql: str = f'UPDATE {Model.TABLENAME} SET status={Model.Status.FINISHED} WHERE id=?'

        self.cur.execute(sql, (task_id,))
        self.conn.commit()

    def get_todo_ids(self) -> list:
        """ Return todo task id list.

        Returns:
            todo_ids(list): todo task id list

        """

        todo_ids: list = []
        sql: str = f'SELECT id FROM {Model.TABLENAME} WHERE status={Model.Status.TODO}'

        self.cur.execute(sql)
        results = self.cur.fetchall()

        for row in results:
            todo_ids.append(row[0])

        return todo_ids

    def get_todo_names(self) -> list:
        """ Return todo task name list.

        Returns:
            todo_names(list): todo task name list

        """

        todo_names: list = []
        sql: str = f'SELECT name FROM {Model.TABLENAME} WHERE status={Model.Status.TODO}'

        self.cur.execute(sql)
        results = self.cur.fetchall()

        for row in results:
            todo_names.append(row[0])

        return todo_names

    def get_finished_ids(self) -> list:
        """ Return finished task id list.

        Returns:
            finished_ids(list): finished task id list

        """

        finished_ids: list = []
        sql: str = f'SELECT id FROM {Model.TABLENAME} WHERE status={Model.Status.FINISHED}'

        self.cur.execute(sql)
        results = self.cur.fetchall()

        for row in results:
            finished_ids.append(row[0])

        return finished_ids

    def get_finished_names(self) -> list:
        """ Return finished taskname list.

        Returns:
            finished_names(list): finished taskname list

        """

        finished_names: list = []
        sql: str = f'SELECT name FROM {Model.TABLENAME} WHERE status={Model.Status.FINISHED}'

        self.cur.execute(sql)
        results = self.cur.fetchall()

        for row in results:
            finished_names.append(row)

        return finished_names


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

        self.todo_listbox = tk.Listbox(todo_frame, selectmode='single')
        self.todo_listbox.pack()
        # ----------------------

        # ---finishedlist related---
        finished_frame = tk.Frame(self)
        finished_frame.pack(side=tk.LEFT)

        finished_label = tk.Label(finished_frame, text='完了済み')
        finished_label.pack()

        self.finished_listbox = tk.Listbox(finished_frame, selectmode='single')
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

        self.todo_list = self.model.get_todo_ids()
        self.finished_list = self.model.get_finished_ids()

        win.protocol('WM_DELETE_WINDOW', self.__window_close)

        self.view.set_todo_listbox(self.model.get_todo_names())
        self.view.set_finished_listbox(self.model.get_finished_names())

        self.view.add_task_button['command'] = lambda: self.__add_task(
            event=None)
        self.view.task_entry.bind('<Return>', self.__add_task)

        self.view.todo_listbox.bind(
            '<Double-Button-1>', self.__finish_task)

    def __add_task(self, event) -> None:
        """ Add task and set todo listbox value.
        """
        name = self.view.task_entry.get()
        if name:
            self.model.add_task(self.view.task_entry.get())

            self.todo_list = self.model.get_todo_ids()
            self.view.set_todo_listbox(self.model.get_todo_names())

            self.view.task_entry.delete(0, tk.END)

    def __finish_task(self, event) -> None:
        """ Change task status and set todo and finished listbox values.
        """
        idx = self.view.todo_listbox.curselection()

        if idx:
            idx = idx[0]
            self.model.finish_task(self.todo_list[idx])

            self.todo_list = self.model.get_todo_ids()
            self.finished_list = self.model.get_finished_ids()

            self.view.set_todo_listbox(self.model.get_todo_names())
            self.view.set_finished_listbox(self.model.get_finished_names())

    def __window_close(self):
        """ Close database connection and window.
        """
        self.model.close_database()
        self.view.master.destroy()
