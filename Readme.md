# Dairy Products APP (Backend)


Dairy Products App for mobile is a cross platform application built in [Graphene](https://docs.graphene-python.org/en/latest/) using GraphQL API.

### Programming language,API and other Modules used in This Project:-
- programming lang:- Python
- API:- GraphQL(Graphene)
- Framework:- FAST API
- Database(RDBMS):- Postgresql,SQLite
- NOSQL Dataabse:- redis
- ORM:- SQLALchemy
- Jwt Library:- PyJWT
- PasswordHashing:- argon2
- CI/CD:- DOCKER(Dockerfile)

- other modules used are datetime,os,load_dotenv



### Setup Project

- Clone this repository using `https://github.com/Rushisalunkhe513/diary-products-app-Backend-.git`.
- `pip install -r requirements.txt` to get all the dependencies.

### Running the app

`uvicorn app.main:app --reload` or
`uvicorn app.main:app --reload --port 5000 --host 0.0.0.0`


## Project Structure

```bash
Milk_production_app/
├── app/ 
|   ├─ /db  # database related details like models(Tables),defult_admin_data,database.py               
|   |  └── blocklist.py                 # blocking jwt tokens from being reused again
|   |  └── database.py                  # database configuration like creating session and managing db
|   |  └── default_admin_data.py        # default_admin data
|   |  └── models.py                    # tables with columns and constraints.
|   ├─ /gql                        # gql folder with mutations and types(schema)
|   |  └── banner                  # banner folder with its mutation and types
|   |       └── mutation.py             # post,update,delete method
|   |       └── types.py                # schema for mutation
|   |  └── items                   # items folder with its mutation and types
|   |       └── mutation.py             # post,update,delete method
|   |       └── types.py                # schema for mutation
|   |  └── orders                  # orders folder with its mutation and types
|   |       └── mutation.py             # post,update,delete method
|   |       └── types.py                # schema for mutation
|   |  └── subscription            # subscription folder with its mutation and types
|   |       └── mutation.py             # post,update,delete method
|   |       └── types.py                # schema for mutation
|   |  └── users                   # users folder with its mutation and types
|   |       └── mutation.py             # post,update,delete method
|   |       └── types.py                # schema for mutation
|   |  └── wallet                  # wallet folder with its mutation and types
|   |       └── mutation.py             # post,update,delete method
|   |       └── types.py                # schema for mutation
|   └── config.py/                 # configuration file for production or development details.
|   └── main.py/                   # main.py with all application resources gathered here
|   └── utils.py                   # utils.py with all function     
├── .gitignore/                    # files to ignore from git will be in .gitignore          
├── Dockerfile/                    # dockerfile for building docker image and running application         
├── Readme.md/                     # application details.    
├── requirements.txt/              # required modules and packages in requirements.txt
```

## Features
- /banner
- /item
- /orders
- /subscription
- / users
- /wallet

## METHODS:-
- In graphql threr is only query and Mutation
- query work as get request where,
- Mutation works as post,put,delete request.

### Note:-

- Most Challenging part for me in this is project is about applying Authorization and Authentication for user and admin Authentiction.
- We used **pyjwt** library for encoding and decoding jwt tokens using user/admin credentials.
- by doing that we are creating access and refresh token.
- accesss token is used for authorization and authentication where,
- refresh token used to genrate new tokens when user logged out or his access token duration about to get expired.