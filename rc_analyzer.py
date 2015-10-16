import analyze_utils
import re
import os
import glob
import csv
import json
import ast

DATA_DIR = os.getenv('HOME') + "/Documents/RC/rc_static/"
CORPORA_DIR = DATA_DIR + "corpora/"
PROCESSED_DIR = DATA_DIR + "processed/"
PROCESSED_BY_DAY_DIR = PROCESSED_DIR + "by_day/"
PROCESSED_BY_GRAM_DIR = PROCESSED_DIR + "tokens/"


""" 
Accepts a list of strings containing any combination of ['1', '2', '3'], indicating gram number n.
Calls process_grams from analyze_utils on all n-grams in the CORPORA dirctory
"""

def process_all_grams(which_grams):
    "Beginning to process every gram file..."
    try:
        os.makedirs(PROCESSED_BY_DAY_DIR)
    except OSError:
        if not os.path.isdir(PROCESSED_BY_DAY_DIR):
            raise
    for gram_num in which_grams:
        days = glob.glob(CORPORA_DIR + '*/')
        for day in days:
            date = day[len(CORPORA_DIR):]
            print('Processing ' + date + 'gram' + gram_num)
            try:
                os.makedirs(PROCESSED_BY_DAY_DIR + date)
            except OSError:
                if not os.path.isdir(PROCESSED_BY_DAY_DIR + date):
                    raise        
            gram_f = day + gram_num + 'gram.txt'    
            # for gram_f in glob.glob(day + gram_num + 'gram.txt'):
            analyze_utils.process_grams(gram_f, PROCESSED_BY_DAY_DIR + date, gram_num)
    print("Done processing gram files")

def remove_old():
    files = glob.glob(CORPORA_DIR + '*/all*')
    for f in files:    
        print("removing " + f)
        os.remove(f)

def create_gram_list(gram):
    print("Creating list of unique tokens...")
    all_grams = set()
    files = glob.glob(PROCESSED_BY_DAY_DIR + '*/all' + gram + 'grams.csv')
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

def remove_all_gram_docs():
    files = glob.glob(PROCESSED_BY_GRAM_DIR + '*')
    for f in files:    
        print("removing " + f)
        os.remove(f)



gram_file_name = "all1grams.csv"
def create_gram_docs():
    try:
        os.makedirs(PROCESSED_BY_GRAM_DIR)
    except OSError:
        if os.path.isdir(PROCESSED_BY_GRAM_DIR):
            remove_all_gram_docs()
        else:
            raise
    created_files = set()
    days = glob.glob(PROCESSED_DIR + 'by_day/*/')
    for day in days:
        date = day[len(PROCESSED_DIR + 'by_day/'):]
        print('Working on ' + date)
        try:
            with open(day + gram_file_name, newline='') as gram_csv:
                gram_reader = csv.reader(gram_csv)
                for line in gram_reader:
                    token = line[3]
                    proportion = line[2]
                    rank = line[0]
                    count = line[1]
                    print('token is ' + token)
                    token_f_name = PROCESSED_BY_GRAM_DIR + token + ".csv"
                    if token not in created_files:
                        with open(token_f_name, mode='w') as token_f:
                            token_f.write('date,rank,count,proportion\n')
                        created_files.add(token)
                    with open(token_f_name, mode='a') as token_f:
                        token_f.write(date + ',' +  rank + ',' +  count + ',' +  proportion + '\n')     
        except EnvironmentError:
            continue

def create_gram_doc(gram):
    try:
        os.makedirs(PROCESSED_BY_GRAM_DIR)
    except OSError:
        if not os.path.isdir(PROCESSED_BY_GRAM_DIR):
            raise
    token_f_name = PROCESSED_BY_GRAM_DIR + gram + ".csv"
    with open(token_f_name, mode='w') as token_f:
        token_f.write('date,rank,count,proportion\n')
        days = glob.glob(PROCESSED_DIR + 'by_day/*/')
        for day in days:
            date = day[len(PROCESSED_DIR + 'by_day/'):len(day) - 1]
            print('Working on ' + date)
            try:
                with open(day + gram_file_name, newline='') as gram_csv:
                    gram_reader = csv.reader(gram_csv)
                    for line in gram_reader:
                        token = line[3]
                        if token != gram:
                            continue
                        proportion = line[2]
                        rank = line[0]
                        count = line[1]
                        token_f.write(date + ',' +  rank + ',' +  count + ',' +  proportion + '\n')     
            except EnvironmentError:
                continue

"""Accepts a list of tokens to analyze"""
def analyze_data_ranges(tokens):
    with open(PROCESSED_DIR + "token_ranges.csv", mode='w') as output:
        output_writer = csv.writer(output, lineterminator='\n')
        output_writer.writerow(['token', 'min_rank', 'max_rank', 'rank_range', 'min_count', 'max_count', 'count_range', 'min_prop', 'max_prop', 'prop_range', 'days'])
        for token in tokens:
            ranges = analyze_utils.analyze_ranges(token)
            if ranges != -1 and ranges[10] < 2 and float(ranges[5]) > 1:
                output_writer.writerow(ranges)






if __name__ == '__main__':
    # which_grams=['1']
    # process_all_grams(which_grams)
    # create_gram_list('1')
    # create_gram_docs() 
    token_list = []
    with open(PROCESSED_DIR + "all_1gram_list.json", "r") as f:
        token_list = ast.literal_eval(f.read())
    analyze_data_ranges(token_list)
    