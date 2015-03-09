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
    # Expects TOKEN to be a string with 1, 2, or 3 words, separated by
    # whitespace.
    import ast
    from nltk import PorterStemmer
    if type(TOKEN) != str:
        raise TypeError('TOKEN is not a string')
    GRAM = len(TOKEN.split(' '))
    if GRAM < 1:
        raise ValueError('Length of TOKEN is less than one')
    if GRAM > 3:
        raise ValueError('Length of TOKEN is greater than three')
    TOKEN = ' '.join([PorterStemmer().stem(item) for item in TOKEN.split(' ')])
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

def nltk_collocation_wrapper():
    import nltk
    from nltk.collocations import BigramCollocationFinder, BigramAssocMeasures
    from lxml import etree
    os.chdir(RCDIR)
    comments = list()
    for filename in glob.glob('pages/*/*.xml'):
        with open(filename, 'r') as f:
            tree = etree.HTML(f.read())
        for element in tree.iter('description'):
            comments.append(element.text)
    while comments.count(None) > 0:
        comments.remove(None)
    comments = ' '.join(comments)
    comments = nltk.wordpunct_tokenize(comments)
    finder = BigramCollocationFinder.from_words(comments)
    finder.apply_freq_filter(10)
    collocations = finder.nbest(nltk.collocations.BigramAssocMeasures().pmi,1000)
    with open('collocations.txt','w') as f:
        f.write(str(collocations))
    return collocations[:10]

def comment_mapper(TOKEN):
    from lxml import etree
    from nltk import wordpunct_tokenize, ngrams, PorterStemmer
    if type(TOKEN) == str:
        TOKEN = TOKEN.lower()
        TOKEN = ' '.join([PorterStemmer().stem(item) for item in TOKEN.split(' ')])
    else:
        raise TypeError
    try:
        os.makedirs(RCDIR + "/maps/")
    except OSError:
        if not os.path.isdir(RCDIR + "/maps/"):
            raise
    os.chdir(RCDIR)
    comments = list()
    ngram_list = list()
    comment_map = dict()
    for filename in glob.glob('pages/*/*.xml'):
        with open(filename, 'r') as f:
            tree = etree.HTML(f.read())
        for item in tree.iter('item'):
            for description in item.iter('description'):
                if type(description.text) == str and len(description.text) > 0:
                    comment = description.text.lower()
                    comment = comment.replace('quot','"')
                    if re.search(TOKEN,comment):
                        comment = comment.replace(TOKEN, '', 1)
                        comments.append(comment)
    comment_count = float(len(comments))
    for comment in comments:
        comment = [PorterStemmer().stem(word) for word in wordpunct_tokenize(comment)]
        for i in (1,2,3):
            for gram in ngrams(comment,i):
                ngram_list.append(gram)
    while len(ngram_list) > 0:
        gram = ' '.join(ngram_list.pop())
        if comment_map.has_key(gram):
            comment_map.update({gram:comment_map.get(gram) + 1})
        else:
            comment_map.update({gram:1})
    probability_map = sorted([(value/comment_count,key) for key, value in comment_map.items()], reverse = True)
    with open("maps/" + TOKEN + "_commap.txt",'w') as f:
        f.write(str(probability_map))
    return probability_map[:10]

def position_mapper(TOKEN):
    from lxml import etree
    from nltk import wordpunct_tokenize, PorterStemmer
    if type(TOKEN) == str:
        TOKEN = TOKEN.lower()
        TOKEN = ' '.join([PorterStemmer().stem(item) for item in TOKEN.split(' ')])
    else:
        raise TypeError
    try:
        os.makedirs(RCDIR + "/maps/")
    except OSError:
        if not os.path.isdir(RCDIR + "/maps/"):
            raise
    os.chdir(RCDIR)
    negative_two = list()
    negative_one = list()
    positive_one = list()
    positive_two = list()
    for filename in glob.glob('pages/*/*.xml'):
        with open(filename, 'r') as f:
            tree = etree.HTML(f.read())
        for item in tree.iter('item'):
            for description in item.iter('description'):
                if type(description.text) == str and len(description.text) > 0:
                    comment = description.text.lower()
                    comment = comment.replace('quot','"')
                    if re.search(TOKEN,comment):
                        comment = wordpunct_tokenize(comment)
                        try:
                            ix = comment.index(TOKEN)
                            if ix > 1:
                                negative_two.append(comment[ix-2])
                            if ix > 0:
                                negative_one.append(comment[ix-1])
                            if len(comment) - ix > 1:
                                positive_one.append(comment[ix+1])
                            if len(comment) - ix > 2:
                                positive_two.append(comment[ix+2])
                        except ValueError:
                            pass
    negative_two = sorted([(negative_two.count(item)/float(len(negative_two)), item) for item in set(negative_two)], reverse = True)
    negative_one = sorted([(negative_one.count(item)/float(len(negative_one)), item) for item in set(negative_one)], reverse = True)
    positive_one = sorted([(positive_one.count(item)/float(len(positive_one)), item) for item in set(positive_one)], reverse = True)
    positive_two = sorted([(positive_two.count(item)/float(len(positive_two)), item) for item in set(positive_two)], reverse = True)
    file_content = str({-2:negative_two,-1:negative_one,1:positive_one,2:positive_two})
    with open('maps/' + TOKEN + '_posmap.txt','w') as f:
        f.write(file_content)
    return negative_two[0], negative_one[0], positive_one[0], positive_two[0]

def top_links():
    from lxml import etree
    os.chdir(RCDIR)
    link_list = []
    for filename in glob.glob('pages/*/*.xml'):
        with open(filename, 'r') as f:
            tree = etree.HTML(f.read())
        for item in tree.iter('item'):
            for description in item.iter('description'):
                if type(description.text) == str and len(description.text) > 0:
                    comment = description.text
                    for regex in (re.compile(r'[\w.:/]+\.com[a-zA-Z0-9!#$%&_=+/.?-]*'),re.compile(r'[\w.:/]+\.com[a-zA-Z0-9!#$%&_=+/?-]*'),re.compile(r'[\w.:/]*youtu\.be[a-zA-Z0-9!#$%&_=+/?-]*')):
                        link_list.extend(regex.findall(comment))
    top_links = sorted([(link_list.count(item), item) for item in set(link_list)], reverse = True)
    with open('top_links.txt','w') as f:
        f.write(str(top_links))
    return top_links[:10]
