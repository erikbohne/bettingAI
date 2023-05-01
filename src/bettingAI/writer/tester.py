import os
import traceback
import sys


import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_

from bettingAI.googleCloud.initPostgreSQL import initPostgreSQL
from bettingAI.writer.databaseClasses import *
from bettingAI.writer.addRow import *
from bettingAI.writer.scraper import (
    get_match_links,
    get_player_links,
    get_player_bio,
    get_match_info,
)
from bettingAI.writer.values import SEASONS

connection = initPostgreSQL()

# Start session with connection
Session = sessionmaker(connection)
session = Session()

match = 3056113
season = "2019-2020"

match = 762074
season = "2010"

matchStats, playerStats = get_match_info(f"/match/{match}")
print(matchStats)
print(playerStats)
match, homeSide, awaySide = add_match(match, season, matchStats)
session.add(match)  # add main info
if homeSide is not None:
    session.add(homeSide)  # add home stats
    session.add(awaySide)  # add away stats
session.commit()
print("comitted")
session.close()
