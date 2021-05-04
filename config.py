db_path = './db/chinook.db'
db_name = 'chinook'
prohibited_query_keywords = ['ALTER', 'ATTACH', 'COMMIT', 'CREATE', 'DATABASE', 
                             'DELETE', 'DETACH', 'DROP', 'INDEX', 'INSERT', 
                             'PRAGMA', 'TABLE', 'TEMP', 'TEMPORARY', 'TRANSACTION', 
                             'TRIGGER', 'UPDATE', 'VACUUM']

# logging configuration
log_name = 'fastapi_app'
log_file_path = '/var/log/fastapi_app.log'  # to avoid circular reference, do not use a file in the app folder
log_format = '%[(time)s %(process)s %(file)s %(line)s %(func)s] %(message)s'