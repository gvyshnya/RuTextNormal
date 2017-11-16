# Competion: https://www.kaggle.com/c/text-normalization-challenge-russian-language/
# Description: tweaked and enhanced submission script with external reference data used
# Inspired by:
# - https://www.kaggle.com/arccosmos/ru-baseline-lb-0-9799-from-en-thread
# - https://www.kaggle.com/alphasis/bigdata-trick-or-treat-lb-0-9954
#
# Text normalization data come from https://github.com/rwsproat/text-normalization-data

import datetime as dt
import os
import operator
from num2words import num2words # not required for RU version
import gc


INPUT_PATH = r'input/'
DATA_INPUT_PATH = r'input/ru_with_types'
SUBM_PATH = "output/"

TRANS = "_trans"

SUB = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")
SUP = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")
OTH = str.maketrans("፬", "4")

def map_ukrainian_char(one_ua_char):
    intab_special_ua = "іїєґ"
    outtab_special_ua = "ииег"

    transtab_special_ua = str.maketrans(intab_special_ua, outtab_special_ua)
    trans_char = one_ua_char.translate(transtab_special_ua)

    return trans_char

def transliterate_latin_char(one_char):
    str_res = ""
    intab_regular_latin_consonants = "zvbnmsdfghklwrtp"
    outtab_regular_latin_consonants = "звбнмсдфгхклуртп"

    intab_latin_sonants = "aoeui"
    outtab_latin_sonants = "аоеуи"

    trantab_latin_consonants = str.maketrans(intab_regular_latin_consonants, outtab_regular_latin_consonants)
    trantab_latin_sonants = str.maketrans(intab_latin_sonants, outtab_latin_sonants)

    trans_char = one_char.translate(trantab_latin_consonants)
    trans_char = trans_char.translate(trantab_latin_sonants)

    # transliterate 'irregular' latin chars
    if trans_char == "x":
        str_res = "к"+ TRANS + " " + "с"+ TRANS
    else:
        if trans_char == "j":
            str_res = "д" + TRANS + " " + "ж" + TRANS
        else:
            if trans_char == "q":
                str_res = "к" + TRANS + " " + "у" + TRANS
            else:
                if trans_char == "c":
                    str_res = "с" + TRANS # TODO: review?
                else:
                    # put transliteration for already transliterated chars
                    str_res = trans_char + TRANS
    return str_res

def containsAny(str, set):
    for c in set:
        if c in str: return 1
    return 0

def has_latin_chars(word):
    set = "qazwsxedcrfvtgbyhnujmikolp"
    if containsAny(word, set):
        return 1
    return 0

def has_ukrainian_chars(word):
    set = "іїєґ"
    if containsAny(word, set):
        return 1
    return 0

def transliterate_ukrainian_lexeme(word):
    """ @param word - a single word string without spaces"""
    str_res = ""
    if has_ukrainian_chars(word):
        # split str_res into chars
        char_list = list(str_res)
        for i in range(len(char_list)):
            c = char_list[i]
            if has_ukrainian_chars(c):
                c = map_ukrainian_char(c)
            str_res = str_res + c
    else:
        str_res = word
    return str_res

def transliterate_latin_in_mixed_lexeme(word):
    """ @param word - a single word string without spaces"""
    str_res = ""
    if has_latin_chars(str_res):
        # split str_res into chars
        char_list = list(str_res)
        for i in range(len(char_list)):
            c = char_list[i]
            if has_latin_chars(c):
                translit = transliterate_latin_char(c)
                str_res = str_res  + translit + " "
            else:
                # cyrillic char  - simply add it to the output as is
                str_res = str_res + c
    else:
        str_res = word
    return str_res

