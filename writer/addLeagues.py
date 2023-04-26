import sys
import os
from sqlalchemy.orm import sessionmaker
from colorama import Fore

sys.path.append(os.path.join("..", "googleCloud"))
from initPostgreSQL import initPostgreSQL

from databaseClasses import *


def add_leagues() -> None:
    
    # Establish connection to the database
    connection = initPostgreSQL()
    if connection is None:
        sys.exit(Fore.RED + "-> Could not connect to PostgreSQL")
    else:
        print(Fore.GREEN + "-> Connected to PostgreSQL")
    
    Session = sessionmaker(connection)
    session = Session()
    
    league1 = Leagues(id="48", name="Championship", country="England", n_teams=24, level=2, year_span=2)
    session.add(league1)
    
    session.commit()
    session.close()

add_leagues()