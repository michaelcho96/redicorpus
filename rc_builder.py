#!/usr/bin/env python
"""
AskReddit-based corpus builder
In development
"""
__author__ = "Dillon Niederhut"
__version__ = "0.0.2"
__email__ = "dillon.niederhut@gmail.com"

import requests 
import re
import time
import os
import glob
import logging

RCDIR = os.environ.get('RCDIR')
NOW = time.strftime("%Y_%m_%d")
logging.basicConfig(filename = RCDIR + '/rc_builder.log', level = logging.INFO, format = '%(asctime)s %(message)s')

def get_links():
    # Retrieves top hundred links from AskReddit and returns them as a list
    # of web addresses
    from lxml import etree
    logging.info("Fetching links")
    base_url = 'http://reddit.com/r/Askreddit/.xml'
    last = ''
    links = list()
    for i in ('','?after=t3_','?after=t3_','?after=t3_'):
        page = etree.HTML(requests.get(base_url + i + last, headers = {
            'User-Agent' : 'redicorpus v. ' + __version__,
            'From' : __email__
        }).content)
        for element in page.iter('guid'):
            links.append(element.text)
        last = re.search(r'[^http://www.reddit.com/r/AskReddit/comments/].{5}',links[-1]).group()
        time.sleep(2)
    logging.debug('links = ' + str(links))
    return links

def get_pages(directory = RCDIR, date = NOW):
    # Retrieves AskReddit comments and saves them to disk as unique id names
    # in a dated folder
    links = get_links()
    try:
        os.makedirs(RCDIR + "/pages/" + date)
    except OSError:
        if not os.path.isdir(RCDIR + "/pages/" + date):
            raise
    os.chdir(RCDIR + "/pages/" + date)
    logging.info("Getting pages")
    for i in links:
        url = str(i+".xml?limit=500&sort=random")
        try:
            page = requests.get(url,headers = {
            'User-Agent' : 'redicorpus v. ' + __version__,
            'From' : __email__}).content
            name = str(re.search(r'[^http://www.reddit.com/r/AskReddit/comments/].{5}', i).group() + '.xml')
            f = open(name, 'w')
            f.write(page)
            f.close()
            logging.debug(url + ' saved as ' + name + ' in ' + RCDIR + "/pages/" + date)
        except:
            pass
        time.sleep(2)

def build_corpus(directory = RCDIR, date = NOW):
    # Builds unigram, bigram, and trigram count dictionaries from a set of xml
    # documents
    from lxml import etree
    from nltk import ngrams, word_tokenize, PorterStemmer
    os.chdir(RCDIR + "/pages/" + date)
    comments = list()
    for filename in glob.glob('*.xml'):
        with open(filename, 'r') as f:
            tree = etree.HTML(f.read())
        for item in tree.iter('item'):
            for description in item.iter('description'):
                comments.append(description.text)
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

def dailies(directory = RCDIR, date = NOW):
    # Compares a day's corpus with previous days' corpora (at least one week
    # and up to one month), finds the top twenty-five most unique (as measured
    # by tf-idf and multiples of expexted frequency) unigrams, bigrams, and
    # trigrams as, and outputs them as dated files
    import math
    from ast import literal_eval
    if len(glob.glob(RCDIR + '/corpora/*')) > 7:
        logging.info('Running dailies')
        top_tfidf = list()
        top_expected = list()
        top_google = list()
        for i in (1,2,3):
            corpus = list()
            tfidf_coef = list()
            expected_coef = list()
            file_list = sorted(glob.glob(RCDIR + '/corpora/*/' + str(i) + 'gram.txt'))
            document_N = len(file_list[-31:])
            term_N = int()
            with open(file_list[-1],'r') as f:
                today = literal_eval(f.read())
            for filename in file_list[-31:]:
                with open(filename, 'r') as f:
                    corpus.append(literal_eval(f.read()))
            for document in corpus:
                term_N += len(document)
            for key in today.keys():
                document_freq = float()
                term_freq = float()
                for document in corpus:
                    if document.has_key(key):
                        document_freq += 1
                        term_freq += document.pop(key)
                tfidf_coef.append((today.get(key) * math.log(document_N/document_freq),key))
                expected_coef.append((today.get(key)*term_N / (len(today)*term_freq),key))
                expected_coef.append((((today.get(key)-len(today)*term_freq/term_N)**2) / (len(today)*term_freq/term_N),key))
            for coef, gram in sorted(tfidf_coef, reverse = True)[:25]:
                top_tfidf.append((gram, coef))
            for coef, gram in sorted(expected_coef, reverse = True)[:25]:
                top_expected.append((gram, coef))          
        try:
            os.makedirs(RCDIR + "/dailies/tfidf/")
        except OSError:
            if not os.path.isdir(RCDIR + "/dailies/tfidf/"):
                raise
        os.chdir(RCDIR + "/dailies/tfidf/")
        with open(date + '.txt','w') as f:
            f.write(str(top_tfidf))
        logging.info(date + '.txt' + 'saved in ' + RCDIR + "/dailies/tfidf/")
        try:
            os.makedirs(RCDIR + "/dailies/expected/")
        except OSError:
            if not os.path.isdir(RCDIR + "/dailies/expected/"):
                raise
        os.chdir(RCDIR + "/dailies/expected/")
        with open(date + '.txt','w') as f:
            f.write(str(top_expected))
        logging.info(date + '.txt' + 'saved in ' + RCDIR + "/dailies/expected/")
    else:
        logging.info('Not enough data to run comparison')

if __name__ == "__main__":
    os.chdir(RCDIR) 
    logging.info('Starting script')
    logging.info('Directory = ' + RCDIR + ', Time = ' + NOW)
    get_pages(RCDIR, NOW)
    build_corpus(RCDIR, NOW)
    dailies(RCDIR, NOW)
    logging.info('Finished script')
