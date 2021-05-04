"""
This application is a sample API using the FastAPI framework. We tested this using the chinook database by default; however, you can change this for any database that is compatible with SQlite using config.py.
"""
from fastapi import FastAPI
import sqlite3
import config
import logging

# setup logging
logging.config.fileConfig('logging.conf', disable_existing_loggers=False, defaults={'logfilename': config.log_file_path})
logger = logging.getLogger()
logger.info('FastAPI Sample Program Initiated')

# instantiate the API
my_app = FastAPI()
    

@my_app.get('/tables/{command}')
async def get_tables(command: str):
    """
    Returns the names of the tables in the database as a dictionary
    """
    query = "SELECT name FROM sqlite_master WHERE type='table';"
    results = {'table_names': []}
    if command == "all":
        conn = sqlite3.connect(config.db_path)
        cur = conn.cursor()
        table_names = [table[0] for table in cur.execute(query).fetchall() if table and 'sqlite' not in table[0]]
        results['table_names'] = table_names
        conn.close()
    else:
        return {'error': f'Unsupported command received: {command}'}
    
    logger.info(f'Found {len(results["table_names"])} tables in the {config.db_name} database')
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
    cursor_results = cur.execute(f'PRAGMA table_info({table})').fetchall()
    results[table] = {field[1]: field[2] for field in cursor_results}
    conn.close()
    return results


@my_app.get('/query/{sqlite_query}')
async def query(sqlite_query: str):
    """
    Send a query to the chinook database

    """
    result = {}
    # ensure no write statements are in query
    test_query = sqlite_query.upper()
    for prohibited_statement in config.prohibited_query_keywords:
        if prohibited_statement in test_query:
            return {}

    conn = sqlite3.connect(config.db_path) 
    cur = conn.cursor()
    response = cur.execute(sqlite_query).fetchall()
    conn.close()
    result['query'] = sqlite_query
    result['result'] = response
    logger.info(f'Found {len(response)} records with query "{sqlite_query}"')
    return result


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

 
