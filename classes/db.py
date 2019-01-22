import sqlite3
import os
import datetime


class DB:
    path = None
    conn = None
    c = None
    tables = [
        "CREATE TABLE IF NOT EXISTS WORDS ("
        "    ID INTEGER PRIMARY KEY,"
        "    WORD TEXT NOT NULL UNIQUE"
        ");",

        "CREATE TABLE IF NOT EXISTS WORDS_PROB ("
        "    WORD_ID INTEGER NOT NULL,"
        "    PROBABILITY NUMBER DEFAULT 1,"
        "        FOREIGN KEY (WORD_ID) REFERENCES WORDS(ID),"
        "        CHECK (PROBABILITY BETWEEN 0 AND 1)"
        ");",

        "CREATE TABLE IF NOT EXISTS PHRASES ("
        "    ID INTEGER,"
        "    WORD_ID INTEGER NOT NULL,"
        "    WORD_ORDER INTEGER DEFAULT 0,"
        "        PRIMARY KEY (ID, WORD_ID, WORD_ORDER),"
        "        FOREIGN KEY (WORD_ID) REFERENCES WORDS(ID)"
        ");",

        "CREATE TABLE IF NOT EXISTS PHRASES_PROB ("
        "    PHRASE_ID INTEGER NOT NULL,"
        "    PROBABILITY NUMBER DEFAULT 1,"
        "    ALPHA NUMBER DEFAULT 1,"
        "        FOREIGN KEY (PHRASE_ID) REFERENCES FHRASES(ID),"
        "        CHECK (PROBABILITY BETWEEN 0 AND 1)"
        ");"
    ]

    def __init__(self, path='database/database.db'):
        self.path = path
        self.conn = sqlite3.connect(path)
        self.c = self.conn.cursor()
        self.check_tables()

    def __del__(self):
        self.conn.close()

    def save_backup(self):
        self.conn.close()
        os.rename(self.path, self.path + datetime.datetime.now().strftime("_%Y%m%d_%H%M%S"))

    def check_tables(self):
        for query in self.tables:
            self.execute(query)
        self.commit()
        return None

    def execute_many(self, query, values=(), commit=False):
        self.c.executemany(query, values)
        if commit:
            self.commit()

    def make_readable(self, cursor):
        lenght = len(cursor)
        if lenght > 0:
            lista = [list(row) for row in cursor]
            if lenght == 1:
                if len(lista[0]) == 1:
                    return lista[0][0]
                return lista[0]
            return lista
        else:
            return None

    def query(self, query, print_values=False):
        self.execute(query)
        retorno = self.make_readable(self.c.fetchall())

        if print_values:
            for r in retorno:
                print(r)
        return retorno

    def execute(self, query):
        try:
            self.c.execute(query)
        except sqlite3.Error as e:
            print(query + "\nError running query: ", e.args)
            exit(999)

    def commit(self):
        self.conn.commit()

    def get_word_id(self, word, force_create=False, print_values=False):
        wid = self.query('SELECT ID FROM WORDS WHERE WORD = \'' + word.value + '\';', print_values=print_values)
        if not wid and force_create:
            wid = self.insert_word_id(word)
        return wid

    def insert_word_id(self, word):
        self.execute('INSERT OR IGNORE INTO WORDS (WORD) VALUES(\'' + word.value + '\');')
        self.commit()
        return self.get_word_id(word)

    def insert_word_prob(self, word):
        wid = self.get_word_id(word, force_create=True)
        self.execute('INSERT INTO WORDS_PROB VALUES (' + str(wid) + ', ' + str(word.probability) + ');')
        self.commit()

    def get_phrase_id(self, phrase, force_create=False, print_values=False):
        query = 'SELECT * FROM PHRASES WHERE '
        for i, word in enumerate(phrase.words):
            if i: query += 'AND '
            wid = self.get_word_id(word)
            query += '(WORD_ID = ' + str(wid) + ' AND WORD_ORDER = ' + str(i) + ') '
        query += 'ORDER BY WORD_ORDER;'
        pid = self.query(query, print_values)

        if not pid and force_create:
            pid = self.insert_new_phrase(phrase)
        return pid

    def insert_new_phrase(self, phrase):
        pid = self.query('SELECT MAX(ID) + 1 FROM PHRASES;')
        if not pid: pid = 1
        for i, word in enumerate(phrase.words):
            wid = self.get_word_id(word, force_create=True)
            self.execute('INSERT INTO PHRASES VALUES (' + str(pid) + ', ' + str(wid) + ', ' + str(i) + ');')
        self.commit()
        return pid

    def insert_phrase_prob(self, phrase):
        pid = self.get_phrase_id(phrase, force_create=True)
        self.execute('INSERT INTO PHRASES_PROB VALUES (' + str(pid) + ', ' +
                     str(phrase.probability) + ', ' +
                     str(phrase.alpha) + ');')
        self.commit()

    def insert_text(self, text):
        for phrase in text.phrases:
            phrase.print()
            for word in phrase.words:
                self.insert_word_prob(word)
            self.insert_phrase_prob(phrase)
