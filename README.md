# FASTAPI_APP

This is a small example API that uses GET and POST for database operations. This application has been
test with the popular chinook sample SQLite3 database from https://www.sqlitetutorial.net/wp-content/uploads/2018/03/chinook.zip. 

## Requiremnets

- FastAPI
- Uvicorn
- Python 3.x

## Tested Python Version

- 3.7.9
- 3.12.10

## Tested Platforms

- Windows 10

## Usage

1. Update settings.py and make sure all directory paths exist on the system
2. Run uvicorn (e.g. python3 -m uvicorn app:my_app --reload)
3. Then, you can run queries against the API at http://127.0.0.1:8000
4. The available APIs are:
    a. "/" - Get usage information
    b. "/tables" - Supported command is 'all' (e.g. tables/all) which produces a list of table names in the database
    c. "/tables/info" - Given a table name, provide the schematics of the table (e.g. /tables/info/my_table provides data about the fields in the table)# FastAPI DB Reader

A lightweight FastAPI application to query and serve data from a SQLite database (e.g., Chinook). Built for fast development, easy integration, and API-based access to structured relational data.

## Features

- RESTful API built with FastAPI
- SQLite database backend (Chinook)
- Configuration via `.ini` files
- Modular design (separated logic, models, settings)
- Automatic API documentation
- Unit tests included

## Requirements

- Python 3.9+
- pip

## Installation

```bash
git clone https://github.com/ryanschostag/fastapi_db_reader.git
cd fastapi_db_reader
pip install -r requirements.txt
```

## Configuration

Edit `config.ini` and `logging.ini` to adjust database paths, logging behavior, and API settings.

## Running the App

```bash
uvicorn app:app --reload
```

```python
python app.py
```

The app will start at `http://127.0.0.1:8000`.

## API Documentation

FastAPI provides interactive docs at:

- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

You can also view the static `api_docs.html`.

## Project Structure

```text
fastapi_db_reader/
├── app.py               # FastAPI app definition
├── db_interface.py      # Database access layer
├── models.py            # Pydantic models
├── settings.py          # Settings loader
├── config.ini           # App configuration
├── logging.ini          # Logging config
├── requirements.txt     # Dependencies
├── db/
│   └── chinook.db       # Example SQLite database
└── tests/
    └── test_app.py      # Unit tests
```

## Running Tests

```bash
pytest tests/
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Author

Created by [Ryan Schostag](https://github.com/ryanschostag)
