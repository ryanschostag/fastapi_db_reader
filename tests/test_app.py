"""
Test module for the app.py FastAPI application

These are integration tests for the functions in the app.py module 

Requirements: 

uvicorn must be running the app:my_app FastAPI instance 
This works with the chinook database. 
"""
import multiprocessing
import time
from typing import Generator
import requests
import pytest
import uvicorn
import app
import app_test_vars as test_vars


DB_INTERFACE = app.DBInterface()
HOST = DB_INTERFACE.hostname
PORT = DB_INTERFACE.port
BASE_URL = f"http://{HOST}:{PORT}"
HEALTHCHECK_PATH = "/healthcheck"  # Replace with your real health check endpoint if available


def run_uvicorn() -> None:
    db_interface_app = app.create_app(DB_INTERFACE)
    uvicorn.run(db_interface_app, host=HOST, port=PORT, log_level="info")


def wait_for_server(url: str, timeout: float = 30.0) -> None:
    start = time.time()
    while True:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return
        except requests.exceptions.ConnectionError:
            pass

        if time.time() - start > timeout:
            raise TimeoutError(f"Server did not become ready within {timeout} seconds.")
        time.sleep(0.25)


@pytest.fixture(scope="session", autouse=True)
def start_server() -> Generator:
    """
    Fixture to start the FastAPI server before running tests.
    This fixture runs the server in a separate process and waits for it to become ready.
    """
    proc = multiprocessing.Process(target=run_uvicorn, daemon=True)
    proc.start()

    try:
        wait_for_server(f"{BASE_URL}{HEALTHCHECK_PATH}")
    except TimeoutError as e:
        proc.terminate()
        proc.join()
        raise RuntimeError(str(e))

    yield

    proc.terminate()
    proc.join()


@pytest.fixture
def api_url() -> None:
    return BASE_URL


def test_health_check(api_url: str) -> None:
    """
    Test the health check endpoint to ensure the server is running.
    """
    response = requests.get(f"{api_url}{HEALTHCHECK_PATH}")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_tables(api_url: str) -> None:
    """
    Test the /tables/ endpoint to retrieve the list of tables.
    """
    response = requests.get(f"{api_url}/tables/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert data == {
        "table_names": [
            "Album",
            "Artist",
            "Customer",
            "Employee",
            "Genre",
            "Invoice",
            "InvoiceLine",
            "MediaType",
            "Playlist",
            "PlaylistTrack",
            "Track"
        ]
    }


@pytest.mark.parametrize('table_name, expected_fields', [
    ('Album', test_vars.album_fields),
    ('Artist', test_vars.artist_fields),
    ('Customer', test_vars.customer_fields),
    ('Employee', test_vars.employee_fields),
    ('Genre', test_vars.genre_fields),
    ('Invoice', test_vars.invoice_fields),
    ('InvoiceLine', test_vars.invoice_line_fields),
    ('MediaType', test_vars.media_type_fields),
    ('Playlist', test_vars.playlist_fields),
    ('PlaylistTrack', test_vars.playlist_track_fields),
    ('Track', test_vars.track_fields)
])
def test_table_info(api_url: str, table_name : str, expected_fields : dict) -> None:
    """
    Test the /tables/info/{table} endpoint to retrieve information about a specific table.
    """
    response = requests.get(f"{api_url}/tables/info/{table_name}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert list(data[table_name].keys()) == expected_fields



@pytest.mark.parametrize('request_body, expected_status_code, expected_sql_query, expected_query_result', [
    # payload with "table", "filters", and "fields"
    (test_vars.album_request, 200, test_vars.album_expected_sql_query, test_vars.album_query_result),  
    # payload without "filters" but with "table" and "fields"
    (test_vars.artist_request, 200, test_vars.artist_expected_sql_query, test_vars.artist_query_result),
    # no "table" in query, but "filters" and "fields"
    (test_vars.no_table_query, 422, None, test_vars.no_table_detail)
])
def test_query(api_url: str, request_body, expected_status_code, expected_sql_query, expected_query_result) -> None:
    """
    Test the /query/ endpoint to execute a SQL query against the database.
    """
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(f"{api_url}/query/", headers=headers, json=request_body)  
    assert response.status_code == expected_status_code
    data = response.json()
    assert isinstance(data, dict)
    if expected_status_code == 200:
        assert data['query'] == expected_sql_query
        assert data['result'] == expected_query_result
    else:
        assert data['detail'] == expected_query_result
