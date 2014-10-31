#!/usr/bin/env python
"""
AskReddit-based corpus builder
In development
"""
__author__ = "Dillon Niederhut"
__version__ = "0.0.1"
__email__ = "dillon.niederhut@gmail.com"

import requests, re, time, os, glob, logging
RCDIR = os.environ.get('RCDIR')
NOW = time.strftime("%Y_%m_%d")

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
        os.makedirs(RCDIR + "/pages/" + NOW)
    except OSError:
        if not os.path.isdir(RCDIR + "/pages/" + NOW):
            raise
    os.chdir(RCDIR + "/pages/" + NOW)
    logging.info("Getting pages")
    for i in links:
        url = str(i+".xml?limit=500")
        page = requests.get(url,headers = {
        'User-Agent' : 'redicorpus v. ' + __version__,
        'From' : __email__}).content
        name = str(re.search(r'[^http://www.reddit.com/r/AskReddit/comments/].{5}', i).group() + '.xml')
        f = open(name, 'w')
        f.write(page)
        f.close()
        logging.debug(url + ' saved as ' + name + ' in ' + RCDIR + "/pages/" + NOW)
        time.sleep(2)

def build_corpus(directory = RCDIR, date = NOW):
    # Builds unigram, bigram, and trigram count dictionaries from a set of xml
    # documents
    from lxml import etree
    from nltk import util, word_tokenize, PorterStemmer
    os.chdir(RCDIR + "/pages/" + NOW)
    comments = list()
    for filename in glob.glob('*.xml'):
        f = open(filename, 'r')
        tree = etree.HTML(f.read())
        f.close()
        for element in tree.iter('description'):
            comments.append(element.text)
    while comments.count(None) > 0:
        comments.remove(None)
    logging.info('Comment number = ' + str(len(comments)))
    comments = ' '.join(comments)
    comments = comments.encode('ascii','ignore')
    for i in (',','.',':',';','"'):
        comments = comments.replace(i,'')
    try:
        os.makedirs(RCDIR + "/corpora/" + NOW)
    except OSError:
        if not os.path.isdir(RCDIR + "/corpora/" + NOW):
            raise
    os.chdir(RCDIR + "/corpora/" + NOW)
    stems = [PorterStemmer().stem(t) for t in word_tokenize(comments.lower())]
    logging.info('Stem number = ' + str(len(stems)))
    for i in (1,2,3):
        logging.info('Making tokens for ' + str(i) + 'grams')
        body = util.ngrams(stems, i)
        logging.info(str(i) + 'gram number = ' + str(len(body)))
        dictionary = dict()
        unique_tokens = set(body)
        logging.info('Unique ' + str(i) + 'gram number = ' + str(len(unique_tokens)))
        for element in unique_tokens:
            dictionary.update({element:body.count(element)})
        f = open(str(i) + 'gram.txt', 'w')
        f.write(str(dictionary))
        f.close()
        logging.info(str(i) + 'gram.txt saved in ' + RCDIR + "/corpora/" + NOW)

def daily(directory = RCDIR, date = NOW):
    # Compares a day's corpus with previous days' corpora (at least one week
    # and up to one month), finds the top ten most unique unigrams, bigrams,
    # and trigrams, and outputs them as a dated file
    from sklearn.feature_extraction import DictVectorizer
    from sklearn.feature_extraction.text import TfidfTransformer
    from sklearn.decomposition import NMF
    if len(glob.glob(RCDIR + '/corpora/*')) > 7:
        logging.info('Running daily')
        V = DictVectorizer()
        T = TfidfTransformer()
        top_ten = list()
        for i in (1,2,3):
            mappings = list()
            for filename in glob.glob(RCDIR + '/corpora/*/' + str(i) + 'gram.txt')[-31:]:
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
            os.makedirs(RCDIR + "/dailies/")
        except OSError:
            if not os.path.isdir(RCDIR + "/dailies/"):
                raise
        os.chdir(RCDIR + "/dailies/")
        f = open(NOW + '.txt','w')
        f.write(str(top_ten))
        f.close()
        logging.info(NOW + '.txt' + 'saved in ' + RCDIR + "/dailies/")
    else:
        logging.info('Not enough data to run comparison')

if __name__ == "__main__":
    os.chdir(RCDIR) 
    logging.basicConfig(filename = 'rc_builder.log', level = logging.INFO, format = '%(asctime)s %(message)s')
    logging.info('Starting script')
    logging.info('Directory = ' + RCDIR + ', Time = ' + NOW)
    get_pages(RCDIR, NOW)
    build_corpus(RCDIR, NOW)
    daily(RCDIR, NOW)
    logging.info('Finished script')
else:
    logging.info('Script failed to initialize')
