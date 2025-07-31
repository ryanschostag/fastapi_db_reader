"""
This application is a sample API using the FastAPI framework. We tested this using the chinook database by default; however, you can change this for any database that is compatible with SQlite using config.py.
"""
import os
import sys
from fastapi import FastAPI, Body, HTTPException
from fastapi.responses import HTMLResponse
import models
from db_interface import DBInterface


def is_uvicorn():
    """
    Check if the application is running under Uvicorn.
    """
    potential_uvicorn = sys.argv[0] if sys.argv else ''
    if not potential_uvicorn:
        return False

    if (
        os.path.dirname(potential_uvicorn).endswith('uvicorn')
    ):
        return True
    else:
        return False


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

    @app.get('/tables/', tags=['DCL'])
    async def get_tables():
        results = interface.get_tables()
        if 'error' in results:
            raise HTTPException(status_code=400, detail=results['error'])
        return results

    @app.get('/tables/info/{table}', tags=['DCL'])
    async def table_info(table: str):
        results = interface.table_info(table)
        if 'error' in results:
            raise HTTPException(status_code=400, detail=results['error'])
        return results

    @app.post('/query/', tags=['DML'])
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
        result = interface.query(interface.metadata, request)
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])
        return result

    @app.get('/', tags=['Welcome'])
    async def root():
        """
        Returns a welcome message and API documentation in HTML format.
        """
        response = HTMLResponse(content=interface.docs_body, status_code=200)
        return response

    @app.get("/healthcheck", tags=["Health"])
    def health_check():
        return {"status": "ok"}

    return app


if is_uvicorn():
    interface = DBInterface()
    app = create_app(interface)


if __name__ == '__main__':
    import uvicorn

    interface = DBInterface()
    app = create_app(interface)
    uvicorn.run(app, host=interface.hostname, port=interface.port)
