#!/usr/bin/env python
"""
Samples top 100 links on AskReddit every half hour and counts number 
of comments
"""
__author__ = "Dillon Niederhut"
__version__ = "0.0.1"
__email__ = "dillon.niederhut@gmail.com"

import requests, re, time, os, glob, logging
#RCDIR = os.environ.get('RCDIR')
RCDIR = '/Users/dillonniederhut/Dropbox/pydir/redicorpus'
FILENAME = time.strftime("%Y_%m_%d") + '_counts.csv'

def count_comments():
    # Grabs the top 100 links from AskRedddit and sums their comment counts
    # every hour, and logs the totals in a csv
    from lxml import etree
    try:
        os.makedirs(RCDIR + "/counts/")
    except OSError:
        if not os.path.isdir(RCDIR + "/counts/"):
            raise
    os.chdir(RCDIR + "/counts/")
    f = open(FILENAME, 'w')
    f.write('year,mon,mday,wday,hour,min,count\n')
    f.close()
    logging.info("Fetching links")
    while True:
        base_url = 'http://reddit.com/r/Askreddit/.xml'
        last = ''
        links = list()
        comment_number = int(0)
        for i in ('','?after=t3_','?after=t3_','?after=t3_'):
            page = etree.HTML(requests.get(base_url + i + last, headers = {
                'User-Agent' : 'comment counter v. ' + __version__,
                'From' : __email__
            }).content)
            for item in page.iter('item'):
                for description in item.iter('description'):
                   comment_number = comment_number + int(re.search('[0-9]+(?= comment)', description.text).group())
            logging.info('Comment number is ' + str(comment_number))
            for guid in page.iter('guid'):
                links.append(guid.text)
            last = re.search(r'[^http://www.reddit.com/r/AskReddit/comments/].{5}',links[-1]).group()
            time.sleep(2)
        with open(FILENAME,'a') as csv:
            now = time.localtime()
            csv.write(str(now.tm_year) + ',' + str(now.tm_mon) + ',' + str(now.tm_mday) + ',' + str(now.tm_wday) + ',' + str(now.tm_hour) + ',' + str(now.tm_min) + ',' + str(comment_number) + '\n')
        #time.sleep(300)
        time.sleep(3600)

if __name__ == "__main__":
    os.chdir(RCDIR) 
    logging.basicConfig(filename = 'counter.log', level = logging.INFO, format = '%(asctime)s %(message)s')
    logging.info('Starting counter')
    logging.info('Directory = ' + RCDIR)
    count_comments()
    logging.info('Finished script')
else:
    logging.info('Script failed to initialize')