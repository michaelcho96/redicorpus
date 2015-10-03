#!/usr/bin/env python
"""
Script to authenticate and scrape from reddit.com/r/AskReddit
"""
__author__ = "Dillon Niederhut"
__version__ = "0.1.0"
__email__ = "dillon.niederhut@gmail.com"

import requests
import datetime
import time
import os
import logging
import yaml
import json
import pymongo
import gzip
import re
import redicorpus as rc
from pymongo import MongoClient

mongo = MongoClient()
#RCDIR = os.environ.get('RCDIR')
RCDIR = '/Users/dillonniederhut/Dropbox/pydir/redicorpus'
os.chdir(RCDIR)
logging.basicConfig(filename = RCDIR + '/redicorpus.log', level = logging.INFO, format = '%(asctime)s %(message)s')

def authorize():
    """Oauth for reddit.com"""
    user_agent = 'linux:redicorpus:v.' + __version__ + ' (by /u/MonsieurDufayel)'
    with open('creds.yaml','r') as f:
        creds = yaml.load(f.read())
    client_auth = requests.auth.HTTPBasicAuth(creds['id'],creds['secret'])
    post_data = {'grant_type':'password', 'username':creds['username'], 'password':creds['password'], 'duration':'permanent'}
    r.status_code = 999
    while response.status_code != 200:
        response = requests.post('https://www.reddit.com/api/v1/access_token', auth=client_auth, data=post_data)
        time.sleep(30)
    return response.json()['token_type'] + ' ' + response.json()['access_token']

def get_listing(date, depth):
    """Retrieve top links from AskReddit"""
    logging.info("Fetching links")
    list_url = 'https://oauth.reddit.com/r/AskReddit/hot/'
    loop_var = ['']
    authorization = authorize()
    for i in depth:
        loop_var.append('?after=t3_')
    for i in loop_var:
        listing = json.loads(requests.get(list_url + i + id36[-1], headers = {
            'User-Agent' : user_agent, 'Authorization' : authorization}).content)
        time.sleep(1)
        for child in listing['data']['children']:
            mongo.askreddit.listings.insert({'_id' = child['data']['id']})

def get_page(id36, comment_id=None):
    """Retrieve comment page by id"""
    url = 'https://oauth.reddit.com/r/AskReddit/comments/' + id36 + '?limit=500&sort=random'
    authorization = authorize()
    if comment != None:
        url += '&comment=' + comment
    r.status_code = 999
    while r.status_code != 200
        r = requests.get(url,
            headers = {'User-Agent' : user_agent, 'Authorization' : authorization})
        if r.status_code == 200:
            return r.json()
        else:
            time.sleep(1)

def insert_comment(item):
    """Pull info out of raw data and insert to job collection"""
    item = item['data']
    document = rc.comment{
    _id : item['id'],
    source : 'askreddit'
    date : datetime.datetime.fromtimestamp(item['created_utc']),
    thread_id : re.search(r'[a-zA-Z0-9]+$',item['link_id']).group(),
    parent_id : re.search(r'[a-zA-Z0-9]+$',item['parent_id']).group(),
    child_id : []
    author : item['author'],
    polarity : item['controversiality'],
    strings : {'counted':0
        'data':word_tokenize(item['body'])},
    stems : {'counted':0,
        'data':[snowball.stem(token) for token in word_tokenize(item['body'])]
        },
    lemmas : {
        'counted':0
        'data':[wordnet.lemmatize(token) for token in word_tokenize(item['body'])]}
    }
    return mongo.reddit.comments.insert(document)

def traverse_comments(level):
    """Traverse comment hierarchies depth-first"""
    while len(level) > 0:
        item = level.pop()
        if item['kind'] == 't1':
            rc.comment.build(item)
            children = item['data']['replies']['data']['children']
            if len(children) > 0:
                insert_comment(children)
        elif item['kind'] == 'more':
            thread_id = list(collection.find(
                {'_id':re.search(r'[a-zA-Z0-9]+$',item['data']['parent_id'])},
                {'thread_id':True, '_id':False}
                ))[0]['thread_id']
            page = get_page(thread_id,comment_id=item['data']['id'])
            traverse_comments(page[1]['data']['children'])
        else:
            pass
    return True

def write_page(page):
    """Compress page and write page to file"""
    try:
        os.makedirs(RCDIR + "/raw/reddit/")
    except OSError:
        if not os.path.isdir(RCDIR + "/raw/reddit/"):
            raise
    id36 = page[0]['data']['children'][0]['id']
    with gzip.GzipFile(RCDIR + "/raw/reddit/" + str(id36) + ".json.gz", 'wb') as f:
        f.write(json.dumps(page))
    return True

if __name__ == "__main__":
    logging.info('Starting askreddit getter')
    get_listing(date = NOW, depth = 4)
    for document in mongo.askreddit.listing.find():
        page = get_page(id36)
        a = write_page(page)
        b = traverse_comments(page[1]['data']['children'])
        if a and b:
            mongo.askreddit.listing.remove(document)
    mongo.close()
    logging.info('Finished askreddit getter')
