#!/usr/bin/env python
"""
AskReddit-based corpus builder
In development
"""
__author__ = "Dillon Niederhut"
__version__ = "0.0.1"
__email__ = "dillon.niederhut@gmail.com"

import requests, re, time, os, glob
from lxml import etree

def get_links():
    print "Fetching links"
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
    rcdir = os.environ.get('RCDIR')
    now = time.strftime("%Y_%m_%d")
    try:
        os.makedirs(rcdir + "/pages/" + now)
    except OSError:
        if not os.path.isdir(rcdir + "/pages/" + now):
            raise
    os.chdir(rcdir + "/pages/" + now)
    print "Getting pages"
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
    from nltk import util, word_tokenize, PorterStemmer
    comments = list()
    print "Getting strings"
    for filename in glob.glob('*.xml'):
        f = open(filename, 'r')
        tree = etree.HTML(f.read())
        f.close()
        for element in tree.iter('p'):
            comments.append(element.text)
    while comments.count(None) > 0:
        comments.remove(None)
    comments = ' '.join(comments)
    comments = comments.encode('ascii','ignore')
    try:
        os.makedirs(rcdir + "/corpora/" + now)
    except OSError:
        if not os.path.isdir(rcdir + "/corpora/" + now):
            raise
    os.chdir(rcdir + "/corpora/" + now)
    print "Making tokens"
    stems = [PorterStemmer().stem(t) for t in word_tokenize(comments.lower())]
    for i in (1,2,3):
        print "making tokens for " + i + "grams"
        body = util.ngrams(stems, i)
        dictionary = dict()
        for gram in set(body):
            dictionary.update({gram : body.count(gram)})
        f = open(str(i) + 'gram.txt', 'w')
        f.write(str(sorted(dictionary)))
        f.close()
    return rcdir, now

def dailies():
    rcdir, now = build_corpus()
    from sklearn.feature_extraction import DictVectorizer
    from sklearn.feature_extraction.text import TfidfTransformer
    from sklearn.decomposition import NMF
    if len(glob.glob(rcdir + '/corpora/*')) > 7:
        print 'Running daily'
        V = DictVectorizer()
        T = TfidfTransformer()
        top_ten = list()
        for i in (1,2,3):
            mappings = list()
            for filename in glob.glob(rcdir + '/corpora/*/' + i + 'gram.txt')[-31:]:
                f = open(filename, 'r')
                text = eval(f.read())
                f.close()
                mappings.append(text)
            vectorized = V.fit_transform(mappings)
            transformed = T.fit_transform(vectorized)
            coefficients = list()
            for ix, item in enumerate(V.get_feature_names()):
                coefficients.append((transformed.getrow(-1).todense()[:,ix], item))
            for value in sorted(coefficients, reverse = True)[:10]:
                top_ten.append(value[-1])
        try:
            os.makedirs(rcdir + "/dailies/")
        except OSError:
            if not os.path.isdir(rcdir + "/dailies/"):
                raise
        os.chdir(rcdir + "/dailies/")
        f = open(now + '.txt','w')
        f.write(str(top_ten))
        f.close()
    else:
        print 'Not enough data to run comparison'

if __name__ == "__main__":
    dailies()
    print "Done!"
else:
    print "Script not run"
