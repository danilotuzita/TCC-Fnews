from classes.text import Text
from classes.db import DB

select_media = "SELECT WORD, AVG(PROBABILITY), COUNT(PROBABILITY) FROM WORDS GROUP BY WORD ORDER BY 2, 3;"
insert_word = "INSERT INTO WORDS VALUES (?,?);"


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
        t = Text(r[0], r[1])
        t.build_phrases(3)
        t.print_phrases()
        texts.append(t)


# main()

db = DB()
# a = db.query(select_media, True)
# input()

