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
    with open(FILENAME, 'w') as csv:
        csv.write('year,mon,mday,count\n')
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
    with open(FILENAME, 'w') as csv:
        csv.write('year,mon,mday,count\n')
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

def fetch_context(STRING):
    from lxml import etree
    os.chdir(RCDIR)
    logging.info('Starting context fetcher')
    context = list()
    STRING = STRING.lower()
    try:
        os.makedirs(RCDIR + "/context/")
    except OSError:
        if not os.path.isdir(RCDIR + "/context/"):
            raise
    FILENAME = RCDIR + '/context/'+ STRING.replace(' ','_') + '.txt'
    logging.debug(FILENAME)
    for page in glob.glob(RCDIR + '/pages/*/*.xml'):
        with open(page, 'r') as f:
            tree = etree.HTML(f.read())
        for comment in tree.iter('description'):
            if comment.text != None:
                if re.search(STRING, comment.text.lower()):
                    paragraphs = comment.text.lower().split('\n')
                    for item in paragraphs:
                        if re.search(STRING, item):
                            context.append(item)
    if not os.path.isfile(FILENAME):
        with open(FILENAME, 'w') as f:
            f.write(str(context))

def sentiment_tracker(STRING):
    if type(STRING) != str:
        raise TypeError('STRING is not a string')
    from lxml import etree
    from textblob import TextBlob
    os.chdir(RCDIR)
    logging.info('Starting sentiment tracker')
    logging.debug(RCDIR)
    try:
        os.makedirs(RCDIR + "/sentiment/")
    except OSError:
        if not os.path.isdir(RCDIR + "/sentiment/"):
            raise
    FILENAME = RCDIR + '/sentiment/'+ STRING.replace(' ','_') + '.csv'
    logging.debug(FILENAME)
    STRING = STRING.lower()       
    with open(FILENAME, 'w') as csv:
        csv.write('year,mon,mday,polarity\n')
        for path in glob.glob(RCDIR + '/pages/*/'):
            logging.debug(path)
            date = re.search('[0-9_]{10}',path).group()
            year = date[0:4]
            mon = date[5:7]
            day = date[8:10]
            comments = str()
            for page in glob.glob(path + '*.xml'):
                with open(page,'r') as f:
                    tree = etree.HTML(f.read())
                for item in tree.iter('description'):
                    if item.text != None:
                        if re.search(STRING,item.text.lower()):
                            comments += item.text.lower()
            polarity = TextBlob(comments).sentiment.polarity
            if comments != "":
                csv.write(year + ',' + mon + ',' + day + ',' + str(polarity) + '\n')
    logging.info(str(STRING) + '\'s counted')

def top_tokens():
    import ast
    os.chdir(RCDIR)
    for gram in ('1','2','3'):
        filename = 'top' + gram + 'grams.csv'
        with open(filename,'w') as f:
            f.write('rank,count,proportion,token\n')
        body = {}
        total_tokens = 0.
        for page in glob.glob(RCDIR + '/corpora/*/' + gram + 'gram.txt'):
            with open(page, 'r') as f:
                dictionary = ast.literal_eval(f.read())
                for key in dictionary:
                    total_tokens += dictionary.get(key)
                    if body.has_key(key):
                        body.update({key:body.get(key) + dictionary.get(key)})
                    else:
                        body.update({key:dictionary.get(key)})
        body = [(body.get(key), body.get(key)/total_tokens, key) for key in body]
        body = sorted(body, reverse=True)[:100]
        with open(filename,'a') as f:
            for ix, item in enumerate(body):
                f.write(str(ix + 1) + ',' + str(item[0]) + ',' + str(item[1]) + ',' + str(item[2]) + '\n')



