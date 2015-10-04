#!/usr/bin/env python

"""

"""

from pymongo import MongoClient
from redicorpus.celery import app
import redicorpus.redicorpus as rc

logging.basicConfig(filename = RCDIR + '/redicorpus.log', level = logging.INFO, format = '%(asctime)s %(message)s')

@app.task
def counter():
    for database in mongo.database_names():
        for collection in database.collection_names():
            if collection.comments.findOne({'counted':0}):
                i = 0
                for document in collection.comments.find({'counted':0}):
                    #r = rc.comment(document).count()
                    if r:
                        i += 1
                        collection.comments.update_one({'_id':document['_id']},
                                                    '$inc' : {'counted' : 1})
