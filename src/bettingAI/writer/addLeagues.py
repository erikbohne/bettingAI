import sys
import os

from colorama import Fore
from sqlalchemy.orm import sessionmaker

from bettingAI.googleCloud.initPostgreSQL import initPostgreSQL
from bettingAI.writer.databaseClasses import *


def add_leagues() -> None:

    # Establish connection to the database
    connection = initPostgreSQL()
    if connection is None:
        sys.exit(Fore.RED + "-> Could not connect to PostgreSQL")
    else:
        print(Fore.GREEN + "-> Connected to PostgreSQL")

    Session = sessionmaker(connection)
    session = Session()

    league1 = Leagues(
        id="204",
        name="2. divisjon",
        country="Norway",
        n_teams=28,
        level=3,
        year_span=1,
    )
    session.add(league1)

    session.commit()
    session.close()


add_leagues()
