import sqlite3
import os
import datetime


class DB:
    path = None
    filename = None

    debug = False
    debug_filename = None
    terminal = None

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

    def __init__(self, path='database/', filename='database', debug=False, debug_filename='database_debug'):
        self.path = path
        self.filename = filename
        self.conn = sqlite3.connect(path + filename + '.db')
        self.c = self.conn.cursor()
        self.check_tables()

        self.debug = debug
        if debug:
            self.open_debug(debug_filename)

    def __del__(self):
        self.conn.close()
        if self.debug:
            self.debug.close()

    def open_debug(self, debug_filename):
        self.debug = open(self.path + debug_filename+'.log', 'w+')

    def save_backup(self, directory=None, rel_directory='bkp/'):
        self.conn.close()
        new_directory = self.path + rel_directory + self.filename
        if directory:
            new_directory = directory + self.filename
        old_filename = self.path + self.filename + '.db'
        new_filename = new_directory + datetime.datetime.now().strftime("_%Y%m%d-%H%M%S.db")
        os.rename(old_filename, new_filename)
        return new_filename

    def check_tables(self):
        for query in self.tables:
            self.execute(query)
        self.commit()
        return None

    def execute_many(self, query, values=(), commit=False):
        self.c.executemany(query, values)
        if commit:
            self.commit()

    # le o cursor e retorna o valor fora de uma lista se o cursor for só uma linha
    def make_readable(self, cursor):
        length = len(cursor)
        if length > 0:
            lista = [list(row) for row in cursor]
            if length == 1:  # se for só uma linha
                if len(lista[0]) == 1:  # se for só um valor
                    return lista[0][0]  # retorna só o valor
                return lista[0]  # retorna a linha
            return lista
        else:
            return None

    def query(self, query, print_values=False):
        self.execute(query)
        retorno = self.make_readable(self.c.fetchall())

        if print_values:
            print(retorno)
        return retorno

    def execute(self, query):
        if self.debug:
            self.debug.write(query + '\n')

        try:
            self.c.execute(query)
        except sqlite3.Error as e:
            print(query + "\nError running query: ", e.args)
            self.conn.close()
            exit(999)

    def commit(self):
        self.conn.commit()

    # retorna o id de uma palavra / param: force_create - cria a palavra na base se não existir
    def get_word_id(self, word, force_create=False, print_values=False):
        wid = self.query('SELECT ID FROM WORDS WHERE WORD = \'' + word.value + '\';', print_values=print_values)
        if not wid and force_create:  # checa se a palavra existe e se deve ser criada
            if self.terminal: print(word.value)
            wid = self.insert_word_id(word)
        return wid

    # cria uma nova palavra na base
    def insert_word_id(self, word):
        self.execute('INSERT OR IGNORE INTO WORDS (WORD) VALUES(\'' + word.value + '\');')
        self.commit()
        return self.get_word_id(word)

    # insere uma palavra x probabilidade na base
    def insert_word_prob(self, word):
        wid = self.get_word_id(word, force_create=True)
        self.execute('INSERT INTO WORDS_PROB VALUES (' + str(wid) + ', ' + str(word.probability) + ');')
        self.commit()

    def get_phrase_count(self):
        return self.query('SELECT COUNT(*) FROM PHRASES;')

    # retorna o id de uma frase / param: force_create - cria a frase na base se não existir
    def get_phrase_id(self, phrase, force_create=False, print_values=False):
        query = 'SELECT ID FROM PHRASES WHERE '
        for i, word in enumerate(phrase.words):  # criando a query de busca
            if i: query += 'OR '
            wid = self.get_word_id(word)
            if not wid: return None
            query += '(WORD_ID = ' + str(wid) + ' AND WORD_ORDER = ' + str(i) + ') '
        query += 'GROUP BY ID HAVING COUNT(*) = ' + str(phrase.k) + ';'
        pid = self.query(query, print_values)

        if not pid and force_create:   # checa se a frase existe e se deve ser criada
            pid = self.insert_new_phrase(phrase)
        return pid

    # retorna a probabilidade de uma frase / param: default_return - valor que deve retornar caso a frase não exista
    def get_phrase_prob(self, phrase, default_return=0.5):
        pid = self.get_phrase_id(phrase)
        if not pid:
            return default_return
        query = 'SELECT AVG(PROBABILITY) FROM PHRASES_PROB WHERE PHRASE_ID = ' + str(pid) + ' GROUP BY PHRASE_ID;'
        return self.query(query)

    # cria uma nova frase na base
    def insert_new_phrase(self, phrase):
        pid = self.query('SELECT MAX(ID) + 1 FROM PHRASES;')
        if not pid: pid = 1
        for i, word in enumerate(phrase.words):
            wid = self.get_word_id(word, force_create=True)
            self.execute('INSERT INTO PHRASES VALUES (' + str(pid) + ', ' + str(wid) + ', ' + str(i) + ');')
        self.commit()
        return pid

    # insere uma frase x probabilidade na base
    def insert_phrase_prob(self, phrase):
        pid = self.get_phrase_id(phrase, force_create=True)
        self.execute('INSERT INTO PHRASES_PROB VALUES (' + str(pid) + ', ' +
                     str(phrase.probability) + ', ' +
                     str(phrase.alpha) + ');')
        self.commit()

    # insere um texto de forma safe
    def insert_text(self, text, prnt=False):
        self.terminal = prnt
        if self.terminal:
            print('---=== TEXTO ===---')
            text.print_text()
            print('--- Inserindo novas Palavras ---')
        for words in text.words:  # insere todas palavras x probabilidade do texto na base
            self.insert_word_prob(words)

        if self.terminal:
            print('--- FRASES ---')
        for phrase in text.phrases:  # insere todas as frases x probabilidade
            if self.terminal:
                phrase.print()
            self.insert_phrase_prob(phrase)

    def update_alpha(self, i, alpha):
        self.execute('UPDATE PHRASES_PROB SET ALPHA = ' + alpha + ' WHERE PHRASE_ID = ' + i + ';')
        self.commit()


    def update_firefly(self, firefly):
        for i, alpha in enumerate(firefly):
            self.update_alpha(i, alpha)
