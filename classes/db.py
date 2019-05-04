# encoding: utf-8
import sqlite3
import os
import datetime
from classes.phrase import Phrase


class DB:
    path = None
    filename = None

    debug = False
    debug_filename = None
    terminal = None
    ram = False

    conn = None
    c = None

    relevancy_min_count = 1

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

        "CREATE UNIQUE INDEX IF NOT EXISTS index_words ON words(word);"
        "CREATE INDEX IF NOT EXISTS index_phrases ON phrases(word_id, word_order);"
    ]

    # connection = sqlite3.connect("file::memory:?cache=shared")
    def __init__(self, path='database/', filename='database', debug=False, debug_filename='database_debug',
                 connection=None, run_on_ram=False):
        print("build db")
        self.path = path
        self.filename = filename
        if connection:
            self.conn = connection
        else:
            if not run_on_ram:
                self.conn = sqlite3.connect(path + filename + '.db')
            else:
                self.conn = sqlite3.connect(":memory:")  # cria banco na memoria
                self.ram = True
                if os.path.isfile(run_on_ram):
                    self.run_sql_file(run_on_ram, self.conn)

        self.c = self.conn.cursor()
        self.check_tables()

        self.debug = debug
        if debug:
            self.open_debug(debug_filename)

    def __del__(self):
        if self.ram:
            with open(self.path + self.filename + '.sql', 'w') as f:
                for line in self.conn.iterdump():
                    f.write('%s\n' % (line.encode('ascii', 'ignore')).decode('utf-8'))
            self.conn.close()
            # conn = sqlite3.connect(self.path + self.filename + '.db')
            # self.run_sql_file('dump.sql', conn)

        self.conn.close()
        if self.debug:
            self.debug.close()

    @staticmethod
    def run_sql_file(filename, conn):
        file = open(filename, 'r')
        sql = file.read()  # watch out for built-in `str`
        cur = conn.cursor()
        cur.executescript(sql)
        conn.commit()

    def open_debug(self, debug_filename):
        self.debug = open(self.path + debug_filename + '.log', 'w+')

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
    @staticmethod
    def make_readable(cursor):
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

        if not pid and force_create:  # checa se a frase existe e se deve ser criada
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

    def get_relevant_phrases(self, floor, roof, count=relevancy_min_count):
        """"
        retorna ids das frases relevantes
        :param floor: probabilidade minima
        :param roof: probablidade maxima
        :param count: numero minimo de vezes que a frase foi citada
        """
        return self.query(
            'SELECT PHRASE_ID FROM PHRASES_PROB GROUP BY PHRASE_ID '
            'HAVING COUNT(PHRASE_ID) >= ' + str(count) +
            ' AND AVG(PROBABILITY) BETWEEN ' + str(floor) + ' AND ' + str(roof) + ';'
        )

    def is_relevant_phrase(self, phrase, floor, roof, count=relevancy_min_count):
        """"
        :param phrase: id da frase<int> ou Phrase
        :param floor: probabilidade minima
        :param roof: probablidade maxima
        :param count: numero minimo de vezes que a frase foi citada
        """
        if type(phrase) is Phrase:
            phrase = self.get_phrase_id(phrase)

        if type(phrase) is int:
            return self.query(
                'SELECT PHRASE_ID FROM PHRASES_PROB '
                'WHERE PHRASE_ID = ' + str(phrase) +
                ' GROUP BY PHRASE_ID HAVING COUNT(PHRASE_ID) >= ' + str(count) +
                ' AND AVG(PROBABILITY) BETWEEN ' + str(roof) + ' AND ' + str(floor) + ';'
            )
        return -1

    def get_all_phrase_prob(self, phrase):
        """"
        retorna a quantidade de vezes que a frase phrase teve certa probabilidade
        SELECT PHRASE_ID, PROBABILITY, COUNT(*) FROM PHRASES_PROB WHERE PHRASE_ID = phrase
        GROUP BY PHRASE_ID, PROBABILITY;
        :param phrase: id da frase<int> ou Phrase
        """
        if type(phrase) is Phrase:
            phrase = self.get_phrase_id(phrase)

        return self.query(
            'SELECT PHRASE_ID, PROBABILITY, COUNT(*) FROM PHRASES_PROB '
            'WHERE PHRASE_ID = ' + str(phrase) + ' '
                                                 'GROUP BY PHRASE_ID, PROBABILITY;'
        )

    def get_phrase_prob_count(self, phrase, prob):
        """"
        retorna a quantidade de vezes que a frase phrase teve probabilidade prob
        SELECT COUNT(*) FROM PHRASES_PROB WHERE PHRASE_ID = phrase AND PROBABILITY = prob;
        :param phrase: id da frase<int> ou Phrase
        :param prob: probabilidade
        """
        if type(phrase) is Phrase:
            phrase = self.get_phrase_id(phrase)

        return self.query(
            'SELECT COUNT(*) FROM PHRASES_PROB '
            'WHERE PHRASE_ID = ' + str(phrase) + ' '
                                                 'AND PROBABILITY = ' + str(prob) + ';'
        )

    def get_phrases_with_prob(self, prob):
        """"
        retorna as frases e sua quantidade de vezes que teve probabilidade prob
        SELECT PHRASE_ID, COUNT(*) FROM PHRASES_PROB WHERE PROBABILITY = prob
        GROUP BY PHRASE_ID;
        :param phrase: id da frase<int> ou Phrase
        :param prob: probabilidade
        """
        return self.query(
            'SELECT PHRASE_ID, COUNT(*) FROM PHRASES_PROB '
            'WHERE PROBABILITY = ' + str(prob) + ' '
                                                 'GROUP BY PHRASE_ID;'
        )
