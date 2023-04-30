import os
import sys

sys.path.append(os.path.join("..", "googleCloud"))
from initPostgreSQL import initPostgreSQL

from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_
import sqlalchemy
import traceback

from databaseClasses import *
from addRow import *
from scraper import get_match_links, get_player_links, get_player_bio, get_match_info
from values import SEASONS

connection = initPostgreSQL()

# Start session with connection
Session = sessionmaker(connection)
session = Session()

match = 3056113
season = '2019-2020'

match = 762074
season = '2010'

matchStats, playerStats = get_match_info(f"/match/{match}")
print(matchStats)
print(playerStats)
match, homeSide, awaySide = add_match(match, season, matchStats)
session.add(match) # add main info
if homeSide is not None:   
    session.add(homeSide) # add home stats
    session.add(awaySide) # add away stats
session.commit()
print("comitted")
session.close()

