#!/usr/bin/env python
"""
High temporal resolution, web-based corpus building and querying
"""
__author__ = "Dillon Niederhut"
__version__ = "0.1.0"
__email__ = "dillon.niederhut@gmail.com"

import re
import os
import glob
import logging
import requests
import datetime
import os
import glob
import logging
import yaml
import json
from nltk import ngrams
from pymongo import MongoClient

#RCDIR = os.environ.get('RCDIR')
RCDIR = '/Users/dillonniederhut/Dropbox/pydir/redicorpus'
os.chdir(RCDIR)
mongo = MongoClient()
logging.basicConfig(filename = RCDIR + '/redicorpus.log', level = logging.INFO, format = '%(asctime)s %(message)s')

class comment(object):
    """A single communicative event"""

    def __init__(self):
        self = self

    def counts(self, grams=(1,2,3)):
        database = self['source']
        for name in  ('strings', 'stems', 'lemmas'):
            collection = mongo.collection.Collection(database, name + 'Counts')
            for n in grams:
                gram_list = ngrams(self[name]['data'], n)
                for gram in gram_list:
                    collection.replace({'_id':gram, date:self.date})
            collection = mongo.collection.Collection(database, name + 'Activation')
            for n in grams:


    def read(self):

    def build(self):




def build_corpus(directory = RCDIR, date = NOW):
    """
    Builds unigram, bigram, and trigram count dictionaries from a set of xml
    documents
    """
    from nltk import ngrams, word_tokenize, PorterStemmer
    os.chdir(RCDIR + "/pages/" + date)
    comments = list()
    for filename in glob.glob('*.json'):
        with open(filename, 'r') as f:
            tree = json.load(f)
        for comment in tree[1]:
            for data in comment['data']:
                comments.append(data['body'])
    while comments.count(None) > 0:
        comments.remove(None)
    logging.info('Comment number = ' + str(len(comments)))
    comments = ' '.join(comments)
    comments = comments.encode('ascii','ignore')
    for i in (',','.',':',';','"','*',"'",'~','|','!','quot','<','>','?','[',']'):
        comments = comments.replace(i,'')
    comments = comments.replace('&',' and ')
    try:
        os.makedirs(RCDIR + "/corpora/" + date)
    except OSError:
        if not os.path.isdir(RCDIR + "/corpora/" + date):
            raise
    os.chdir(RCDIR + "/corpora/" + date)
    stems = [PorterStemmer().stem(t) for t in word_tokenize(comments.lower())]
    logging.info('Stem number = ' + str(len(stems)))
    for i in (1,2,3):
        logging.info('Making tokens for ' + str(i) + 'grams')
        body = list(ngrams(stems, i))
        logging.info(str(i) + 'gram number = ' + str(len(body)))
        dictionary = dict()
        while len(body) > 0:
            element = ' '.join(body.pop())
            if dictionary.has_key(element):
                dictionary.update({element:dictionary.get(element) + 1})
            else:
                dictionary.update({element:1})
        logging.info('Unique ' + str(i) + 'gram number = ' + str(len(dictionary)))
        with open(str(i) + 'gram.txt', 'w') as dictionary_file:
            dictionary_file.write(str(dictionary))
        logging.info(str(i) + 'gram.txt saved in ' + RCDIR + "/corpora/" + date)

def token_tracker(TOKEN):
    """
    Expects TOKEN to be a string with 1, 2, or 3 words, separated by
    whitespace.
    """
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
    #change to json
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
    #change to json
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
    for gram in ('1'):
    #for gram in ('1','2','3'):
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
        body = {key:value/total_tokens for key, value in body.items()}
        with open('total' + str(gram) + 'grams.txt', 'w') as f:
            f.write(str(body))
        body = [(body.get(key)*total_tokens, body.get(key), key) for key in body]
        body = sorted(body, reverse=True)[:100]
        with open(filename,'a') as f:
            for ix, item in enumerate(body):
                f.write(str(ix + 1) + ',' + str(item[0]) + ',' + str(item[1]) + ',' + str(item[2]) + '\n')

