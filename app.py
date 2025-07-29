"""
This application is a sample API using the FastAPI framework. We tested this using the chinook database by default; however, you can change this for any database that is compatible with SQlite using config.py.
"""
from typing import Optional, Union
from pathlib import Path
import logging
import logging.config
import sqlite3
import configparser
from fastapi import FastAPI


DEFAULT_CONFIG_FILE = 'config.ini'


class Config:
    """
    Configuration class for app
    """
    current_directory = Path(__file__).parent
    default_config_filepath = current_directory / DEFAULT_CONFIG_FILE
    config = configparser.ConfigParser()
    config.read(default_config_filepath)

    # database configuration
    db_config = config['database']
    db_path = Path(db_config.get('db_directory')) / db_config.get('db_filename')
    db_name = db_config.get('db_name')
    prohibited_query_keywords = [
        item for item in db_config.get('prohibited_query_keywords').split(',') \
        if item.strip()
    ]

    # logging configuration
    logging_config = config['logging']
    logger_name = logging_config.get('fastapi_app')
    log_directory = current_directory / Path(logging_config.get('log_directory'))
    log_filepath =  log_directory / logging_config.get('log_filename')
    log_config_filename = logging_config.get('log_config_filename')

    # API configuration
    api_config = config['api']
    hostname = api_config.get('hostname')
    port = api_config.getint('port')

    def __init__(self, config_file : Optional[Union[str, Path]] = None):
        """
        Constructor for Config class that can accept and alternative
        configuration file than DEFAULT_CONFIG_FILE
        """
        
        if (
            config_file is not None
            and Path.is_file(config_file)
        ):
            if isinstance(config_file, str):
                config_file = Path(config_file)

            self.config.read(config_file)

        # database configuration
        self.db_config = self.config['database']
        self.db_path = Path(self.db_config.get('db_directory')) / self.db_config.get('db_filename')
        self.db_name = self.db_config.get('db_name')
        self.prohibited_query_keywords = [
            item for item in self.db_config.get('prohibited_query_keywords').split(',') \
            if item.strip()
        ]

        # logging configuration
        self.logging_config = self.config['logging']
        self.logger_name = self.logging_config.get('fastapi_app')
        self.log_directory = self.current_directory / Path(self.logging_config.get('log_directory'))
        self.log_filepath =  self.log_directory / self.logging_config.get('log_filename')
        self.log_config_file = self.current_directory / self.logging_config.get('log_config_filename')

        # API configuration
        self.api_config = self.config['api']
        self.hostname = self.api_config.get('hostname')
        self.port = self.api_config.getint('port')


class FastAPIApp(Config):
    """
    The FastAPI application: 
    This accepts a JSON input that is converted to a SQL query, 
    queries the configured database and returns the result
    """
    def __init__(self, config_file : Optional[Union[str, Path]] = None):
        """
        Constructor for the FastAPI app
        """
        super().__init__(config_file)

        if self.log_directory.is_dir() is False:
            self.log_directory.mkdir(parents=True, exist_ok=True)


def create_app(config : FastAPIApp) -> FastAPI:
    app = FastAPI()

    @app.get('/tables/{command}')
    async def get_tables(command: str):
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
        config.logger.info(f'Found {len(results["table_names"])} tables in the {config.db_name} database')
        return results

    @app.get('/tables/info/{table}')
    async def table_info(table: str, results=None):
        results = {} if results is None else results
        conn = sqlite3.connect(config.db_path)
        cur = conn.cursor()
        cursor_results = cur.execute(f'PRAGMA table_info({table})').fetchall()
        results[table] = {field[1]: field[2] for field in cursor_results}
        conn.close()
        return results

    @app.get('/query/{sqlite_query}')
    async def query(sqlite_query: str):
        result = {}
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
        config.logger.info(f'Found {len(response)} records with query "{sqlite_query}"')
        return result

    @app.get('/')
    async def root():
        return {
            'message': f'Welcome to the {config.db_name} database',
            'apis': {
                'tables': 'View the table names. Only accepts the "all" command (e.g. tables/all)',
                'tables/info': 'View information about the table. For example, tables/info/my_table returns a list of lists containing field information about the my_table table',
                'query': 'Send a SQL query to database, and receive a list of results. For example, /query/SELECT%20*%20FROM%20my_table returns a list of all of the rows in the my_table table. In web browsers, such as Firefox, spaces and other characters do not need to be escaped.'
            }
        }

    return app


if __name__ == '__main__':
    import uvicorn

    config = FastAPIApp()
    app = create_app(config)
    uvicorn.run(app, host=config.hostname, port=config.port)
