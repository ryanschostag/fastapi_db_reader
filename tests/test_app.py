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


def test_app_table_names():
    # Tests that the tables URI works 
    session = requests.Session()
    response = session.get('http://127.0.0.1:8000/tables/all')
    session.close()
    assert isinstance(ast.literal_eval(response.text), list)


# @pytest.xfail('This is a test for the chinook database only')
def test_app_table_info():
    # Tests that the tables/info URI works 
    session = requests.Session()
    response = session.get('http://127.0.0.1:8000/tables/info/albums')
    assert response.text

