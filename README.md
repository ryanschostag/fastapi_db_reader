# FASTAPI_APP

This is a small example API that uses GET and POST for database operations. This application has been
test with the popular chinook sample SQLite3 database from https://www.sqlitetutorial.net/wp-content/uploads/2018/03/chinook.zip. 

## Requiremnets
- FastAPI
- Uvicorn
- Python 3.6+

## Usage
1. Update config.py and make sure all directory paths exist on the system
2. Run uvicorn (e.g. python3 -m uvicorn app:my_app --reload)
3. Then, you can run queries against the API at http://127.0.0.1:8000
4. The available APIs are:
    a. "/" - Get usage information
    b. "/tables" - Supported command is 'all' (e.g. tables/all) which produces a list of table names in the database
    c. "/tables/info" - Given a table name, provide the schematics of the table (e.g. /tables/info/my_table provides data about the fields in the table)
    d. "/query"- Send a SELECT SQL statement to the database. Prohibited keywords are found in config.py 

### config.py
Set the database path, name, prohibited SQL keywords and other settings in this file.
