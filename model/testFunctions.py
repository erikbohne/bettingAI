import os 
import sys

sys.path.append(os.path.join("..", "googleCloud"))
from initPostgreSQL import initPostgreSQL
from sqlalchemy.orm import sessionmaker
from colorama import Fore

from getInputs import *

engine = initPostgreSQL()
Session = sessionmaker(engine)
session = Session()
print(Fore.GREEN + "Connected to database", end="\n\n")

# Teams and seasons to test
toTest = [(9825, "2022-2023"), (9825, "2020-2021"), (9825, "2021-2022")]
sides = ["home", "away"]

# Testing functions from getInputs.py
print(Fore.CYAN + "getInputs.py:")

# Testing statistics features
print(Fore.MAGENTA + "    Statistics:")

# Testing get_average_goals_season()
tested = 0
try:
    for teamID, season in toTest:
        for side in sides:
            get_average_goals_season(teamID, season, side, session)
        tested += 1
    print(Fore.GREEN + f"        get_average_goals_season() {tested}/{len(toTest)}")
except Exception as e:
    print(Fore.RED + f"        get_average_goals_season() {tested}/{len(toTest)} -> {e}")
    
# Testing get_average_conceded_season()
tested = 0
try:
    for teamID, season in toTest:
        for side in sides:
            get_average_conceded_season(teamID, season, side, session)
        tested += 1
    print(Fore.GREEN + f"        get_average_conceded_season() {tested}/{len(toTest)}")
except Exception as e:
    print(Fore.RED + f"        get_average_conceded_season() {tested}/{len(toTest)} -> {e}")
    
# Testing get_average_goaldiff_season()
tested = 0
try:
    for teamID, season in toTest:
        for side in sides:
            get_average_goaldiff_season(teamID, season, side, session)
        tested += 1
    print(Fore.GREEN + f"        get_average_goaldiff_season() {tested}/{len(toTest)}")
except Exception as e:
    print(Fore.RED + f"        get_average_goaldiff_season() {tested}/{len(toTest)} -> {e}")
    
# Testing get_outcome_rate()
tested = 0
try:
    for teamID, season in toTest:
        for side in sides:
            total = 0
            for outcome in ["win", "draw", "loss"]:
                total += get_outcome_rate(teamID, season, side, outcome, session)
            if total != 1: # check if all rates go up to 1 to ensure correct rates
                raise ValueError("win/draw/loss rates does not add up to 1")
        tested += 1
    print(Fore.GREEN + f"        get_outcome_rate() {tested}/{len(toTest)}")
except Exception as e:
    print(Fore.RED + f"        get_outcome_rate() {tested}/{len(toTest)} -> {e}")

# Testing get_clean_sheet_rate()
tested = 0
try:
    for teamID, season in toTest:
        for side in sides:
            get_clean_sheet_rate(teamID, season, side, session)
        tested += 1
    print(Fore.GREEN + f"        get_clean_sheet_rate() {tested}/{len(toTest)}")
except Exception as e:
    print(Fore.RED + f"        get_clean_sheet_rate() {tested}/{len(toTest)} -> {e}")
    

# Testing Recent form features
print(Fore.MAGENTA + "    Recent form:")

# Testing Recent form features
print(Fore.MAGENTA + "    Head 2 head:")

# Testing Recent form features
print(Fore.MAGENTA + "    Player info:")

# Testing Recent form features
print(Fore.MAGENTA + "    Playstyle:")

