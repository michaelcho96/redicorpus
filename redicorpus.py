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
