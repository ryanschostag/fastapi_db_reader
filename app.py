import os
from fastapi import FastAPI
import sqlite3
import config


my_app = FastAPI()


@my_app.get('/tables/{command}')
async def get_tables(command: str):
    """
    Returns the names of the tables in the database
    """
    if command == "all":
        table_names = os.popen(f"sqlite3 {config.db_path} \"SELECT name FROM sqlite_master WHERE type='table';\"").read().split('\n')
        table_names = sorted([t for t in table_names if t and 'sqlite' not in t])
    else:
        return {'error': 'Unsupported command received: %s' % command}
    return table_names


@my_app.get('/tables/info/{table}')
async def table_info(table: str):
    """
    returns the field names in a table
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
    conn = sqlite3.connect(config.db_path) 
    cur = conn.cursor()
    response = cur.execute(sqlite_query).fetchall()
    conn.close()
    return response


@my_app.get('/')
async def root():
    return {'message': 'Welcome to the chinook database'}

 
