"""
Variables for test_app.py
"""
album_fields = ['AlbumId', 'Title', 'ArtistId']
artist_fields = ['ArtistId', 'Name']
customer_fields = ['CustomerId', 'FirstName', 'LastName', 'Company', 'Address', 'City', 'State', 
                   'Country', 'PostalCode', 'Phone', 'Fax', 'Email', 'SupportRepId']
employee_fields = ['EmployeeId', 'LastName', 'FirstName', 'Title', 'ReportsTo', 'BirthDate', 
                   'HireDate', 'Address', 'City', 'State', 'Country', 'PostalCode', 'Phone', 'Fax', 'Email']
genre_fields = ['GenreId', 'Name']
invoice_fields = ['InvoiceId', 'CustomerId', 'InvoiceDate', 'BillingAddress', 'BillingCity', 'BillingState',
                  'BillingCountry', 'BillingPostalCode', 'Total']
invoice_line_fields = ['InvoiceLineId', 'InvoiceId', 'TrackId', 'UnitPrice', 'Quantity']
media_type_fields = ['MediaTypeId', 'Name']
playlist_fields = ['PlaylistId', 'Name']
playlist_track_fields = ['PlaylistId', 'TrackId']
track_fields = ['TrackId', 'Name', 'AlbumId', 'MediaTypeId', 'GenreId', 'Composer', 'Milliseconds', 'Bytes', 'UnitPrice']
album_request = {
    "table": "Album",
    "fields": ["AlbumId", "Title"],
    "filters": {
        "ArtistId": 1
    }   
}
album_expected_sql_query = 'SELECT "Album"."AlbumId", "Album"."Title" \nFROM "Album" \nWHERE "Album"."ArtistId" = :ArtistId_1'
album_query_result = [{'AlbumId': 1, 'Title': 'For Those About To Rock We Salute You'}, {'AlbumId': 4, 'Title': 'Let There Be Rock'}]
artist_request = {
    "table": "Artist",
    "filters": {
        "ArtistId": 1
    }
}
artist_expected_sql_query = 'SELECT "Artist"."ArtistId", "Artist"."Name" \nFROM "Artist" \nWHERE "Artist"."ArtistId" = :ArtistId_1'
artist_query_result = [{'ArtistId': 1, 'Name': 'AC/DC'}]
no_table_query = {
    "fields": ["AlbumId", "Title"],
    "filters": {
        "ArtistId": 1
    }
}
no_table_detail = [{
    'type': 'missing',
    'loc': ['body', 'table'],
    'msg': 'Field required',
    'input': {
        'fields': ['AlbumId', 'Title'],
        'filters': {'ArtistId': 1}},
        'url': 'https://errors.pydantic.dev/2.5/v/missing'
}]
