#!/usr/bin/env python

import os
import pymongo

RCDIR = os.path.abspath(os.path.dirname(__file__))
mongo = pymongo.MongoClient()
