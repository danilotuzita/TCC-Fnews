import sqlite3


class DB:
    conn = None
    c = None

    indispensable_tables = [
        'words'
    ]

    def __init__(self):
        self.conn = sqlite3.connect('database.db')
        self.c = self.conn.cursor()

    def __del__(self):
        self.conn.close()

    def check_tables(self):
        for i in self.indispensable_tables:
            self.c.execute("SELECT NAME FROM SQLITE_MASTER WHERE TYPE='table' AND NAME='?';", (i,))
            if not self.c.fetchall():
                # c.execute('CREATE TABLE WORDS (WORD TEXT, PROBABILITY REAL);')
                print(i + " - Não EXISTE!!!")
                return i
        return None

    def execute_many(self, query, values=(), commit=False):
        self.c.executemany(query, values)
        if commit:
            self.commit()

    def query(self, query, print_values=False):
        self.c.execute(query)
        retorno = self.c.fetchall()
        if print_values:
            for r in retorno:
                print(r)
        return retorno

    def commit(self):
        self.conn.commit()
