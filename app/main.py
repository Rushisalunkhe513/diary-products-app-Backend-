from graphene import Schema,ObjectType
from starlette_graphene3 import GraphQLApp,make_playground_handler

from app.gql.mutation import Mutation
from app.gql.queries import Query

from fastapi import FastAPI
from app.db.database import prepare_database
import uvicorn


schema = Schema(query=Query,mutation=Mutation)

# app object fir FASTAPI.
app = FastAPI()

"""
app: This is a variable name that typically refers to the instance of the FastAPI application. This instance will be used to define routes, 
handle requests, and configure various aspects of the API.

FastAPI(): This is a constructor call that creates an instance of the FastAPI class. The FastAPI class provides methods and attributes that 
allow developers to define API endpoints, handle requests and responses, and configure middleware, among other things.
"""

app.title = "Milk_Production application"
app.version = "0.1.0"
app.summary = "This web application Milk_products app is for Local Dairy shop people"

# lets get database started up every time application starts up.
"""
everytime app starts database will start as well
it will create all tables,columns as app starts running.
"""
@app.on_event("startup")
def startup_event():
    prepare_database()


# now lets mount our application on some endpoint.
"""
This will help us to handle queries and Mutation in this garphql app.
"""
app.mount("/",GraphQLApp(schema=schema,on_get = make_playground_handler())) # important to give make_palyground_handler() as it is.


# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="debug")