def nltk_collocation_wrapper():
    import nltk
    from nltk.collocations import BigramCollocationFinder, BigramAssocMeasures
    #change to json
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
    #change to json
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
    total_gram_count = float()
    for comment in comments:
        comment = [PorterStemmer().stem(word) for word in wordpunct_tokenize(comment)]
        total_gram_count += len(comment)
        for i in (1,2,3):
            for gram in ngrams(comment,i):
                ngram_list.append(gram)
    while len(ngram_list) > 0:
        gram = ' '.join(ngram_list.pop())
        if comment_map.has_key(gram):
            comment_map.update({gram:comment_map.get(gram) + 1})
        else:
            comment_map.update({gram:1})
    probability_map = sorted([(value/total_gram_count,key) for key, value in comment_map.items()], reverse = True)
    with open("maps/" + TOKEN.replace(' ','_') + "_commap.txt",'w') as f:
        f.write(str(probability_map))
    return probability_map[:10]

def word_mapper(TOKEN, gram_length=1):
    #change to json
    from nltk import wordpunct_tokenize, ngrams, PorterStemmer
    if type(TOKEN) == str:
        TOKEN = TOKEN.lower()
        TOKEN = ' '.join([PorterStemmer().stem(word) for word in TOKEN.split(' ')])
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
                    for i in (',','.',':',';','"','*',"'",'~','|','!','quot','<','>','?','[',']'):
                        comment = comment.replace(i,'')
                    comment = comment.replace('&','and')
                    comment = ' '.join([PorterStemmer().stem(word) for word in wordpunct_tokenize(comment)])
                    if re.search(TOKEN,comment):
                        comment = comment.replace(TOKEN, '', 1)
                        comments.append(wordpunct_tokenize(comment))
    for comment in comments:
        for gram in ngrams(comment,gram_length):
            ngram_list.append(gram)
    while len(ngram_list) > 0:
        gram = ' '.join(ngram_list.pop())
        if comment_map.has_key(gram):
            comment_map.update({gram:comment_map.get(gram) + 1})
        else:
            comment_map.update({gram:1})
    total_count = sum(comment_map.values())
    comment_map = {key:value/float(total_count) for key,value in comment_map.items()}
    with open("maps/" + TOKEN.replace(' ','_') + "_wordmap.txt",'w') as f:
        f.write(str(comment_map))
    return sorted([(value,key) for key,value in comment_map.items()], reverse = True)[:25]

def position_mapper(TOKEN): #rewrite as dict
    #change to json
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
    with open('maps/' + TOKEN.replace(' ','_') + '_posmap.txt','w') as f:
        f.write(file_content)
    return negative_two[0], negative_one[0], positive_one[0], positive_two[0]

def top_links():
    #change to json
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

def zipf_test(word):
    from ast import literal_eval
    from nltk import wordpunct_tokenize, PorterStemmer
    chi_square_total = 0.
    if type(token) != str:
        raise TypeError
    else:
        token = word.lower()
        token = ' '.join([PorterStemmer().stem(item) for item in token.split(' ')])
    filename = 'maps/' + token.replace(' ','_') + '_wordmap.txt'
    if not os.path.isfile(filename):
        word_mapper(word)
    with open(filename,'r') as f:
        word_map = literal_eval(f.read())
    filename = 'total1grams.txt'
    with open(filename, 'r') as f:
        total_probs = literal_eval(f.read())
    for key in total_probs.keys():
        if word_map.has_key(key):
            chi_square_element = ((float(word_map.get(key))*1000000 - total_probs.get(key)*1000000)**2)/(total_probs.get(key)*1000000)
        else:
            chi_square_element = ((0. - total_probs.get(key)*1000000)**2)/(total_probs.get(key)*1000000)
        chi_square_total += chi_square_element
    return chi_square_total, len(word_map)-1

