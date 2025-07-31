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
from fastapi import FastAPI, Body, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, MetaData, Table, select, and_, text
from sqlalchemy.exc import SQLAlchemyError
import settings
import models


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
    connection_string = db_config.get('connection_string').strip()

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
    docs_filename = api_config.get('docs_html_filename')
    docs_path = current_directory / docs_filename
    default_docs_body = api_config.get('default_docs_body')

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
            self.connection_string = self.db_config.get('connection_string').strip()

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
            self.docs_filename = self.api_config.get('docs_html_filename')
            self.docs_path = self.current_directory / self.docs_filename
            self.default_docs_body = self.api_config.get('default_docs_body')


class Setup(Config):
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
        self.logger.info('FastAPI App Setup Complete')

        # Setup database engine
        try:
            self.engine = create_engine(self.connection_string)
        except SQLAlchemyError as e:
            self.logger.error(f"Error creating SQLAlchemy engine: {e}")
            raise RuntimeError(f"Database connection failed: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error creating engine: {e}")
            raise RuntimeError(f"Unexpected error: {e}")

        # Setup documentation
        if not Path(self.docs_path).is_file():
            self.logger.warning(f'No Documentation File for API at: {self.docs_path}')
            self.docs_body = self.default_docs_body
        else:
            with open(self.docs_path, 'r') as file:
                self.docs_body = file.read()
                self.logger.info(f'Created documentation body from file: {self.docs_path}')


class DBInterface(Setup):
    """
    This class provides an interface to interact with the database.
    It allows querying tables, getting table information, and executing SQL queries.
    """
    def __init__(self, config_file: Optional[Union[str, Path]] = None):
        super().__init__(config_file)
        self.metadata = MetaData()
        self.metadata.reflect(bind=self.engine)
        self.logger.info('Database Interface Initialized')

    def get_tables(self) -> dict:
        """
        Returns a list of table names in the database.
        """
        results = {'table_names': []}
        if self.connection_string.startswith('sqlite'):
            try:
                with self.engine.connect() as conn:
                    query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
                    query = text(query)
                    data = conn.execute(query).fetchall()
                    table_names = [row[0] for row in data if row and 'sqlite' not in row[0]]
                    results['table_names'] = table_names
                    self.logger.info(f'Found {len(table_names)} tables in the {self.db_name} database')
            except SQLAlchemyError as e:
                self.logger.error(f"SQLAlchemy error: {e}")
                results['error'] = str(e)
            except Exception as e:
                self.logger.error(f'Unknown error: {e}')
                results['error'] = str(e)
        else:
            results['error'] = 'This endpoint supports only SQLite databases'
            self.logger.error('This endpoint supports only SQLite databases')
        return results

    def table_info(self, table : str) -> dict:
        """
        Returns information about the tables in the database.
        """
        results = {}
        if self.connection_string.startswith('sqlite'):
            try:
                # Use SQLAlchemy to reflect the table info
                with self.engine.connect() as conn:
                    pragma_stmt = text(f'PRAGMA table_info({table})')
                    cursor_results = conn.execute(pragma_stmt).fetchall()
                    results[table] = {row[1]: row[2] for row in cursor_results}
                    self.logger.info(f'Found {len(cursor_results)} fields in the {table} table')
            except SQLAlchemyError as e:
                self.logger.error(f"SQLAlchemy error: {e}")
                results['error'] = str(e)
        else:
            results['error'] = 'This endpoint supports for SQLite databases'
        return results

    def query(self, metadata : MetaData, request: models.QueryRequest = Body(...)) -> dict:
        """
        Executes a SQL query against the database.
        The query is expected to be in the form of a JSON object.
        
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
        table_name = request.table
        fields = request.fields
        filters = request.filters or {}

        try:
            # Reflect the table
            table = Table(table_name, metadata, autoload_with=self.engine)
            # Build the select statement
            if fields:
                columns = [table.c[field] for field in fields]
                stmt = select(columns)
            else:
                stmt = select(table)  # Select all columns            

            # Build WHERE clause
            if filters:
                conditions = [table.c[key] == value for key, value in filters.items()]
                stmt = stmt.where(and_(*conditions)) 

            with self.engine.connect() as conn:
                response = conn.execute(stmt).fetchall()
                result['query'] = str(stmt)
                result['result'] = [dict(row._mapping) for row in response]
                self.logger.info(f'Found {len(result["result"])} records with query \"{stmt}\"')
        except SQLAlchemyError as e:
            self.logger.error(f"SQLAlchemy error: {e}")
            result['error'] = str(e)
        except Exception as e:
            self.logger.error(f"General error: {e}")
            result['error'] = str(e)
        return result

def create_app(interface : DBInterface) -> FastAPI:
    """
    Create and configure the FastAPI application that handles database queries
    to the configured database. 

    When the app is run, it will provide endpoints to:
    - /tables/: List all tables in the database
    - /tables/info/: Get information about a specific table
    - /query/: Execute a SQL query against the database
    - /: Provide a welcome message with API documentation
    """
    app = FastAPI()
    metadata = MetaData()
    metadata.reflect(bind=interface.engine)

    @app.get('/tables/')
    async def get_tables():
        results = interface.get_tables()
        if 'error' in results:
            raise HTTPException(status_code=400, detail=results['error'])
        return results

    @app.get('/tables/info/{table}')
    async def table_info(table: str):
        results = interface.table_info(table)
        if 'error' in results:
            raise HTTPException(status_code=400, detail=results['error'])
        return results

    @app.post('/query/')
    async def query(request: models.QueryRequest = Body(...)):
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
        result = interface.query(metadata, request)
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])
        return result

    @app.get('/')
    async def root():
        """
        Returns a welcome message and API documentation in HTML format.
        """
        response = HTMLResponse(content=interface.docs_body, status_code=200)
        return response

    return app


if __name__ == '__main__':
    import uvicorn

    interface = DBInterface()
    app = create_app(interface)
    uvicorn.run(app, host=interface.hostname, port=interface.port)
