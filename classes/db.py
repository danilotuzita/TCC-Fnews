import sqlite3


class DB:
    conn = None
    c = None
    # TESTE = "CREATE TABLE IF NOT EXISTS WORDS ("
    #     "    ID INTEGER PRIMARY KEY AUTOINCREMENT, "
    #     "    WORD TEXT NOT NULL UNIQUE,"
    #     "    PROBABILITY NUMBER DEFAULT 1,"
    #     "    COUNT INTEGER DEFAULT 1,"
    #     "        CHECK (PROBABILITY BETWEEN 0 AND 1)"
    #     ");"

    tables = [
        "CREATE TABLE IF NOT EXISTS WORDS ("         # 0, 'TRUMP'
        "    ID INTEGER PRIMARY KEY AUTOINCREMENT, "
        "    WORD TEXT NOT NULL UNIQUE"
        ");",

        "CREATE TABLE IF NOT EXISTS WORDS_PROB ("
        "    WORD_ID INTEGER NOT NULL,"
        "    PROBABILITY NUMBER DEFAULT 1,"
        "        CHECK (PROBABILITY BETWEEN 0 AND 1)"
        ");",


        # TODO: ARRUMAR AS TABELAS DAS FRASES. NÃO FUNCIONA SE A FRASE SE REPETIR, DESCOBRIR COMO CALCULAR A MÉDIA
        "CREATE TABLE IF NOT EXISTS PHRASES ("
        "    PHRASE INTEGER,"
        "    WORD_ID INTEGER NOT NULL,"
        "    WORD_ORDER INTEGER DEFAULT 0,"
        "        FOREIGN KEY (WORD_ID) REFERENCES WORDS(ID)"
        ");",

        "CREATE TABLE IF NOT EXISTS PHRASES_PROB ("
        "    PHRASE INTEGER NOT NULL,"
        "    PROBABILITY NUMBER DEFAULT 1,"
        "    COUNT INTEGER DEFAULT 1,"
        "    ALPHA NUUMBER NOT NULL,"
        "        FOREIGN KEY (PHRASE) REFERENCES FHRASES(PHRASE),"
        "        CHECK (PROBABILITY BETWEEN 0 AND 1)"
        ");"
    ]

    def __init__(self, path='database/database.db'):
        self.conn = sqlite3.connect(path)
        self.c = self.conn.cursor()
        self.check_tables()

    def __del__(self):
        self.conn.close()

    def check_tables(self):
        for query in self.tables:
            self.execute(query)
        self.commit()
        return None

    def execute_many(self, query, values=(), commit=False):
        self.c.executemany(query, values)
        if commit:
            self.commit()

    def query(self, query, print_values=False):
        self.execute(query)
        retorno = self.c.fetchall()
        if print_values:
            for r in retorno:
                print(r)
        return retorno

    def execute(self, query):
        try:
            self.c.execute(query)
        except sqlite3.Error as e:
            print(query + "\nError running query: ", e.args)

    def commit(self):
        self.conn.commit()
