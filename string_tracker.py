#!/usr/bin/env python
"""
Redicorpus-based string tracker
In development
"""
__author__ = "Dillon Niederhut"
__version__ = "0.0.1"
__email__ = "dillon.niederhut@gmail.com"

def string_tracker(STRING):
    import re, os, glob, logging
    from lxml import etree
    #RCDIR = os.environ.get('RCDIR')
    RCDIR = '/Users/dillonniederhut/Dropbox/pydir/redicorpus'
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