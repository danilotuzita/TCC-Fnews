from classes.text import Text
from classes.db import DB
import csv


def main2():
    texts = []
    raw_texts = [
        [str.split('Bill and Hillary Clinton attend Donald Trump last wedding', ' '), 1],
        [str.split('Donald Trump have say he loves war including with nukes', ' '), 0.8],
        [str.split('Delegates can not legally change Republican National Convention rules to prevent '
                   'Donald Trump nominate', ' '), 0.6],
        [str.split('Donald Trump say women And you can tell them to go fuck themselves', ' '), 0.0]
    ]
    for r in raw_texts:
        t = Text(r[0], r[1])
        t.build_phrases(3)
        t.print_phrases()
        texts.append(t)


def main():
    t = None
    with open('database/treino.csv', newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.reader(csvfile, delimiter=";", quoting=csv.QUOTE_NONE)
        for row in reader:
            t = Text(str.split(str.upper(row[1])), row[0])
            t.build_phrases(3)
    db = DB()
    db.insert_text(t)


main()


# a = db.query(select_media, True)
# input()

