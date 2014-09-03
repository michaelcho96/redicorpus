#!/usr/bin/env python
"""
AskReddit-based corpus builder
In development
"""
__author__ = "Dillon Niederhut"
__version__ = "0.0.1"
__email__ = "dillon.niederhut@gmail.com"

import requests, re, io, time, os, glob
from lxml import etree
from nltk import util, word_tokenize, PorterStemmer

def get_links():
    page = etree.XML(requests.get('http://reddit.com/r/Askreddit/.xml', headers = {
        'User-Agent' : 'redicorpus v. ' + __version__,
        'From' : __email__
    }).content)
    links = list()
    for element in page.iter('guid'):
        links.append(element.text)
    return links

def get_pages():
    links = get_links()
    rcdir = os.getcwd()
    now = time.strftime("%Y_%m_%d")
    try:
        os.makedirs(rcdir + "/pages/" + now)
    except OSError:
        if not os.path.isdir(rcdir + "/pages/" + now):
            raise
    os.chdir(rcdir + "/pages/" + now)
    for i in links:
        url = str(i+".xml/?limit=500")
        page = requests.get(url,headers = {
        'User-Agent' : 'redicorpus v. ' + __version__,
        'From' : __email__}).content
        name = str(re.search(r'[^http://www.reddit.com/r/AskReddit/comments/].{5,5}', i).group() + '.xml')
        f = open(name, 'w')
        f.write(page)
        f.close()
        time.sleep(2)
    return rcdir, now

def build_corpus():
    rcdir, now = get_pages()
    comments = list()
    os.getcwd()
    for filename in glob.glob('*.xml'):
        f = open(filename, 'r')
        tree = etree.HTML(f.read())
        f.close()
        for element in tree.iter('p'):
            comments.append(element.text)
    comments = str(comments)
    try:
        os.makedirs(rcdir + "/corpora/" + now)
    except OSError:
        if not os.path.isdir(rcdir + "/corpora/" + now):
            raise
    os.chdir(rcdir + "/corpora/" + now)
    stems = [PorterStemmer().stem(t) for t in word_tokenize(comments.lower())]
    for i in (1,2,3):
        body = str(sorted(util.ngrams(stems, i)))
        f = open(str(i) + 'gram.txt', 'w')
        f.write(body)
        f.close()
    print "Done!"

if __name__ == "__main__":
    build_corpus()
else:
    print "Goodbye"
