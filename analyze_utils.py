"""
Utility for analyzing an already tokenized corpus.

"""
import re
import os
import glob
import logging
import math

DATA_DIR = "~/Documents/RC/rc_static/"
CORPORA_DIR = DATA_DIR + "corpora/"
IGNORE_STR = ['/r/', '/u/', 'https//', 'http//', '1', '2', '3', '4', '5', '6', '7', '8' '9', '0']


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
stored in the same directory as the corrosponding gram files.

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

""" 
Assumes DATA_DIR contains CORPORA_DIRs organized by date, 
containing files of format '#gram.txt'.

Creates a all_#grams.csv file with rank,count,proportion,token 
in the date folder
"""
def top_gram_by_day():
    newfile_heading = 'rank,count,proportion,token'
    import ast
    import json
    os.chdir(DATA_DIR)
    which_grams = ['1']
    for gram_num in which_grams:
        for day in glob.glob(CORPORA_DIR + '*/'):
            print('Processing ' + day[len(CORPORA_DIR):])
            body = {}
            total_tokens = 0.
            for gram_f in glob.glob(day + gram_num + 'gram.txt'):
                with open(gram_f, 'r') as f:
                    corpus = ast.literal_eval(f.read())
                    for token in corpus:
                        skip = False
                        for ignore in IGNORE_STR:
                            if ignore in token:
                                skip = True
                                break
                        if skip:
                            continue
                        total_tokens += get_count(corpus, token)
                        if body.has_key(token):
                            body.update({token:body.get(token) + get_count(corpus, token)})
                        else:
                            body.update({token:get_count(corpus, token)})
            body = {token:count/total_tokens for token, count in body.items()}
            body = [(body.get(token)*total_tokens, body.get(token), token) for token in body]
            body = sorted(body, reverse=True)
            filename = day + 'all' + gram_num + 'grams.csv'
            with open(filename,'w') as f:
                f.write(newfile_heading + '\n')
            with open(filename,'a') as f:
                for ix, item in enumerate(body):
                    f.write(str(ix + 1) + ',' + str(item[0]) + ',' + str(item[1]) + ',' + str(item[2]) + '\n')
