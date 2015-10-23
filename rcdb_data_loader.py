"""
Python script to interface with a PostgresSQL database used to 
organize and analyze RC data.
"""

import postgresql
import re
import os
import glob
import math
import datetime

DATABASE = "rcdb"
USERNAME = "michaelcho"
PASSWORD = "rcpassword"
DATA_DIR = os.getenv('HOME') + "/Documents/RC/rc_static/"
CORPORA_DIR = DATA_DIR + "corpora/"
IGNORE_STR = ['/r/', '/u/', 'https//', 'http//', '?', '!', '[', ']', '^', '_', '+', '=', '\\', '/', '1', '2', '3', '4', '5', '6', '7', '8' '9', '0']

db_connection = psycopg.connect(
                    database=DATABASE, 
                    username=USERNAME, 
                    password=PASSWORD)

cursor = db_connection.cursor()


