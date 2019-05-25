from os.path import isfile, isdir
from classes.Firefly import *
from classes.util import find_files, load_firefly, save_firefly, create_database

# path setup
_slice = 0
p_delta = 0
experiment = '1'
phrase_size = 2
db_filename = 'database' + '.sql'
csv_path = ''
experiment_path = ''
training_filename = 'training_tab' + '.csv'
dbh_filename = 'training' + '.dbh'
firefly_filename = 'firefly' + '.ff'
validation_filename = 'validation_tab' + '.csv'

# variables
db = None
dbh = None
best_firefly = None


def load_all():
    global db, dbh, best_firefly, phrase_size
    global db_filename, csv_path, experiment_path, training_filename, dbh_filename, firefly_filename, validation_filename

    experiment_path = 'experiments/' + experiment + '/' + str(_slice) + '/' + str(phrase_size) + '/' + str(p_delta) + '/'
    if not os.path.exists(experiment_path):
        os.makedirs(experiment_path)

    csv_path = 'experiments/' + experiment + '/' + str(_slice) + '/'
    if not isfile(experiment_path + db_filename):
        print("DB not found: ", experiment_path + db_filename)
        db = create_database(csv_path + training_filename, experiment_path + db_filename, phrase_size)
        del db
    db = DB(run_on_ram=experiment_path + db_filename)
    db.ram = False  # disable sql dump

    if not isfile(experiment_path + firefly_filename):
        print("Firefly not found: ", experiment_path + firefly_filename)
        if not isfile(csv_path + dbh_filename):
            print("DBH not found: ", csv_path + dbh_filename)
            if not isfile(csv_path + training_filename):
                print("Training csv not found: ", csv_path + training_filename)
                training_filename = find_files(csv_path, 'csv')
            print("Training csv: ", csv_path + training_filename)
            dbh = get_all_phrases_prob(csv_path + training_filename, db, phrase_size)
            dbh.to_file(csv_path + str(phrase_size) + '/', dbh_filename)
        else:
            print("Loading DBH: ", csv_path + str(phrase_size) + '/' + dbh_filename)
            dbh = DbHandler()
            dbh.from_file(csv_path + str(phrase_size) + '/', dbh_filename)

        [brightness, best_firefly] = firefly(
            dimension=5,
            number_fireflies=100,
            max_generation=10,
            processes=16,
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
    global best_firefly
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

        output.write("General assertivity: " + str(
            (true_positive + true_negative) * 100 /
            (truenews_count + fakenews_count)
        ) + '\n')

        output.write(str(row_number) + " lines tested")
        print("============ RESULTS ============")
        print("Experiment : ", experiment)
        print("Slice      : ", _slice)
        print("Phrase Size: ", phrase_size)
        print("Plus Delta : ", p_delta)
        print("Upper Bound: ", upper_bound)
        print("Lower Bound: ", lower_bound)
        print("True Positive: " + str(truenews_count) + ", Found: " + str(true_positive) +
                     " (" + str(true_positive * 100 / truenews_count) + "%)")

        print("True Negative: " + str(fakenews_count) + ", Found: " + str(true_negative) +
                     " (" + str(true_negative * 100 / fakenews_count) + "%)")
        print("Assertivity  : ",
            (true_positive + true_negative) * 100 /
            (truenews_count + fakenews_count)
        )
        print(row_number, " lines tested")
    output.close()


def ex_1():
    global phrase_size, _slice, p_delta
    for phrase_s in [3]:
        phrase_size = phrase_s
        for s in range(2, 6):
            _slice = s
            for p_d in [0, 1, 5]:
                if s == 2 and p_d in (0, 1):
                    continue
                p_delta = p_d
                load_all()
                test()
                if not isfile(csv_path + str(phrase_size) + '/' + "validation.dbh"):
                    _dbh = get_all_phrases_prob(csv_path + validation_filename, db, phrase_size)
                    _dbh.to_file(csv_path + str(phrase_size) + '/', "validation.dbh")


ex_1()

# from classes.validation import validation_files_creation

# for i in range(1, 6):
#     validation_files_creation(5, i, 'experiments/cross validation files/10700/LIAR_1_10700.csv',
#                               'experiments/cross validation files/10700/' + str(i))



"""
ff = np.array([0.28126, 0.26142, 0.0035938, 0.39035, 0.063372]) + 1
dbh = DbHandler()
dbh.from_file(experiment_path, 'dbhExperimento_FULL.txt')

quinto = len(dbh.texts) / 5

truenews_count = 0
fakenews_count = 0

true_positive = 0
true_negative = 0

upper_bound = 0.75
lower_bound = 0.25

for i, text in enumerate(dbh.texts):
    probs = []
    for phrase in text.phrases:
        probs.append(phrase)
    [aaa, bbb] = get_used_clusters(probs, 5)
    ground_truth = text.real_prob
    text_prob = calc_prob(aaa, ff)
    if i > quinto:
        break

    if ground_truth >= upper_bound:
        if text_prob >= upper_bound:
            true_positive += 1
            correct_classification = True
        truenews_count += 1

    if ground_truth <= lower_bound:
        if text_prob <= lower_bound:
            true_negative += 1
            correct_classification = True
        fakenews_count += 1


print("True Positive: " + str(truenews_count) + ", Found: " + str(true_positive) +
             " (" + str(true_positive * 100 / truenews_count) + "%)\n")

print("True Negative: " + str(fakenews_count) + ", Found: " + str(true_negative) +
             " (" + str(true_negative * 100 / fakenews_count) + "%)\n")

print("General Assertivity: " + str(
    (true_positive + true_negative) * 100 /
    (truenews_count + fakenews_count)
) + '\n')
"""