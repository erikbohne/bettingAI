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
        id="208",
        name="3. Liga",
        country="Germany",
        n_teams=20,
        level=3,
        year_span=2,
    )
    session.add(league1)

    session.commit()
    session.close()


add_leagues()
