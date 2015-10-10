import analyze_utils
import re
import os
import glob

DATA_DIR = "~/Documents/RC/rc_static/"
CORPORA_DIR = DATA_DIR + "corpora/"

""" 
Accepts a list of strings containing any combination of ['1', '2', '3'], indicating gram number n.
Calls process_grams from analyze_utils on all n-grams in the CORPORA dirctory
"""
def process_all_grams(which_grams):
    for gram_num in which_grams:
        for day in glob.glob(CORPORA_DIR + '*/'):
            print('Processing ' + day[CORPORA_DIR.length:] + 'gram' + gram_num)
            for gram_f in glob.glob(day + gram_num + 'gram.txt'):
                process_grams(gram_f, day, gram_num)

if __name__ == '__main__':
    which_grams=['1']
    process_all_grams(which_grams)
