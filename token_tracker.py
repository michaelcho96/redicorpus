#!/usr/bin/env python
"""
Redicorpus-based token tracker
In development
"""
__author__ = "Dillon Niederhut"
__version__ = "0.0.1"
__email__ = "dillon.niederhut@gmail.com"

def token_tracker(TOKEN):
    # Expects TOKEN to be a tuple of strings with length of 1, 2, or 3
    # For example, to search for 'foo', enter TOKEN = ('foo',)
    if type(TOKEN) != tuple:
        raise TypeError('TOKEN is not a tuple')
    GRAM = len(TOKEN)
    if GRAM < 1:
        raise ValueError('Length of TOKEN is less than one')
    if GRAM > 3:
        raise ValueError('Length of TOKEN is greater than three')
    import re, os, glob, logging, ast
    #RCDIR = os.environ.get('RCDIR')
    RCDIR = '/Users/dillonniederhut/Dropbox/pydir/redicorpus'
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

