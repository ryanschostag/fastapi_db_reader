"""
This application is a sample API using the FastAPI framework. We tested this using the chinook database by default; however, you can change this for any database that is compatible with SQlite using config.py.
"""
import json
from typing import Optional, Union
from pathlib import Path
import logging
import logging.config
import sqlite3
import configparser
from fastapi import FastAPI
import settings


class Config:
    """
    Configuration class for app
    """
    current_directory = Path(__file__).parent.absolute()
    default_config_filepath = current_directory / settings.default_config_filename
    config = configparser.ConfigParser()
    config.read(default_config_filepath)

    # database configuration
    db_config = config['database']
    db_path = Path(db_config.get('db_directory').strip()) / db_config.get('db_filename').strip()
    db_name = db_config.get('db_name').strip()
    prohibited_query_keywords = [
        item.strip() for item in db_config.get('prohibited_query_keywords').split(',') \
        if item.strip()
    ]

    # logging configuration
    logging_config = config['logging']
    logger_name = logging_config.get('fastapi_app')
    log_directory = current_directory / Path(logging_config.get('log_directory'))
    log_filepath =  str(log_directory / logging_config.get('log_filename'))
    log_config_filename = logging_config.get('log_config_filename')
    log_filepath =  str(log_directory / logging_config.get('log_filename').strip()).replace("\\", "/")
    log_config_file = str(current_directory / logging_config.get('log_config_filename').strip())
    
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
            isinstance(config_file, (str, Path))
            and Path.is_file(config_file)
        ):
            self.config = configparser.ConfigParser()
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
            self.log_directory = self.current_directory / self.logging_config.get('log_directory').strip()
            self.log_filepath =  str(self.log_directory / self.logging_config.get('log_filename').strip()).replace("\\", "/")
            self.log_config_file = str(self.current_directory / self.logging_config.get('log_config_filename').strip())

            # API configuration
            self.api_config = self.config['api']
            self.hostname = self.api_config.get('hostname')
            self.port = self.api_config.getint('port')


class FastAPIApp(Config):
    """
    The FastAPI application: 
    This accepts SQL input, validates it against prohibited keywords,
    queries the configured database and returns the result
    """
    def __init__(self, config_file : Optional[Union[str, Path]] = None):
        """
        Constructor for the FastAPI app
        """
        super().__init__(config_file)

        # Set up logging
        if self.log_directory.is_dir() is False:
            self.log_directory.mkdir(parents=True, exist_ok=True)

        logging.config.fileConfig(
            self.log_config_file,
            disable_existing_loggers=True,
            defaults={'logfilename': self.log_filepath}
        )
        self.logger = logging.getLogger()

        # Set up database: create and load Chinook data if missing or empty
        db_needs_init = False
        if not self.db_path.is_file():
            db_needs_init = True
        else:
            # Check if the database is empty (no tables)
            try:
                conn = sqlite3.connect(self.db_path)
                cur = conn.cursor()
                cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
                if not cur.fetchall():
                    db_needs_init = True
            except Exception as e:
                self.logger.exception(f"Error checking database: {e}")
                db_needs_init = True
            finally:
                conn.close()

        if db_needs_init:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(self.db_path)
            try:
                if self.db_path.is_file() is False:
                    conn = sqlite3.connect(self.db_path)
                    conn.close()
                    self.logger.error(f'Database file {self.db_path} does not exist. Creating a new and empty database.')
            except Exception as e:
                self.logger.exception(f"Error loading Chinook data: {e}")

        self.logger.info('FastAPI App Setup Complete')


def create_app(config : FastAPIApp) -> FastAPI:
    """
    Create and configure the FastAPI application that handles database queries
    to the configured database. 

    When the app is run, it will provide endpoints to:
    - List all tables in the database
    - Get information about a specific table
    - Execute a SQL query against the database
    - Provide a welcome message with API documentation
    """
    app = FastAPI()
    logger = config.logger

    @app.get('/tables/')
    async def get_tables():
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
        results = {'table_names': []}
        try:
            conn = sqlite3.connect(config.db_path)
            cur = conn.cursor()
            data = cur.execute(query).fetchall()
            table_names = [table[0] for table in data if table and 'sqlite' not in table[0]]
            results['table_names'] = table_names
            conn.close()
            logger.info(f'Found {len(results["table_names"])} tables in the {config.db_name} database')
        except sqlite3.Error as e:
            logger.error(f"SQLite error: {e}")
            results['error'] = str(e)
        return results

    @app.get('/tables/info/{table}')
    async def table_info(table: str, results=None):
        results = {} if results is None else results
        try:
            conn = sqlite3.connect(config.db_path)
            cur = conn.cursor()
            cursor_results = cur.execute(f'PRAGMA table_info({table})').fetchall()
            results[table] = {field[1]: field[2] for field in cursor_results}
            conn.close()
            logger.info(f'Found {len(cursor_results)} fields in the {table} table')
        except sqlite3.Error as e:
            logger.error(f"SQLite error: {e}")
            results['error'] = str(e)   
        return results

    @app.get('/query/{data}')
    async def query(data: str):
        """
        Accepts JSON as input, converts it to a SQL query, and returns the results.

        For example:

            {
                "table": "Album",
                "fields": ["AlbumId", "Title"],
                "filters": {
                    "ArtistId": 1
                }
            }
        """
        result = {}
        try:
            json_input = json.loads(data)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error (input={data}) (error={e})")

        table = json_input.get('table')
        fields = json_input.get('fields', '*')
        fields = ','.join(field_name.strip() for field_name in fields) if isinstance(fields, list) else fields
        filters = json_input.get('filters', {})
        if not filters:
            sql_query = f'SELECT {fields} FROM {table}'
        else:
            filters = 'WHERE 1=1 AND '.join(
                f"{key} = '{value}'" if isinstance(value, str) else f"{key} = {value}"
                for key, value in filters.items()
            )
            sql_query = f'SELECT {fields} FROM {table} WHERE {filters}'

        try:
            conn = sqlite3.connect(config.db_path)
            cur = conn.cursor()
            response = cur.execute(sql_query).fetchall()
            conn.close()
            result['query'] = sql_query
            result['result'] = response
            logger.info(f'Found {len(response)} records with query "{sql_query}"')
        except sqlite3.Error as e:
            logger.error(f"SQLite error: {e}")
            result['error'] = str(e)
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
