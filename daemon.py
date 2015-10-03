#!/usr/bin/env python

"""

"""

__author__ = "Dillon Niederhut"
__version__ = "0.1.0"
__email__ = "dillon.niederhut@gmail.com"

from pymongo import MongoClient
import redicorpus as rc

mongo = MongoClient()
logging.basicConfig(filename = RCDIR + '/redicorpus.log', level = logging.INFO, format = '%(asctime)s %(message)s')

if __name__ == '__main__':
    logging.info("Daemon respawned")
    for database in mongo.database_names():
        for collection in database.collection_names():
            if collection.comments.findOne({'counted':0}):
                for document in collection.comments.find({'counted':0}):
                    #do rc.body.build 
                    collection.comments.update_one({'_id':document['_id']},
                                                    '$inc' : {'counted' : 1})

    logging.ingo("Daemon entered {} comments".format(i))
    mongo.close()