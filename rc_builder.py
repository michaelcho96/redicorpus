#!/usr/bin/env python
"""
AskReddit-based corpus builder
In development
"""
__author__ = "Dillon Niederhut"
__version__ = "0.0.1"
__email__ = "dillon.niederhut@gmail.com"

import requests, re, time, os, glob, logging

def get_links():
    from lxml import etree
    print "Fetching links"
    page = etree.XML(requests.get('http://reddit.com/r/Askreddit/.xml', headers = {
        'User-Agent' : 'redicorpus v. ' + __version__,
        'From' : __email__
    }).content)
    links = list()
    for element in page.iter('guid'):
        links.append(element.text)
    logging.info('links = ' + links)
    return links

def get_pages(directory = rcdir, time = now):
    links = get_links()
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
        logging.info(url + ' saved as ' + name + ' in ' + rcdir + "/pages/" + now)
        time.sleep(2)


def build_corpus(directory = rcdir, time = now):
    from lxml import etree
    from nltk import util, word_tokenize, PorterStemmer
    comments = list()
    for filename in glob.glob('*.xml'):
        f = open(filename, 'r')
        tree = etree.HTML(f.read())
        f.close()
        for element in tree.iter('p'):
            comments.append(element.text)
    while comments.count(None) > 0:
        comments.remove(None)
    logging.info('Comment number = ' + len(comments))
    comments = ' '.join(comments)
    comments = comments.encode('ascii','ignore')
    for i in (',','.',':',';','"'):
        comments = comments.replace(i,'')
    try:
        os.makedirs(rcdir + "/corpora/" + now)
    except OSError:
        if not os.path.isdir(rcdir + "/corpora/" + now):
            raise
    os.chdir(rcdir + "/corpora/" + now)
    stems = [PorterStemmer().stem(t) for t in word_tokenize(comments.lower())]
    logging.info('Stem number = ' + len(stems))
    for i in (1,2,3):
        logging.info('Making tokens for ' + i + 'grams')
        body = util.ngrams(stems, i)
        logging.info(i + 'gram number = ' + len(body))
        dictionary = dict()
        grams = set(body)
        logging.info('Unique ' i + 'gram number = ' + len(grams))
        for gram in grams:
            dictionary.update({gram : body.count(gram)})
        f = open(str(i) + 'gram.txt', 'w')
        f.write(str(sorted(dictionary)))
        f.close()
        logging.info(str(i) + 'gram.txt saved in ' + rcdir + "/corpora/" + now)

def daily(directory = rcdir, time = now):
    from sklearn.feature_extraction import DictVectorizer
    from sklearn.feature_extraction.text import TfidfTransformer
    from sklearn.decomposition import NMF
    if len(glob.glob(rcdir + '/corpora/*')) > 7:
        logging.info('Running daily')
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
        logging.info(now + '.txt' + 'saved in ' rcdir + "/dailies/")
    else:
        logging.info('Not enough data to run comparison')

if __name__ == "__main__":   
    logging.basicConfig(filename = 'rc_builder.log', level = logging.INFO, format = '%(asctime)s %(message)s')
    logging.info('Starting script')
    rcdir = os.environ.get('RCDIR')
    now = time.strftime("%Y_%m_%d")
    logging.info('Directory = ' + rcdir + ', Time = ' + now)
    get_pages(rcdir, now)
    build_corpus(rcdir, now)
    daily(rcdir, now)
    logging.info('Finished script')
else:
    logging.info('Script failed to initialize')
