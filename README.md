# FastAPI DB Reader

A lightweight FastAPI application for querying and serving data from a SQLite database using RESTful endpoints. Built with simplicity and modularity in mind.

## Features

- FastAPI-based REST API
- SQLite database backend (Chinook)
- Pydantic models for request/response validation
- Configurable via `.ini` files
- Logging configuration support
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

- `config.ini`: Application settings (e.g., database path)
- `logging.ini`: Logging behavior (format, level, etc.)

## Running the App

```bash
uvicorn app:app --reload
```

Visit: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for the interactive Swagger documentation.

## Project Structure

```
fastapi_db_reader/
├── app.py               # FastAPI app setup and routes
├── db_interface.py      # DB query interface logic
├── models.py            # Pydantic models
├── settings.py          # Settings/config parsing
├── config.ini           # Application configuration
├── logging.ini          # Logging configuration
├── requirements.txt     # Project dependencies
├── db/
│   └── chinook.db       # SQLite database file
└── tests/
    ├── test_app.py      # Tests for app endpoints
    └── app_test_vars.py # Test fixtures/config
```

## Running Tests

```bash
pytest tests/
```

## License

MIT License. See [LICENSE](LICENSE) for details.

## Author

[Ryan Schostag](https://github.com/ryanschostag)
