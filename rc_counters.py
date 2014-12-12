#!/usr/bin/env python
"""
Redicorpus-based counters
Utility for tracking tokens through corpora
Utility for tracking strings through pages
In development
"""
__author__ = "Dillon Niederhut"
__version__ = "0.0.2"
__email__ = "dillon.niederhut@gmail.com"

import re
import os
import glob
import logging
#RCDIR = os.environ.get('RCDIR')
RCDIR = '/Users/dillonniederhut/Dropbox/pydir/redicorpus'
logging.basicConfig(filename = 'tracker.log', level = logging.DEBUG, format = '%(asctime)s %(message)s')

def token_tracker(TOKEN):
    # Expects TOKEN to be a tuple of strings with length of 1, 2, or 3
    # For example, to search for 'foo', enter TOKEN = ('foo',)
    import ast
    if type(TOKEN) != str:
        raise TypeError('TOKEN is not a string')
    GRAM = len(TOKEN.split(' '))
    if GRAM < 1:
        raise ValueError('Length of TOKEN is less than one')
    if GRAM > 3:
        raise ValueError('Length of TOKEN is greater than three')
    os.chdir(RCDIR)
    logging.info('Starting token counter')
    logging.debug(RCDIR)
    try:
        os.makedirs(RCDIR + "/trackers/")
    except OSError:
        if not os.path.isdir(RCDIR + "/trackers/"):
            raise
    FILENAME = RCDIR + '/trackers/token_'+ str(TOKEN) + '.csv'
    logging.debug(FILENAME)
    if not os.path.isfile(FILENAME):
        with open(FILENAME, 'w') as f:
            f.write('year,mon,mday,count\n')
    with open(FILENAME, 'a') as csv:
        for path in glob.glob(RCDIR + '/corpora/*/' + str(GRAM) + 'gram.txt'):
            logging.debug(path)
            date = re.search('[0-9_]{10}',path).group()
            year = date[0:4]
            mon = date[5:7]
            day = date[8:10]
            with open(path,'r') as f:
                dictionary = ast.literal_eval(f.read())
            if type(dictionary) == dict:
                if dictionary.has_key(TOKEN):
                    csv.write(year + ',' + mon + ',' + day + ',' + str(dictionary.get(TOKEN)) + '\n')
                else:
                    csv.write(year + ',' + mon + ',' + day + ',' + '0' + '\n')
            else:
                pass
    logging.info(str(TOKEN) + '\'s counted')

def string_tracker(STRING):
    from lxml import etree
    os.chdir(RCDIR)
    logging.info('Starting string counter')
    logging.debug(RCDIR)
    try:
        os.makedirs(RCDIR + "/trackers/")
    except OSError:
        if not os.path.isdir(RCDIR + "/trackers/"):
            raise
    FILENAME = RCDIR + '/trackers/string_'+ str(STRING) + '.csv'
    logging.debug(FILENAME)
    if not os.path.isfile(FILENAME):
        f = open(FILENAME, 'w')
        f.write('year,mon,mday,count\n')
        f.close()
    with open(FILENAME, 'a') as csv:
        for path in glob.glob(RCDIR + '/pages/*/'):
            logging.debug(path)
            count = 0
            date = re.search('[0-9_]{10}',path).group()
            year = date[0:4]
            mon = date[5:7]
            day = date[8:10]
            for page in glob.glob(path + '*.xml'):
                f = open(page,'r')
                tree = etree.HTML(f.read())
                f.close()
                for comment in tree.iter('description'):
                    if comment.text != None:
                        count += comment.text.count(str(STRING))
            csv.write(year + ',' + mon + ',' + day + ',' + str(count) + '\n')
    logging.info(str(STRING) + '\'s counted')

def string_context(STRING):
    from lxml import etree
    os.chdir(RCDIR)
    logging.info('Starting string context')
    context = list()
    STRING = STRING.lower()
    try:
        os.makedirs(RCDIR + "/context/")
    except OSError:
        if not os.path.isdir(RCDIR + "/context/"):
            raise
    FILENAME = RCDIR + '/context/string_'+ STRING.replace(' ','_') + '.txt'
    logging.debug(FILENAME)
    for page in glob.glob(RCDIR + '/pages/*/*.xml'):
        with open(page, 'r') as f:
            tree = etree.HTML(f.read())
        for comment in tree.iter('description'):
            if re.search(STRING, comment.text.lower()):
                paragraphs = comment.text.lower().split('\n')
                for item in paragraphs:
                    if re.search(STRING, item):
                        context.append(item)
    if not os.path.isfile(FILENAME):
        with open(FILENAME, 'w') as f:
            f.write(str(context))


