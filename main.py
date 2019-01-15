from text import Text
import sqlite3

conn = None
c = None


def insert_new_lines(mylist):
    values = []
    global c, conn

    for i in mylist[0]:
        values.append((i, mylist[1]))

    print(values)

    c.executemany('INSERT INTO WORDS VALUES (?,?)', values)
    conn.commit()


def bd():
    global c, conn
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='WORDS';")
    if not c.fetchall():
        c.execute('CREATE TABLE WORDS (WORD TEXT, PROBABILITY REAL);')

    conn.commit()


def main():
    texts = []
    raw_texts = [
        [str.split('Bill and Hillary Clinton attend Donald Trump last wedding', ' '), 1],
        [str.split('Donald Trump have say he loves war including with nukes', ' '), 0.8],
        [str.split('Delegates can not legally change Republican National Convention rules to prevent '
                   'Donald Trump nominate', ' '), 0.6],
        [str.split('Donald Trump say women And you can tell them to go fuck themselves', ' '), 0.0]
    ]
    for r in raw_texts:
        insert_new_lines(r)

        t = Text(r[0], r[1])
        t.build_phrases(3)
        # t.print_text()
        texts.append(t)

    global conn
    conn.close()

bd()
main()
