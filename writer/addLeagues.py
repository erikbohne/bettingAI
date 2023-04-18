import sys
import os
from sqlalchemy.orm import sessionmaker
from colorama import Fore

sys.path.append(os.path.join("..", "googleCloud"))
from initPostgreSQL import initPostgreSQL

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
    
    league1 = Leagues(id="47", name="Premier League", country="England", n_teams=20, level=1, year_span=2)
    session.add(league1)
    
    league2 = Leagues(id="59", name="Eliteserien", country="Norway", n_teams=16, level=1, year_span=1)
    session.add(league2)
    
    session.commit()
    session.close()

add_leagues()