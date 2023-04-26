import os
import json

import sqlalchemy
from google.cloud.sql.connector import Connector

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '../../keys/googleCloudKey.json'

def initPostgreSQL():
    """
    Connects and initializes PostgreSQL
    """
    # Import database creditations
    creds = json.load(open("../../keys/postgreSQLKey.json"))

    def getConnection():
        connector = Connector()
        connection = connector.connect(
            creds["connectionName"],
            "pg8000",
            user=creds["user"],
            password=creds["password"],
            db=creds["dbname"]
        )
        return connection
    
    try: # Try to connecto to database
        engine = sqlalchemy.create_engine(
            "postgresql+pg8000://",
            creator=getConnection,
        )
        return engine
    except Exception as e: # Connection failed
        return None