def solve():
    print('Train start...')

    file = "ru_train.csv"
    train = open(os.path.join(INPUT_PATH, "ru_train.csv"), encoding='UTF8')
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
    print(file + ':\tTotal: {} Have diff value: {}'.format(total, not_same))

    files = os.listdir(DATA_INPUT_PATH)
    for file in files:
        train = open(os.path.join(DATA_INPUT_PATH, file), encoding='UTF8')
        while 1:
            line = train.readline().strip()
            if line == '':
                break
            total += 1
            pos = line.find('\t')
            text = line[pos + 1:]
            if text[:3] == '':
                continue
            arr = text.split('\t')
            if arr[0] == '<eos>':
                continue
            if arr[1] != '<self>':
                not_same += 1

            if arr[1] == '<self>' or arr[1] == 'sil':
                arr[1] = arr[0]

            if arr[0] not in res:
                res[arr[0]] = dict()
                res[arr[0]][arr[1]] = 1
            else:
                if arr[1] in res[arr[0]]:
                    res[arr[0]][arr[1]] += 1
                else:
                    res[arr[0]][arr[1]] = 1
        train.close()
        print(file + ':\tTotal: {} Have diff value: {}'.format(total, not_same))
        gc.collect()

    sdict = {}
    sdict['км²'] = 'квадратных километров'
    sdict['км2'] = 'квадратных километров'
    sdict['km²'] = 'квадратных километров'
    sdict['км'] = 'километров'
    sdict['km'] = 'километров'
    sdict['кг'] = 'килограмм'
    sdict['kg'] = 'килограмм'
    sdict['m²'] = 'квадратных метров'
    sdict['м²'] = 'квадратных метров'

    total = 0
    changes = 0
    out = open(os.path.join(SUBM_PATH, 'tweaked_ext_ru.csv'), "w", encoding='UTF8')
    out.write('"id","after"\n')
    test = open(os.path.join(INPUT_PATH, "ru_test.csv"), encoding='UTF8')
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
            if len(line) > 1:
                val = line.split(',')
                if len(val) == 2 and val[0].isdigit and val[1].isdigit:
                    line = ''.join(val)

            if line.isdigit():
                srtd = line.translate(SUB)
                srtd = srtd.translate(SUP)
                srtd = srtd.translate(OTH)
                out.write('"' + num2words(float(srtd)) + '"')
                changes += 1
            elif len(line.split(' ')) > 1:
                val = line.split(' ')
                for i, v in enumerate(val):
                    if v.isdigit():
                        srtd = v.translate(SUB)
                        srtd = srtd.translate(SUP)
                        srtd = srtd.translate(OTH)
                        val[i] = num2words(float(srtd))
                    elif v in sdict:
                        val[i] = sdict[v]
                    else:
                        # TODO: handle roman numbers first
                        if has_ukrainian_chars(v):
                            val[i] = transliterate_ukrainian_lexeme(v)
                            if has_latin_chars(val[i]):
                                val[i] = transliterate_latin_in_mixed_lexeme(val[i])
                        else:
                            if has_latin_chars(v):
                                val[i] = transliterate_latin_in_mixed_lexeme(v)

                out.write('"' + ' '.join(val) + '"')
                changes += 1
            else:
                # a single lexeme
                # TODO: handle roman numbers first
                if has_ukrainian_chars(line):
                    line = transliterate_ukrainian_lexeme(line)
                    if has_latin_chars(line):
                        line = transliterate_latin_in_mixed_lexeme(line)
                else:
                    if has_latin_chars(line):
                        line = transliterate_latin_in_mixed_lexeme(line)
                out.write('"' + line + '"')

        out.write('\n')
        total += 1

    print('Total: {} Changed: {}'.format(total, changes))
    test.close()
    out.close()

if __name__ == '__main__':
    start_time = dt.datetime.now()
    print("Started tweaked_ext_ru.py at ", start_time)

    solve()

    # Finalize ...
    end_time = dt.datetime.now()
    elapsed_time = end_time - start_time
    print("Finished tweaked_ext_ru.py at ", end_time)
    print("Elapsed time: ", elapsed_time)