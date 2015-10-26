import time
import psycopg2

DATABASE = "rcdb"
USERNAME = "michaelcho"
PASSWORD = "rcpassword"
MAX_TOKEN_LENGTH = 100

# Takes a string formatted "%Y_%m_%d" and returns a psql date
# object created via psycopg2.Date(year, month, day) 
def format_timestr(timestr):
    date_pieces = timestr.split("_")
    return psycopg2.Date(int(date_pieces[0]), int(date_pieces[1]), int(date_pieces[2]))


def get_count(corpus, token):
    count = corpus.get(token)
    if not isinstance(count, int):
        raise TypeError("Corpus must be a dictionary of form token:count")
    return count

def has_token(corpus, token):
    return token in corpus

def commit_and_close(connection):
    connection.commit()
    connection.close()

def init_connection():
    return psycopg2.connect(
                database=DATABASE, 
                user=USERNAME, 
                password=PASSWORD)