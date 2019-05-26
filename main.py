import pandas
from os.path import isfile, isdir
from classes.Firefly import *
from classes.util import *

# params setup
_slice = 0
p_delta = 0
bound = 0.25
experiment = '0'
phrase_size = 2

# path setup
csv_path = ''
dbh_path = ''
experiment_path = ''

# filenames setup
training_filename = 'training_tab' + '.csv'
validation_filename = 'validation_tab' + '.csv'
db_filename = 'database' + '.sql'
dbh_filename = 'training' + '.dbh'
firefly_filename = 'firefly' + '.ff'

# files ref
result_file = None
result_file_row = 0

# variables
db = None
dbh = None
best_firefly = None


def load_all():
    global db, dbh, best_firefly, phrase_size
    global db_filename, training_filename, dbh_filename, firefly_filename, validation_filename
    global dbh_path, csv_path, experiment_path

    experiment_path = 'experiments/' + experiment + '/' + str(_slice) + '/' + str(phrase_size) + '/' + str(p_delta) + '/'
    if not os.path.exists(experiment_path):
        os.makedirs(experiment_path)

    csv_path = 'experiments/' + experiment + '/' + str(_slice) + '/'
    dbh_path = csv_path + str(phrase_size) + '/'
    if not isfile(csv_path + training_filename):
        print("Training csv not found: ", csv_path + training_filename)
        training_filename = find_files(csv_path, 'csv')
    print("Training csv: ", csv_path + training_filename)

    if not isfile(dbh_path + db_filename):
        print("DB not found: ", dbh_path + db_filename)
        db = create_database_from_csv(csv_path + training_filename, dbh_path + db_filename, phrase_size)
        del db
    print("Loading DB: ", dbh_path + db_filename)
    db = DB(run_on_ram=dbh_path + db_filename)
    db.ram = False  # disable sql dump

    if not isfile(experiment_path + firefly_filename):
        print("Firefly not found: ", experiment_path + firefly_filename)
        if not isfile(dbh_path + dbh_filename):
            print("DBH not found: ", dbh_path + dbh_filename)
            dbh = get_all_phrases_prob(csv_path + training_filename, db, phrase_size)
            dbh.to_file(dbh_path, dbh_filename)
        else:
            print("Loading DBH: ", dbh_path + dbh_filename)
            dbh = DbHandler()
            dbh.from_file(dbh_path, dbh_filename)

        print("Starting Firefly training")
        [brightness, best_firefly] = firefly(
            dimension=5,
            number_fireflies=100,
            max_generation=10,
            processes=0,
            phrase_size=phrase_size,
            dbh=dbh,
            plot=experiment_path,
            plus_delta=p_delta
        )
        save_firefly(best_firefly, experiment_path + 'firefly.ff')
    else:
        print("Loading Firefly: ", experiment_path + firefly_filename)
        best_firefly = load_firefly(experiment_path + firefly_filename)


def test(ff=0, upper_bound=0.75, lower_bound=0.25):
    global best_firefly, result_file
    if ff:
        best_firefly = ff

    print("Start testing")
    output = open(experiment_path + 'resultados.csv', 'w')
    output.write('text;ground_truth;found;phrases_found;out_of\n')
    row_number = 0

    truenews_count = 0
    fakenews_count = 0

    true_positive = 0
    true_negative = 0

    with open(csv_path + validation_filename, newline='', encoding='utf-8-sig') as csvfile:  # lendo o csv
        reader = csv.reader(csvfile, delimiter=";", quoting=csv.QUOTE_NONE)
        for i, row in enumerate(reader):
            if not divmod(i, 10)[1]:
                print(i)

            ground_truth = float(row[0])
            text = row[1]
            line = text + ';' + str(ground_truth) + ';'
            [text_prob, found, out_of] = calc_text_prob(row[1], db, best_firefly, phrase_size)

            if ground_truth >= upper_bound:
                if text_prob >= upper_bound:
                    true_positive += 1
                truenews_count += 1

            if ground_truth <= lower_bound:
                if text_prob <= lower_bound:
                    true_negative += 1
                fakenews_count += 1

            line += str(text_prob) + ';' + str(found) + ';' + str(out_of)
            output.write(line + '\n')
            row_number += 1
        output.write("True Positive: " + str(truenews_count) + ", Found: " + str(true_positive) +
                     " (" + str(true_positive * 100 / truenews_count) + "%)\n")

        output.write("True Negative: " + str(fakenews_count) + ", Found: " + str(true_negative) +
                     " (" + str(true_negative * 100 / fakenews_count) + "%)\n")

        assertivity = (true_positive + true_negative) * 100 / (truenews_count + fakenews_count)
        output.write("General assertivity: " + str(assertivity) + '\n')

        output.write(str(row_number) + " lines tested")
        print("============ RESULTS ============")
        print("Experiment : ", experiment)
        print("Slice      : ", _slice)
        print("Phrase Size: ", phrase_size)
        print("Plus Delta : ", p_delta)
        print("Upper Bound: ", upper_bound)
        print("Lower Bound: ", lower_bound)
        print(
            "True Positive: " + str(truenews_count) + ", Found: " + str(true_positive) +
            " (" + str(true_positive * 100 / truenews_count) + " %)"
        )
        print(
            "True Negative: " + str(fakenews_count) + ", Found: " + str(true_negative) +
            " (" + str(true_negative * 100 / fakenews_count) + " %)"
        )
        print("Assertivity  : ", assertivity)
        print(row_number, " lines tested")
        result_file.at[result_file_row, 'True News'] = truenews_count
        result_file.at[result_file_row, 'Fake News'] = fakenews_count
        result_file.at[result_file_row, 'True Positive'] = true_positive
        result_file.at[result_file_row, 'True Negative'] = true_negative
        result_file.at[result_file_row, 'Assertivity'] = assertivity
        result_file.at[result_file_row, 'Total Text'] = row_number
    output.close()


def ex_1():
    global phrase_size, _slice, p_delta, result_file, result_file_row, experiment
    experiment = '1'
    result_filename = 'experiment_1.csv'
    result_file = pandas.read_csv('experiments/' + experiment + '/' + result_filename)
    for i, row in result_file.iterrows():
        if pandas.isna(row['True News']):
            result_file_row = i
            phrase_size = int(row['Words'])
            _slice = int(row['Slice'])
            p_delta = int(row['Plus Delta'])
            print(
                "Slice      : ", _slice, '\n'
                "Phrase Size: ", phrase_size, '\n'
                "Plus Delta : ", p_delta
            )
            load_all()
            test()
            result_file.to_csv('experiments/' + experiment + '/' + result_filename)


def ex_2():
    global phrase_size, _slice, p_delta, result_file, result_file_row, bound, experiment
    experiment = '2'
    result_filename = 'experiment.csv'
    result_file = pandas.read_csv('experiments/' + experiment + '/' + result_filename)
    for i, row in result_file.iterrows():
        if pandas.isna(row['True News']):
            result_file_row = i
            phrase_size = int(row['Words'])
            _slice = int(row['Slice'])
            p_delta = int(row['Plus Delta'])
            bound = float(row['Bounds'])
            print(
                "Slice      : ", _slice, '\n'
                "Phrase Size: ", phrase_size, '\n'
                "Plus Delta : ", p_delta, '\n'
                "Bounds     : ", bound
            )
            load_all()
            test(
                upper_bound=0.5 + bound,
                lower_bound=0.5 - bound
            )
        result_file.to_csv('experiments/' + experiment + '/' + result_filename)


ex_1()
