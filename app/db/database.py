# here in database.py will be having database connection related info.
# like which server will be connecting production or devlopment.
import os
from dotenv import load_dotenv
from app.config import Development,Production
from sqlalchemy import create_engine  # create engine will create connection with database.
from sqlalchemy.orm import sessionmaker,scoped_session # we will be importing sessionmaker to make database operation like adding, removing data from the database.

from app.db.models import Base,AdminModel
from app.db.default_admin_data import default_admin

load_dotenv()
 
# connecting to database based on requirements.
config = Production() if os.getenv("PRODUCTION")  else Development()

# lets get database url from the configuration(config)

DB_URL = config.db_url
print("*******Database url******", DB_URL)

# lets get create_engine to establish connection with database and python application.
"""
The create_engine function in SQLAlchemy is used to create an Engine object, which acts as the central connection point to your database. It establishes a 
connection between your Python application and the database server, allowing you to interact with the database using SQLAlchemy's functionalities.
ex,
engine = create_engine(db_url, pool_size = 30, echo = True) 
"""

engine = create_engine(
    DB_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=5,
    echo=True,
    pool_recycle=1800
)

"""
now here will be discussed above configurations:
DB_URL = db_url is our database url.,
pool_pre_ping = pool_pre_Ping will ensure the database connection is still active or not,
pool_size = pool_size will declare max no of simultenous connection can be made to database.
max_overflow = max_overflow will allow additional connection to connect to database beyond pool_size.
pool_recycle = pool_cycle will kept current database connection for 1800 seconds open and after 1800 seconds
               current connection will be closed and new will be opened.
echo = this will show us all sql queries made to database in logging way.we can comment this if we want.
"""

# now lets bind this database to sessionmaker.

"""
sesionmaker = sesionmaker is used to create factory of database connection like session which are reesponsible for querying data from database,adding and deleting
and much more.
scoped_session = scoped session is used for managing threads of database. if we are using multiple threads to get,add data from database then multiple session will
be created and there might conflict happen so, for to give each session there unique thread we use scoped_session. which will allow uninterupted session work.
auto_commit= auto_commit will avoid adding or updating data everytime we do changes instead it will commit the changes in single time.
auto_flush = auto_flush will keep chanes or commits in database for timebeing. it doesnt commit right away.
"""

Session = scoped_session(sessionmaker(bind = engine,autoflush=False,autocommit =False))


# lets create prepare_database function
"""
this prepare_database function will prepare database evrytime application starts.
"""

def prepare_database():
    Base.metadata.create_all(engine)
    with Session() as session:
        for admin_data in default_admin:
            admin_details = AdminModel(**admin_data)
            session.add(admin_details)
            try:
                session.commit()
                session.refresh(admin_details)
            except:
                session.rollback()
                
        session.commit()
        
# this prepare_database function will create table we described in our models.py only once.