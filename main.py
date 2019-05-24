from csv import excel
from os.path import isfile
from numpy.core.defchararray import isnumeric
from classes.Firefly import *
from classes.util import find_files, load_firefly, save_firefly

# path setup
experiment = '1'
phrase_size = '3'
experiment_path = 'experiments/' + experiment + '/' + phrase_size + '/'
db_filename = 'database' + '.sql'
training_filename = 'training_tab' + '.csv'
dbh_filename = 'dbh' + '.dbh'
firefly_filename = 'firefly' + '.ff'
validation_filename = 'validation_tab' + '.csv'

# variables
db = None
dbh = None
best_firefly = None

phrase_size = int(phrase_size)


def load_all():
    global db, dbh, best_firefly
    global db_filename, training_filename, dbh_filename, firefly_filename, validation_filename

    if not isfile(experiment_path + db_filename):
        print("DB not found: ", experiment_path + db_filename)
        db_filename = find_files(experiment_path, 'sql')
    db = DB(run_on_ram=db_filename)
    db.ram = False  # disable sql dump

    if not isfile(experiment_path + firefly_filename):
        print("Firefly not found: ", experiment_path + firefly_filename)
        if not isfile(experiment_path + dbh_filename):
            print("DBH not found: ", experiment_path + dbh_filename)
            if not isfile(experiment_path + training_filename):
                print("Training csv not found: ", experiment_path + training_filename)
                training_filename = find_files(experiment_path, 'csv')
            dbh = get_all_phrases_prob(experiment_path + training_filename, db, phrase_size)
            dbh.to_file(experiment_path, 'dbh.dbh')
        else:
            print("Loading DBH: ", experiment_path + dbh_filename)
            dbh = DbHandler()
            dbh.from_file(experiment_path, dbh_filename)

        [brightness, best_firefly] = firefly(
            dimension=5,
            number_fireflies=100,
            max_generation=100,
            processes=8,
            phrase_size=phrase_size,
            dbh=dbh
        )
        save_firefly(best_firefly, experiment_path + 'firefly.ff')
    else:
        print("Loading Firefly: ", experiment_path + firefly_filename)
        best_firefly = load_firefly(experiment_path + firefly_filename)


def test(upper_bound=0.75, lower_bound=0.25):
    output = open(experiment_path + '/resultados.csv', 'w')
    output.write('text;ground_truth;found;comparison\n')
    row_number = 0

    truenews_count = 0
    fakenews_count = 0

    true_positive = 0
    true_negative = 0

    with open(experiment_path + 'validation_tab.csv', newline='', encoding='utf-8-sig') as csvfile:  # lendo o csv
        reader = csv.reader(csvfile, delimiter=";", quoting=csv.QUOTE_NONE)
        for row in reader:
            ground_truth = float(row[0])
            text = row[1]
            line = text + ';' + str(ground_truth) + ';'
            [text_prob, found, out_of] = calc_text_prob(row[1], db, best_firefly, phrase_size)

            correct_classification = False

            if ground_truth >= upper_bound:
                if text_prob >= upper_bound:
                    true_positive += 1
                    correct_classification = True
                truenews_count += 1

            if ground_truth >= lower_bound:
                if text_prob >= lower_bound:
                    true_negative += 1
                    correct_classification = True
                fakenews_count += 1

            if lower_bound > ground_truth < upper_bound:
                if lower_bound > text_prob < upper_bound:
                    correct_classification = True

            line += str(text_prob) + ';' + str(correct_classification)
            output.write(line + '\n')
            row_number += 1

    print(row_number, " lines tested")
    output.close()


load_all()
test()

