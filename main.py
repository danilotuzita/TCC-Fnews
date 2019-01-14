import word, text, phrase


def main():
    w = str.split('Bill and Hillary Clinton attend Donald Trump last wedding', ' ')
    t = text.Text()
    t.make_text(w)
    t.build_phrases(2)
    t.print_phrases()


main()
