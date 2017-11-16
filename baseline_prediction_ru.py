# -*- coding: utf-8 -*-
# Competion: https://www.kaggle.com/c/text-normalization-challenge-russian-language/
# Description: baseline submission script
# Inspired by: 'ZFTurbo: https://kaggle.com/zfturbo'


import datetime as dt
import operator

INPUT_PATH = "input/"
SUBM_PATH = "output/"


def solve():
    print('Train start...')
    train = open(INPUT_PATH + "ru_train.csv", encoding='UTF8')
    line = train.readline()
    res = dict()
    total = 0
    not_same = 0
    while 1:
        line = train.readline().strip()
        if line == '':
            break
        total += 1
        pos = line.find('","')
        text = line[pos + 2:]
        if text[:3] == '","':
            continue
        text = text[1:-1]
        arr = text.split('","')
        if arr[0] != arr[1]:
            not_same += 1
        if arr[0] not in res:
            res[arr[0]] = dict()
            res[arr[0]][arr[1]] = 1
        else:
            if arr[1] in res[arr[0]]:
                res[arr[0]][arr[1]] += 1
            else:
                res[arr[0]][arr[1]] = 1

    train.close()
    print('Total: {} Have diff value: {}'.format(total, not_same))

    total = 0
    changes = 0
    out = open(SUBM_PATH + 'baseline_ru.csv', "w", encoding='UTF8')
    out.write('"id","after"\n')
    test = open(INPUT_PATH + "ru_test.csv", encoding='UTF8')
    line = test.readline().strip()
    while 1:
        line = test.readline().strip()
        if line == '':
            break

        pos = line.find(',')
        i1 = line[:pos]
        line = line[pos + 1:]

        pos = line.find(',')
        i2 = line[:pos]
        line = line[pos + 1:]

        line = line[1:-1]
        out.write('"' + i1 + '_' + i2 + '",')
        if line in res:
            srtd = sorted(res[line].items(), key=operator.itemgetter(1), reverse=True)
            out.write('"' + srtd[0][0] + '"')
            changes += 1
        else:
            out.write('"' + line + '"')

        out.write('\n')
        total += 1

    print('Total: {} Changed: {}'.format(total, changes))
    test.close()
    out.close()


if __name__ == '__main__':
    start_time = dt.datetime.now()
    print("Started baseline_prediction_ru.py at ", start_time)

    solve()

    # Finalize ...
    end_time = dt.datetime.now()
    elapsed_time = end_time - start_time
    print("Finished baseline_prediction_ru.py at ", end_time)
    print("Elapsed time: ", elapsed_time)