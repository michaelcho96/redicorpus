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

import re, os, glob, logging
RCDIR = os.environ.get('RCDIR')

def token_tracker(TOKEN):
    # Expects TOKEN to be a tuple of strings with length of 1, 2, or 3
    # For example, to search for 'foo', enter TOKEN = ('foo',)
    import ast
    if type(TOKEN) != tuple:
        raise TypeError('TOKEN is not a tuple')
    GRAM = len(TOKEN)
    if GRAM < 1:
        raise ValueError('Length of TOKEN is less than one')
    if GRAM > 3:
        raise ValueError('Length of TOKEN is greater than three')
    os.chdir(RCDIR)
    logging.basicConfig(filename = 'tracker.log', level = logging.DEBUG, format = '%(asctime)s %(message)s')
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
    logging.basicConfig(filename = 'tracker.log', level = logging.INFO, format = '%(asctime)s %(message)s')
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
            count = int()
            date = re.search('[0-9_]{10}',path).group()
            year = date[0:4]
            mon = date[5:7]
            day = date[8:10]
            for page in glob.glob(path + '*.xml'):
                f = open(page,'r')
                tree = etree.HTML(f.read())
                f.close()
                for comment in tree.iter('description'):
                    count = count + comment.text.count(str(STRING))
            csv.write(year + ',' + mon + ',' + day + ',' + str(count) + '\n')
    logging.info(str(STRING) + '\'s counted')

