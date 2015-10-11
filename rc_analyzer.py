import analyze_utils
import re
import os
import glob
import csv
import json

DATA_DIR = os.getenv('HOME') + "/Documents/RC/rc_static/"
CORPORA_DIR = DATA_DIR + "corpora/"
PROCESSED_DIR = DATA_DIR + "processed/"
PROCCESSED_BY_DAY_DIR = PROCESSED_DIR + "by_day/"


""" 
Accepts a list of strings containing any combination of ['1', '2', '3'], indicating gram number n.
Calls process_grams from analyze_utils on all n-grams in the CORPORA dirctory
"""

def process_all_grams(which_grams):
    "Beginning to process every gram file..."
    try:
        os.makedirs(PROCCESSED_BY_DAY_DIR)
    except OSError:
        if not os.path.isdir(PROCCESSED_BY_DAY_DIR):
            raise
    for gram_num in which_grams:
        days = glob.glob(CORPORA_DIR + '*/')
        for day in days:
            date = day[len(CORPORA_DIR):]
            print('Processing ' + date + 'gram' + gram_num)
            try:
                os.makedirs(PROCCESSED_BY_DAY_DIR + date)
            except OSError:
                if not os.path.isdir(PROCCESSED_BY_DAY_DIR + date):
                    raise        
            gram_f = day + gram_num + 'gram.txt'    
            # for gram_f in glob.glob(day + gram_num + 'gram.txt'):
            analyze_utils.process_grams(gram_f, PROCCESSED_BY_DAY_DIR + date, gram_num)
    print("Done processing gram files")

# def remove_old():
#     files = glob.glob(CORPORA_DIR + '*/all*')
#     for f in files:    
#         print("removing " + f)
#         os.remove(f)

def create_gram_list(gram):
    print("Creating list of unique tokens...")
    all_grams = set()
    files = glob.glob(PROCCESSED_BY_DAY_DIR + '*/all' + gram + 'grams.csv')
    for f in files:
        with open(f, newline='') as csvfile:
            f_reader = csv.reader(csvfile)
            for line in f_reader:
                all_grams.add(line[3])
    all_grams = list(all_grams)
    all_grams_json = PROCESSED_DIR + "all_" + gram + "gram_list.json"
    with open(all_grams_json, 'w') as f:
        json.dump(all_grams,f)
    print("Finished list")



if __name__ == '__main__':
    which_grams=['1']
    process_all_grams(which_grams)
    create_gram_list('1')
    