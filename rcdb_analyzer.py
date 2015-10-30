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





# def create_dailystats():
#     connection = utils.init_connection()
#     cursor = connection.cursor()
#     query = "DROP TABLE IF EXISTS dailystats;"
#     cursor.execute(query)
#     query = "CREATE TABLE dailystats (\
#                             day date, \
#                             token varchar({0}), \
#                             rank int, \
#                             proportion decimal, \
#                             PRIMARY KEY (day, token) \
#                         );".format(utils.MAX_TOKEN_LENGTH)
#     cursor.execute(query)
#     utils.commit_and_close(connection)

"""
Deletes table if exists!
"""
def create_and_fill_dailystats():
    connection = utils.init_connection()
    cursor = connection.cursor()
    query = "DROP TABLE IF EXISTS dailystats;"
    cursor.execute(query)
    query = "CREATE TABLE dailystats as \
            SELECT raw.day as day, \
            raw.token as token, \
            daytokcount::float/totaltokens as  proportion \
            FROM rawtokens as raw, daytotal as daytotal \
            WHERE raw.day = daytotal.day;"
    cursor.execute(query)
    utils.commit_and_close(connection)

# takes ints for start and end date fields 
def find_proportion_change(start_y=2000, start_m=1, start_d=1, 
                            end_y=2100, end_m=12, end_d=31):
    connection = utils.init_connection()
    cursor = connection.cursor()
    start_date = datetime.date(start_y, start_m, start_d)
    end_date = datetime.date(end_y, end_m, end_d)
    query = "SELECT d.token as token,\
            d.day as day, \
            d.proportion as proportion \
            FROM dailystats as d\
            WHERE d.day::date BETWEEN {0} AND {1}\
            AND proportion = ((SELECT max(proportion) FROM dailystats WHERE ) - \
                        (SELECT min(proportion) FROM dailystats))\
            ;".format(start_date, end_date)
    cursor.execute(query)
    print(cursor.fetchall())




if __name__  =='__main__':
    # create_and_fill_dailystats()
    find_proportion_change(2014, 10, 31, 2014, 11, 10)




