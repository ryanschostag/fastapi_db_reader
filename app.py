"""
This application is a sample API using the FastAPI framework. We are using the chinook database by default; however, you can change this for any database that is compatible with SQlite using config.py.
"""
from fastapi import FastAPI
import sqlite3
import config


my_app = FastAPI()


@my_app.get('/tables/{command}')
async def get_tables(command: str):
    """
    Returns the names of the tables in the database
    """
    query = "SELECT name FROM sqlite_master WHERE type='table';"
    if command == "all":
        conn = sqlite3.connect(config.db_path)
        cur = conn.cursor()
        table_names = [table[0] for table in cur.execute(query).fetchall() if table and 'sqlite' not in table[0]]
        conn.close()
    else:
        return {'error': 'Unsupported command received: %s' % command}
    return table_names


@my_app.get('/tables/info/{table}')
async def table_info(table: str):
    """
    Returns the field names in a table
    """
    conn = sqlite3.connect(config.db_path)
    cur = conn.cursor()
    results = cur.execute(f'PRAGMA table_info({table})').fetchall()
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
            return []

    conn = sqlite3.connect(config.db_path) 
    cur = conn.cursor()
    response = cur.execute(sqlite_query).fetchall()
    conn.close()
    return response


@my_app.get('/')
async def root():
    return {
              'message': 'Welcome to the chinook database',
              'apis': {
                         'tables': 'View the table names. Only accepts the "all" command (e.g. tables/all)',
                         'tables/info': 'View information about the table. For example, tables/info/my_table returns a list of lists containing field information about the my_table table',
                         'query': 'Send a SQL query to database, and receive a list of results. For example, /query/SELECT%20*%20FROM%20my_table returns a list of all of the rows in the my_table table. In web browsers, such as Firefox, spaces and other characters do not need to be escaped.'
                      }

           }

 
