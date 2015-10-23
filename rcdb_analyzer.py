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