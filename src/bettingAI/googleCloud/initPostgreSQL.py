import os
import json

import sqlalchemy
from sqlalchemy.orm import sessionmaker
from google.cloud.sql.connector import Connector

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "../../../../keys/googleCloudKey.json"


def initPostgreSQL() -> sqlalchemy.engine.Engine:
    """Connects and initializes PostgreSQL.

    Returns:
        The SQLAlchemy engine object for the PostgreSQL connection.
    """
    # Import database creditations
    creds = json.load(open("../../../../keys/postgreSQLKey.json"))

    def getConnection():
        connector = Connector()
        connection = connector.connect(
            creds["connectionName"],
            "pg8000",
            user=creds["user"],
            password=creds["password"],
            db=creds["dbname"],
        )
        return connection

    try:  # Try to connecto to database
        engine = sqlalchemy.create_engine(
            "postgresql+pg8000://",
            creator=getConnection,
        )
        return engine
    except Exception as e:  # Connection failed
        return None
    
def initSession() -> sqlalchemy.orm.Session:
    """Initializes a SQLAlchemy session for the PostgreSQL connection.
    
    Returns:
        The SQLAlchemy session object.
    """
    connection = initPostgreSQL()
    Session = sessionmaker(connection)
    return Session()
