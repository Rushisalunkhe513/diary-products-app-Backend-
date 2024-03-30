import os
import redis
from dotenv import load_dotenv
# we will first do test(development) and then we will do deployment(Production)

"""
lets create class Config which will have db_url,
db_url will be diffrent for development and Production.
"""
load_dotenv()


# also we will be needing redis database which is NOSQL key value store type database.
# we installe redis now lets go and create redis server here.
    
class Development():
    db_url = os.getenv("DEV_DB_URL")
    r_client = redis.Redis(host='localhost',port=6379,db=0)
    """
    This configuration is for redis developemnt.
    Here we are setting up redis clien with,
    host = 'localhost' meaning that our redis server will be run on same machine where python scipt or app is running.
    port = 6379(default port for redis) on this port redis will listen to request from connections.
    db = 0 meaning redis have 16 dataabses so, by that we are connecting to db =0 first dataabse.
    """
    
class Production():
    db_url = f"postgresql+psycopg2://{os.getenv('SQL_DB_USERNAME')}:{os.getenv('SQL_DB_PASSWORD')}@{os.getenv('SQL_DB_HOST')}/{os.getenv('SQL_DB_NAME')}"
    r_client = redis.Redis(
        host=os.getenv("REDIS_HOSTNAME"),
        username=os.getenv("REDIS_USER_NAME"),
        password=os.getenv("REDIS_USER_PASS"),
        port=6379,
        db=os.getenv("REDIS_DB"),
        ssl=True,
        ssl_cert_reqs=None,
        charset="utf-8",
    )
    
    