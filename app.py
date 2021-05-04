"""
This application is a sample API using the FastAPI framework. We tested this using the chinook database by default; however, you can change this for any database that is compatible with SQlite using config.py.
"""
import json
from fastapi import FastAPI
import sqlite3
import config
import logging
from logging.handlers import RotatingFileHandler


# setup logging
logger = logging.getLogger(config.log_name)
log_handler = RotatingFileHandler(config.log_file_path)
log_formatter = logging.Formatter(config.log_format)
log_handler.setFormatter(log_formatter)
_ = [logger.removeHandler(handler) for handler in logger.handlers[:]]  # remove all old handlers
logger.addHandler(log_handler)

# instantiate the API
my_app = FastAPI()
    

@my_app.get('/tables/{command}')
async def get_tables(command: str):
    """
    Returns the names of the tables in the database as a dictionary
    """
    query = "SELECT name FROM sqlite_master WHERE type='table';"
    results = {'table_names': None}
    if command == "all":
        conn = sqlite3.connect(config.db_path)
        cur = conn.cursor()
        table_names = [table[0] for table in cur.execute(query).fetchall() if table and 'sqlite' not in table[0]]
        results['table_names'] = table_names
        conn.close()
    else:
        return {'error': f'Unsupported command received: {command}'}
    
    return results
    


@my_app.get('/tables/info/{table}')
async def table_info(table: str, results=None):
    """
    Returns the field names in a table as a dictionary. Optionally, pass in a 
    dictionary that will be updated with the key as the table name, and the 
    value as results 
    """
    results = {} if results is None else results
    conn = sqlite3.connect(config.db_path)
    cur = conn.cursor()
    results[table] = cur.execute(f'PRAGMA table_info({table})').fetchall()
    conn.close()
    return results


@my_app.get('/query/{sqlite_query}')
async def query(sqlite_query: str):
    """
    Send a query to the chinook database
    """
    # ensure no write statements are in query
    test_query = sqlite_query.upper()
    for prohibited_statement in config.prohibited_query_keywords:
        if prohibited_statement in test_query:
            return {}

    conn = sqlite3.connect(config.db_path) 
    cur = conn.cursor()
    response = cur.execute(sqlite_query).fetchall()
    conn.close()
    
    results = {field_info[1]: [field_info[2], field_info[3]] for field_info in response}
    return results


@my_app.get('/')
async def root():
    return {
              'message': f'Welcome to the {config.db_name} database',
              'apis': {
                         'tables': 'View the table names. Only accepts the "all" command (e.g. tables/all)',
                         'tables/info': 'View information about the table. For example, tables/info/my_table returns a list of lists containing field information about the my_table table',
                         'query': 'Send a SQL query to database, and receive a list of results. For example, /query/SELECT%20*%20FROM%20my_table returns a list of all of the rows in the my_table table. In web browsers, such as Firefox, spaces and other characters do not need to be escaped.'
                      }

           }

 
