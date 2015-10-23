"""
Utility for analyzing an already tokenized corpus.

"""
import re
import os
import glob
import logging
import math
import csv

DATA_DIR = os.getenv('HOME') + "/Documents/RC/rc_static/"
PROCESSED_DIR = DATA_DIR + 'processed/'
TOKENS_DIR = PROCESSED_DIR + 'tokens/'
CORPORA_DIR = DATA_DIR + "corpora/"
IGNORE_STR = ['/r/', '/u/', 'https//', 'http//', '?', '!', '[', ']', '^', '_', '+', '=', '\\', '/', '1', '2', '3', '4', '5', '6', '7', '8' '9', '0']


"""Helper functions for process_grams"""
def get_count(corpus, token):
    count = corpus.get(token)
    if not isinstance(count, int):
        raise TypeError("Corpus must be a dictionary of form token:count")
    return count

def has_token(corpus, token):
    return token in corpus

""" 
Takes in a gram_file of n-grams and their counts.

Creates a all_#grams.csv file with rank,count,proportion,token 
in the dest folder.
rank
proportion=count/(total tokens)

Note that csv files have no identifying data, and as such should be
stored in an identifying directory.

For the sake of data size, ignores grams with substrings that indicate
they are parts of urls or not words (see IGNORE_STR).
"""

def process_grams(gram_file, dest_dir, gram_n=999):
    newfile_heading = 'rank,count,proportion,token'
    import ast
    body = {}
    total_tokens = 0
    with open(gram_file, 'r') as f:
        corpus = ast.literal_eval(f.read())
        if not isinstance(corpus, dict):
            raise TypeError("gram_file must contain a dictionary.")
        for token in corpus:
            skip = False
            for ignore in IGNORE_STR:
                if ignore in token:
                    skip = True
                    break
            if skip:
                continue
            total_tokens += get_count(corpus, token)
            if token in body:
                body.update({token:body.get(token) + get_count(corpus, token)})
            else:
                body.update({token:get_count(corpus, token)})
    body = {token:float(count)/total_tokens for token, count in body.items()}
    body = [(body.get(token)*total_tokens, body.get(token), token) for token in body]
    body = sorted(body, reverse=True)
    filename = dest_dir + 'all' + gram_n + 'grams.csv'
    with open(filename,'w') as f:
        f.write(newfile_heading + '\n')
    with open(filename,'a') as f:
        for ix, item in enumerate(body):
            f.write(str(ix + 1) + ',' + str(item[0]) + ',' + str(item[1]) + ',' + str(item[2]) + '\n')


def analyze_ranges(token):
    try:
        token_filename = TOKENS_DIR + token + ".csv"
        with open(token_filename, newline='') as token_csv:
            print(token_filename)
            tok_reader = csv.reader(token_csv)
            max_rank, min_rank = -1, 99999999999
            max_count, min_count = -1, 99999999999
            max_prop, min_prop = -1, 99999999999
            days = 0
            for line in tok_reader:
                if line[1] == 'rank':
                    continue
                rank = float(line[1])
                count = float(line[2])
                prop = float(line[3])
                max_rank, min_rank = max(max_rank, rank), min(min_rank, rank)
                max_count, min_count = max(max_count, count), min(min_count, count)
                max_prop, min_prop = max(max_prop, prop), min(min_prop, prop)
                days += 1
            rank_range = max_rank - min_rank
            count_range = max_count - min_count
            prop_range = max_prop - min_prop
            return [token, str(min_rank), str(max_rank), str(rank_range), str(min_count), str(max_count), str(count_range), str(min_prop), str(max_prop), str(prop_range), days]
    except EnvironmentError:
        print("Environment Error on " + token)
        return -1
