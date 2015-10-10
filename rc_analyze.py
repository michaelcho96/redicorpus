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

def get_count(corpus, token):
    return corpus.get(token)

def has_token(corpus, token):
    return corpus.has_key(token)

""" 
Assumes DATA_DIR contains CORPORA_DIRs organized by date, 
containing files of format '#gram.txt'.
Creates a .csv file with rank,count,proportion,token in the date folder
"""
def top_gram_by_day():
    newfile_heading = 'rank,count,proportion,token'
    import ast
    import json
    os.chdir(DATA_DIR)
    which_grams = ['1']
    for gram_num in which_grams:
        for day in glob.glob(CORPORA_DIR + '*/'):
            print('Processing ' + day[CORPORA_DIR.length:])
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
            filename = day + 'all_top' + gram_num + 'grams.csv'
            with open(filename,'w') as f:
                f.write(newfile_heading + '\n')
            with open(filename,'a') as f:
                for ix, item in enumerate(body):
                    f.write(str(ix + 1) + ',' + str(item[0]) + ',' + str(item[1]) + ',' + str(item[2]) + '\n')
