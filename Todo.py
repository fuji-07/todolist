import tkinter as tk
import sqlite3


class Status:
    TODO: int = 0
    FINISHED: int = 1


class TodoModel:
    DBNAME: str = 'todolist.db'
    TABLENAME: str = 'todolist'

    def __init__(self) -> None:
        self.__open_database()
        self.__create_table()

    def __open_database(self) -> None:
        self.conn: sqlite3.Connection = sqlite3.connect(TodoModel.DBNAME)
        self.cur: sqlite3.Cursor = self.conn.cursor()

    def close_database(self) -> None:
        self.conn.close()

    def __create_table(self) -> None:
        self.cur.execute(f'CREATE TABLE IF NOT EXISTS {TodoModel.TABLENAME}('
                         'id INTEGER PRIMARY KEY AUTOINCREMENT,'
                         'name TEXT NOT NULL,'
                         f'status INTEGER CHECK(status={Status.TODO} OR status={Status.FINISHED})'
                         ')')

        self.conn.commit()

    def add_todo(self, name: str) -> None:
        sql: str = f'INSERT INTO {TodoModel.TABLENAME}(name, status) VALUES(?, {Status.TODO})'

        self.cur.execute(sql, (name,))
        self.conn.commit()

    def finish_todo(self, name: str) -> None:
        sql: str = f'UPDATE {TodoModel.TABLENAME} SET status={Status.FINISHED} WHERE name=?'

        self.cur.execute(sql, (name,))
        self.conn.commit()

    def get_todo(self) -> list:
        todo_list: list = []
        sql: str = f'SELECT name FROM {TodoModel.TABLENAME} WHERE status={Status.TODO}'

        for row in self.cur.execute(sql):
            todo_list.append(row[0])

        return tuple(todo_list)

    def get_finished(self) -> list:
        finished_list: list = []
        sql: str = f'SELECT name FROM {TodoModel.TABLENAME} WHERE status={Status.FINISHED}'

        for row in self.cur.execute(sql):
            finished_list.append(row[0])

        return tuple(finished_list)


class TodoView(tk.Frame):

    def __init__(self, master=None) -> None:
        super().__init__(master)
        self.master = master

        self.master.title('TodoList')
        self.master.minsize(width=400, height=300)

        self.pack()
        self.create_widgets()

    def create_widgets(self):
        title_label = tk.Label(self, text='TodoList')
        title_label.pack()

        add_todo_frame = tk.Frame(self)
        add_todo_frame.pack()

        self.todo_entry = tk.Entry(add_todo_frame)
        self.todo_entry.pack(side=tk.LEFT)
        self.add_todo_button = tk.Button(add_todo_frame, text='追加')
        self.add_todo_button.pack(side=tk.LEFT)

        # todoリスト関連
        todo_frame = tk.Frame(self)
        todo_frame.pack(side=tk.LEFT)

        todo_label = tk.Label(todo_frame, text='未完了')
        todo_label.pack()

        self.todo_listbox = tk.Listbox(todo_frame)
        self.todo_listbox.pack()

        # finishedリスト関連
        finished_frame = tk.Frame(self)
        finished_frame.pack(side=tk.LEFT)

        finished_label = tk.Label(finished_frame, text='完了済み')
        finished_label.pack()

        self.finished_listbox = tk.Listbox(finished_frame)
        self.finished_listbox.pack()

    def init_todo_listbox(self, todo_list: list) -> None:
        var = tk.StringVar(value=todo_list)
        self.todo_listbox.config(listvariable=var)

    def init_finished_listbox(self, finished_list: list) -> None:
        var = tk.StringVar(value=finished_list)
        self.finished_listbox.config(listvariable=var)


class TodoController:
    def __init__(self, win) -> None:
        self.model = TodoModel()
        self.view = TodoView(win)

        self.view.init_todo_listbox(self.model.get_todo())
        self.view.init_finished_listbox(self.model.get_finished())
