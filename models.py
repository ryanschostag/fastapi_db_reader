from typing import List, Dict, Any, Optional
from pydantic import BaseModel, RootModel


class TableSchema(RootModel[Dict[str, str]]):
    """
    Represents the schema of a database table, mapping column names to their SQL types.
    """
    pass


class TableModel(RootModel[Dict[str, str]]):
    """
    Represents a database table with its fields and their types.
    """
    pass


class TableWrapper(RootModel[Dict[str, TableModel]]):
    """One table name → table schema"""
    pass


class QueryRequest(BaseModel):
    """
    Represents a request to query a database table."""
    table: str
    fields: Optional[List[str]] = None
    filters: Optional[Dict[str, Any]] = None


class TableList(BaseModel):
    """
    Represents a list of table names in the database.
    """
    table_names: List[str]


class DBQueryResponse(BaseModel):
    query: str
    result: List[Dict[str, Any]]

