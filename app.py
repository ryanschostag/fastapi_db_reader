from fastapi import FastAPI
my_app = FastAPI()

@my_app.get('/')
async def root():
    return {'message': 'hello world!'}
 
