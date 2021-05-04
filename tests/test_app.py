"""
Test module for the app.py FastAPI application

These are integration tests for the functions in the app.py module 

Requirements: 

uvicorn must be running the app:my_app FastAPI instance 
This works with the chinook database. 
"""
import ast
import json
import requests
import pytest 


def test_app_root_works():
    # Test that "/" works
    session = requests.Session()
    response = session.get('http://127.0.0.1:8000/') 
    session.close()
    assert response.text 
    

def test_app_root_keys():
    # Test that "/" returns usage information 
    session = requests.Session()
    response = session.get('http://127.0.0.1:8000/') 
    session.close()
    response_dict = json.loads(response.text)
    assert sorted(response_dict.keys()) == ['apis', 'message']
    assert sorted(response_dict['apis'].keys()) == ['query', 'tables', 'tables/info']


@pytest.mark.parametrize('command,expected_key', [
    ('all', 'table_names'),
    ('fake', 'error')
])
def test_app_get_tables(command, expected_key):
    # Tests that the tables URI works; It should return a dictionary
    # if all is not the command passed, it should return an error 
    session = requests.Session()
    response = session.get(f'http://127.0.0.1:8000/tables/{command}')
    response_dict = json.loads(response.text)
    session.close()
    assert 'error' in response_dict.keys() if expected_key == 'error' else 'table_names' in response_dict.keys()


@pytest.mark.xfail(msg='This is a test for the chinook database only')
def test_app_table_info():
    # Tests that the tables/info URI works 
    session = requests.Session()
    response = session.get('http://127.0.0.1:8000/tables/info/albums')
    assert json.loads(response.text)


@pytest.mark.xfail(msg='This is a test for the chinook database only')
@pytest.mark.parametrize('sql_query,expected_result', [
    ('SELECT * FROM employees', 'non-empty'),
    ('DROP employees', [])
])
def test_app_query(sql_query, expected_result):
    # Tests that the API works as expected: return [] if prohibited keywords are used else a non-empty list 
    # Tests that the result is JSON serializable 
    session = requests.Session()
    received_dict = json.loads(session.get(f'http://127.0.0.1:8000/query/{sql_query}').text)
    session.close()
    assert received_dict if expected_result == 'non-empty' else not received_dict


    
