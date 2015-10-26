"""
Python functions to load initial data to a PostgreSQL database.
Imports data from a CORPORA dir that is organized with date
subdirectories each containing files with dictionaries of gram
to count.

When run as main, this will delete existing rawtokencount and daytotal
data, replacing it with new data imported from the CORPORA.


TODO: 
    Figure out a way to implement generic create_table function.
    Create functions for updating rcdb with new data
    load_data:
        add error checking to make sure table exists, and updates properly

"""

import psycopg2
import re
import os
import glob
import math
import datetime
import utils


DATA_DIR = os.getenv('HOME') + "/Documents/RC/rc_static/"
CORPORA_DIR = DATA_DIR + "corpora/"
IGNORE_STR = set(['/r/', '/u/', 'https//', 'http//', '?', '!', '[', ']',
                '^', '_', '+', '=', '\\', '/', '1', '2', '3', '4', 
                '5', '6', '7', '8' '9', '0', '\'', '\"' ])

def create_rawtokens():
    connection = utils.init_connection()
    cursor = connection.cursor()
    command = "DROP TABLE IF EXISTS rawtokens;"
    cursor.execute(command)
    command = "CREATE TABLE rawtokens (\
                            day date, \
                            token varchar({0}), \
                            daytokcount int, \
                            PRIMARY KEY (day, token) \
                        );".format(utils.MAX_TOKEN_LENGTH)
    cursor.execute(command)
    utils.commit_and_close(connection)

def create_daytotal():
    connection = utils.init_connection()
    cursor = connection.cursor()
    command = "DROP TABLE IF EXISTS daytotal;"
    cursor.execute(command)
    command = "CREATE TABLE daytotal (\
                            day date PRIMARY KEY, \
                            totaltokens int \
                        );"
    cursor.execute(command)
    utils.commit_and_close(connection)


def load_data(which_grams):
    connection = utils.init_connection()
    cursor = connection.cursor()
    # ADD ERROR CHECKING TO MAKE SURE TABLE DOESN'T ALREADY EXIST
    # OR TO MAKE SURE THIS IS UPDATING PROPERLY
    for gram_num in which_grams:
        days = glob.glob(CORPORA_DIR + '*/')
        for day in days:
            date = day[len(CORPORA_DIR):]
            print('Processing ' + date + 'gram' + gram_num)    
            gram_f = day + gram_num + 'gram.txt'    
            process_day(gram_f, gram_num, date[:len(date) - 1], cursor)
    utils.commit_and_close(connection)

""" 
Adds a day's worth of data from CORPORA to the rcdb rawTokenCount
table.  Assumes table has been made. Date is a string of format YYYY_MM_DD.

Ignores tokens:
    -Containing most punctuation (allows hyphens)
    -Of length greater than MAX_TOKEN_LENGTH characters

"""
def process_day(day_file, gram_n, date, cursor):
    import ast
    body = set()
    total_tokens = 0
    with open(day_file, 'r') as f:
        corpus = ast.literal_eval(f.read())
        if not isinstance(corpus, dict):
            raise TypeError("day_file must contain a dictionary.")
        for token in corpus:
            skip = False
            if len(token) > utils.MAX_TOKEN_LENGTH:
                continue;
            for ignore in IGNORE_STR:
                if ignore in token:
                    skip = True
                    break
            if skip:
                continue
            token_count = utils.get_count(corpus, token)
            total_tokens += token_count
            psqlday = utils.format_timestr(date)
            if token + date in body:
                command = "UPDATE rawtokens  \
                            SET daytokcount = daytokcount + {0} \
                            WHERE day = {1}, token = {2};".format(token_count, 
                                                            psqlday, token)
                cursor.execute(command)                    
            else:
                body.add(token + date)
                command = "INSERT INTO rawtokens \
                                (day, token, daytokcount) \
                                VALUES( {0}, \'{1}\', {2} ); \
                                ".format(psqlday, token, token_count)
                cursor.execute(command)                    
    command = "INSERT INTO dayTotal VALUES( \
                {0}, {1});".format(psqlday, total_tokens)
    cursor.execute(command)


if __name__ == '__main__':
    confirm_strs = set(["yes", "y", "Y", "Yes"])
    print("This will clear all current rcdb data if it exists. Continue? (y/n)")
    confirm = input(">>>")
    if confirm not in confirm_strs:
        print("Exiting.")
    attempt = input("Password: ")
    if attempt != utils.PASSWORD:
        print("Incorrect password. Exiting.")
    create_rawtokens()
    create_daytotal()
    which_grams=['1']
    load_data(which_grams)
        

        