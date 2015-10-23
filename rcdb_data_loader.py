"""
Python script to interface with a PostgresSQL database used to 
organize and analyze RC data.
"""

import psycopg2
# import postgresql
import re
import os
import glob
import math
import datetime
import utils

DATABASE = "rcdb"
USERNAME = "michaelcho"
PASSWORD = "rcpassword"
DATA_DIR = os.getenv('HOME') + "/Documents/RC/rc_static/"
CORPORA_DIR = DATA_DIR + "corpora/"
IGNORE_STR = ['/r/', '/u/', 'https//', 'http//', '?', '!', '[', ']',
                '^', '_', '+', '=', '\\', '/', '1', '2', '3', '4', 
                '5', '6', '7', '8' '9', '0', '\'', '\"' ]


def init_connection():
    return psycopg2.connect(
                database=DATABASE, 
                user=USERNAME, 
                password=PASSWORD)
 

#TODO: Figure out a way to implement this
# def create_table(name, cols, num_cols):
#     if type(cols) != dict:
#         raise TypeError("cols must be dictionary colname:type")
#     createtablestr = "CREATE TABLE %s ("
#     strvals = name + ","

def create_raw_token_count():
    connection = init_connection()
    cursor = connection.cursor()
    command = "DROP TABLE IF EXISTS rawTokenCount"
    cursor.execute(command)
    command = "CREATE TABLE rawTokenCount (\
                            day date, \
                            token varchar(512), \
                            count int \
                        );"
    cursor.execute(command)
    utils.commit_and_close(connection)

def create_day_total():
    connection = init_connection()
    cursor = connection.cursor()
    command = "DROP TABLE IF EXISTS dayTotal"
    cursor.execute(command)
    command = "CREATE TABLE dayTotal (\
                            day date PRIMARY KEY, \
                            total int \
                        );"
    cursor.execute(command)
    utils.commit_and_close(connection)


def load_data(which_grams):
    connection = init_connection()
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
            if len(token) > 512:
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
                command = "UPDATE rawTokenCount  \
                            SET count = count + {0} \
                            WHERE day = {1}, token = {2};".format(token_count, psqlday, token)
                cursor.execute(command)                    
            else:
                body.add(token + date)
                command = "INSERT INTO rawTokenCount \
                                (day, token, count) \
                                VALUES( {0}, \'{1}\', {2} ); \
                                ".format(psqlday, token, token_count)
                cursor.execute(command)                    
    command = "INSERT INTO dayTotal VALUES( \
                {0}, {1});".format(psqlday, total_tokens)
    cursor.execute(command)


if __name__ == '__main__':
    create_raw_token_count()
    create_day_total()
    which_grams=['1']
    load_data(which_grams)


        