def zipf_control(p,n=10):
    from ast import literal_eval
    from numpy import random
    #change to json
    from nltk import wordpunct_tokenize, PorterStemmer
    chi_square_list = []
    n_total = []
    with open('total1grams.txt','r') as f:
        total_probs = literal_eval(f.read())
    for i in range(0,n):
        comments = []
        chi_square_total = 0.
        n_comments = 0
        body = {}
        for page in glob.glob(RCDIR + '/pages/*/*.xml'):
            with open(page, 'r') as f:
                tree = etree.HTML(f.read())
            for description in tree.iter('description'):
                if description.text != None:
                    if random.binomial(1,p) == 1:
                        n_comments += 1
                        comments.append(description.text.lower())
        comments = ' '.join(comments)
        for punctuation in (',','.',':',';','"','*',"'",'~','|','!','quot','<','>','?','[',']'):
            comments = comments.replace(punctuation,'')
        comments = comments.replace('&',' and ')
        stemmed_words = [PorterStemmer().stem(word) for word in wordpunct_tokenize(comments)]
        while len(stemmed_words) > 0:
            word = stemmed_words.pop()
            if word in body:
                body.update({word:body.get(word)+1})
            else:
                body.update({word:1})
        body_length = sum(body.values())
        for key in total_probs.keys():
            if key in body:
                chi_square_total += ((float(body.get(key)) - total_probs.get(key)*body_length)**2)/(total_probs.get(key)*body_length)
            else:
                chi_square_total += ((0. - total_probs.get(key)*body_length)**2)/(total_probs.get(key)*body_length)
        chi_square_list.append(chi_square_total)
        n_total.append(n_comments)
    return sum(chi_square_list)/len(chi_square_list), sum(n_total)/len(n_total)

    # class document(object):
#     """A page with metadata"""

#     def __init__(self):
#         self.data = []

#     def build(self, content):
#         """Build document from structured dict"""
#         if type(data) != dict:
#             raise TypeError('Content is not json-like')
#         self._id = content['_id']
#         self.source = content['source']
#         self.created = content['created']
#         self.requested = content['requested']
#         self.data = content['data']

#     def write_json(self):
#         """Write document to file as json"""
#         datename = create_datename(self.created)
#         try:
#             os.makedirs(RCDIR + "/pages/" + datename)
#         except OSError:
#             if not os.path.isdir(RCDIR + "/pages/" + datename):
#                 raise
#         with open(RCDIR + '/pages/' + datename + '/' + self._id + '.json','w') as f:
#             json.dump({'_id' : self._id, 'source' : self.source,
#                        'created' : self.created, 'requested' : self.requested
#                        'data' : self.data}, f)

#     def read_json(fp):
#         """Read document from json by filepath"""
#         with open(fp,'r') as f:
#             return document.build(json.load(f))

#     @staticmethod
#     def read_json_from_date(date, num_days=0, all_data=False):
#         """
#         Read page(s) by a datetime object and integer of days before or after.
#         Returns a generator of loaded json pages
#         E.g. ...from_date(datetime.datetime(2000,12,25), -12) for the twelve
#         days of Christmas. To return all json pages, set all_data=True
#         """
#         if all_data == True:
#             for fp in glob.glob(RCDIR + '/pages/*/*.json'):
#                 yield document.read_json(fp)
#         else:
#             if num_days == 0:
#                 datename = create_datename(date)
#                 for fp in glob.glob(RCDIR + '/pages/' + datename + '/*.json'):
#                     yield document.read_json(fp)
#             if num_days != 0:
#                 for i in range(0:num_days):
#                     datename = create_datename(datetime.date(date) + datetime.timedelta(i))
#                     for fp in glob.glob(RCDIR + '/pages/' + date_name + '/*.json'):
#                         yield document.read_json(fp)
