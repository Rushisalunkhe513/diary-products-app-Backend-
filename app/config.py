import os
from dotenv import load_dotenv
# we will first do test(development) and then we will do deployment(Production)

"""
lets create class Config which will have db_url,
db_url will be diffrent for development and Production.
"""
load_dotenv()
    
    
class Development():
    db_url = os.getenv("DEV_DB_URL")
    
class Production():
    db_url = f"postgresql+psycopg2://{os.getenv('SQL_DB_USERNAME')}:{os.getenv('SQL_DB_PASSWORD')}@{os.getenv('SQL_DB_HOST')}/{os.getenv('SQL_DB_NAME')}"
    