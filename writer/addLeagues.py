import sys
from sqlalchemy.orm import sessionmaker
from colorama import Fore
from writer import initPostgreSQL
from databaseClasses import *


def add_leagues():
    
    # Establish connection to the database
    connection = initPostgreSQL()
    if connection is None:
        sys.exit(Fore.RED + "-> Could not connect to PostgreSQL")
    else:
        print(Fore.GREEN + "-> Connected to PostgreSQL")
    
    Session = sessionmaker(connection)
    session = Session()
    
    league1 = Leagues(id="48", name="Championship", country="England", n_teams=24, level=2)
    session.add(league1)
    
    league2 = Leagues(id="108", name="League One", country="England", n_teams=24, level=3)
    session.add(league2)
    
    league3 = Leagues(id="109", name="Leauge Two", country="England", n_teams=24, level=4)
    session.add(league3)
    
    league4 = Leagues(id="59", name="Eliteserien", country="Norway", n_teams=16, level=1)
    session.add(league4)
    
    session.commit()
    session.close()

add_leagues()