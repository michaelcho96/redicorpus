"""
Python functions to analyze data already loaded to the rawtokencount
and daytotal tables in the rcdb.

TODO: 
    

"""
import psycopg2
import re
import os
import glob
import math
import datetime
import utils



"""
Deletes table if exists!
"""

def create_dailystats():
    connection = utils.init_connection()
    cursor = connection.cursor()
    query = "DROP TABLE IF EXISTS dailystats;"
    cursor.execute(query)
    query = "CREATE TABLE tokentotal (\
                            day date, \
                            token varchar({0}), \
                            rank int, \
                            proportion decimal, \
                            PRIMARY KEY (day, token) \
                        );".format(utils.MAX_TOKEN_LENGTH)
    cursor.execute(query)
    utils.commit_and_close(connection)

def fill_dailystats():
    connection = utils.init_connection()
    cursor = connection.cursor()
    query = "CREATE TABLE dailystats as \
            SELECT raw.day as day, \
            raw.token as token, \
            daytokcount/totaltokens as proportion \
            FROM rawTokenCount as raw, daytotal as daytotal \
            WHERE rawtoken.token = daytotal.token;"
    cursor.execute(query)
    utils.commit_and_close(connection)


if __name__  =='__main__':
    create_dailystats()
    fill_dailystats()




