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
    for collection in ###:
        if collection.comments.findOne():
            for document in collection.commends.find():
                
    logging.ingo("Daemon entered {} comments".format(i))
    mongo.close()
