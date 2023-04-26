import os 
import sys
from datetime import datetime

from sqlalchemy.orm import sessionmaker
from colorama import Fore

from bettingAI.googleCloud.initPostgreSQL import initPostgreSQL
from bettingAI.model.getInputs import *

# Teams and seasons to test
toTest = [(9825, "2022-2023"), (8650, "2020-2021"), (8456, "2021-2022"), (8466, "2022-2023")]
sides = ["home", "away"]

def test_statistics(session):
    # Testing statistics features
    print(Fore.MAGENTA + "    Statistics:")

    # Testing get_average_goals_season()
    tested = 0
    try:
        for teamID, season in toTest:
            for side in sides:
                get_average_goals_season(teamID, season, side, session)
            tested += 1
        print(Fore.GREEN + f"        get_average_goals_season() {tested}/{len(toTest)} ✅")
    except Exception as e:
        print(Fore.RED + f"        get_average_goals_season() {tested}/{len(toTest)} -> {e}")
        
    # Testing get_average_conceded_season()
    tested = 0
    try:
        for teamID, season in toTest:
            for side in sides:
                get_average_conceded_season(teamID, season, side, session)
            tested += 1
        print(Fore.GREEN + f"        get_average_conceded_season() {tested}/{len(toTest)} ✅")
    except Exception as e:
        print(Fore.RED + f"        get_average_conceded_season() {tested}/{len(toTest)} -> {e}")
        
    # Testing get_average_goaldiff_season()
    tested = 0
    try:
        for teamID, season in toTest:
            for side in sides:
                get_average_goaldiff_season(teamID, season, side, session)
            tested += 1
        print(Fore.GREEN + f"        get_average_goaldiff_season() {tested}/{len(toTest)} ✅")
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
        print(Fore.GREEN + f"        get_outcome_rate() {tested}/{len(toTest)} ✅")
    except Exception as e:
        print(Fore.RED + f"        get_outcome_rate() {tested}/{len(toTest)} -> {e}")

    # Testing get_clean_sheet_rate()
    tested = 0
    try:
        for teamID, season in toTest:
            for side in sides:
                get_clean_sheet_rate(teamID, season, side, session)
            tested += 1
        print(Fore.GREEN + f"        get_clean_sheet_rate() {tested}/{len(toTest)} ✅")
    except Exception as e:
        print(Fore.RED + f"        get_clean_sheet_rate() {tested}/{len(toTest)} -> {e}")
    
def test_recent_form(session):
    # Testing Recent form features
    print(Fore.MAGENTA + "    Recent form:")

    toTestRecent = [(8197, datetime(year=2022, month=7, day=18))]

    # Testing get_outcome_streak(teamID, date, session):
    tested = 0
    try:
        for teamID, date in toTestRecent:
            get_outcome_streak(teamID, date, session)
            tested += 1
        print(Fore.GREEN + f"        get_outcome_streak() {tested}/{len(toTestRecent)} ✅")
    except Exception as e:
        print(Fore.RED + f"        get_outcome_streak() {tested}/{len(toTestRecent)} -> {e}")

def test_h2h(session):
    # Testing Recent form features
    print(Fore.MAGENTA + "    Head 2 head:")
    
    toTestH2H = [
        (8650, 8456, datetime(year=2023, month=4, day=1)),   # liverpool - man city
        (8191, 10204, datetime(year=2022, month=12, day=1)), # burnley - brighton
        (10261, 9825, datetime(year=2023, month=2, day=28)), # newcastle - arsenal
        (8466, 8455, datetime(year=2023, month=1, day=12))   # southampton - chelsea
        ]

    # Testing get_outcome_distribution()
    tested = 0
    try:
        for teamID, opponentID, date in toTestH2H:
            get_outcome_distribution(teamID, opponentID, date, session)
            tested += 1
        print(Fore.GREEN + f"        get_outcome_distribution() {tested}/{len(toTestH2H)} ✅")
    except Exception as e:
        print(Fore.RED + f"        get_outcome_distribution() {tested}/{len(toTestH2H)} -> {e}")
    
    # Testing get_side_distribution()
    tested = 0
    try:
        for teamID, opponentID, date in toTestH2H:
            get_side_distribution(teamID, opponentID, date, session)
            tested += 1
        print(Fore.GREEN + f"        get_side_distribution() {tested}/{len(toTestH2H)} ✅")
    except Exception as e:
        print(Fore.RED + f"        get_side_distribution() {tested}/{len(toTestH2H)} -> {e}")
    
    # Testing get_recent_encounters()
    tested = 0
    try:
        for teamID, opponentID, date in toTestH2H:
            get_recent_encounters(teamID, opponentID, date, session)
            tested += 1
        print(Fore.GREEN + f"        get_recent_encounters() {tested}/{len(toTestH2H)} ✅")
    except Exception as e:
        print(Fore.RED + f"        get_recent_encounters() {tested}/{len(toTestH2H)} -> {e}")
         
    # Testing get_average_goals_per_match()
    tested = 0
    try:
        for teamID, opponentID, date in toTestH2H:
            get_average_goals_per_match(teamID, opponentID, date, session)
            tested += 1
        print(Fore.GREEN + f"        get_average_goals_per_match() {tested}/{len(toTestH2H)} ✅")
    except Exception as e:
        print(Fore.RED + f"        get_average_goals_per_match() {tested}/{len(toTestH2H)} -> {e}")
    
    # Testing def get_average_goals_conceded_per_match(teamID, opponentID, date, session):
    tested = 0
    try:
        for teamID, opponentID, date in toTestH2H:
            get_average_goals_conceded_per_match(teamID, opponentID, date, session)
            tested += 1
        print(Fore.GREEN + f"        get_average_goals_conceded_per_match() {tested}/{len(toTestH2H)} ✅")
    except Exception as e:
        print(Fore.RED + f"        get_average_goals_conceded_per_match() {tested}/{len(toTestH2H)} -> {e}")
       
    # Testing get_average_goals_difference_match()
    tested = 0
    try:
        for teamID, opponentID, date in toTestH2H:
            get_average_goal_difference_match(teamID, opponentID, date, session)
            tested += 1
        print(Fore.GREEN + f"        get_average_goals_difference_match() {tested}/{len(toTestH2H)} ✅")
    except Exception as e:
        print(Fore.RED + f"        get_average_goals_difference_match() {tested}/{len(toTestH2H)} -> {e}")
        
    # Testing get_btts_rate()
    tested = 0
    try:
        for teamID, opponentID, date in toTestH2H:
            get_btts_rate(teamID, opponentID, date, session)
            tested += 1
        print(Fore.GREEN + f"        get_btts_rate() {tested}/{len(toTestH2H)} ✅")
    except Exception as e:
        print(Fore.RED + f"        get_btts_rate() {tested}/{len(toTestH2H)} -> {e}")
        
    # Testing get_clean_sheet_rate()
    tested = 0
    try:
        for teamID, opponentID, date in toTestH2H:
            get_clean_sheet_rate_h2h(teamID, opponentID, date, session)
            tested += 1
        print(Fore.GREEN + f"        get_clean_sheet_rate() {tested}/{len(toTestH2H)} ✅")
    except Exception as e:
        print(Fore.RED + f"        get_clean_sheet_rate() {tested}/{len(toTestH2H)} -> {e}")
        
    # Testing def get_over_under_2_5(teamID, opponentID, date, session):
    tested = 0
    try:
        for teamID, opponentID, date in toTestH2H:
            get_over_under_2_5(teamID, opponentID, date, session)
            tested += 1
        print(Fore.GREEN + f"        get_over_under_2_5() {tested}/{len(toTestH2H)} ✅")
    except Exception as e:
        print(Fore.RED + f"        get_over_under_2_5() {tested}/{len(toTestH2H)} -> {e}")
        
    # Testing def get_outcome_streak_h2h(teamID, opponentID, date, session):
    tested = 0
    try:
        for teamID, opponentID, date in toTestH2H:
            get_outcome_streak_h2h(teamID, opponentID, date, session)
            tested += 1
        print(Fore.GREEN + f"        get_outcome_streak_h2h() {tested}/{len(toTestH2H)} ✅")
    except Exception as e:
        print(Fore.RED + f"        get_outcome_streak_h2h() {tested}/{len(toTestH2H)} -> {e}")  
        
def test_player_info(session):
    # Testing player info functions
    print(Fore.MAGENTA + "    Player info:") 
    
    # Testing get_average_player_rating()
    tested = 0
    try:
        for teamID, _ in toTest:
            get_average_player_rating(teamID, session)
            tested += 1
        print(Fore.GREEN + f"        get_average_player_rating() {tested}/{len(toTest)} ✅")
    except Exception as e:
        print(Fore.RED + f"        get_average_player_rating() {tested}/{len(toTest)} -> {e}")

    # Testing get_average_player_rating()
    tested = 0
    try:
        for teamID, _ in toTest:
            get_average_player_age(teamID, session)
            tested += 1
        print(Fore.GREEN + f"        get_average_player_age() {tested}/{len(toTest)} ✅")
    except Exception as e:
        print(Fore.RED + f"        get_average_player_age() {tested}/{len(toTest)} -> {e}")
        
    # Testing get_average_player_height()
    tested = 0
    try:
        for teamID, _ in toTest:
            get_average_player_height(teamID, session)
            tested += 1
        print(Fore.GREEN + f"        get_average_player_height() {tested}/{len(toTest)} ✅")
    except Exception as e:
        print(Fore.RED + f"        get_average_player_height() {tested}/{len(toTest)} -> {e}")
        
    # Testing get_average_player_value()
    tested = 0
    try:
        for teamID, _ in toTest:
            get_average_player_value(teamID, session)
            tested += 1
        print(Fore.GREEN + f"        get_average_player_value() {tested}/{len(toTest)} ✅")
    except Exception as e:
        print(Fore.RED + f"        get_average_player_value() {tested}/{len(toTest)} -> {e}")
    
def test_playstyle(session):
    # Testing playstyle features
    print(Fore.MAGENTA + "    Playstyle:")

def get_session():
    engine = initPostgreSQL()
    Session = sessionmaker(engine)
    session = Session()
    print(Fore.GREEN + "Connected to database", end="\n\n")
    return session

if __name__ == "__main__":
    
    with get_session() as session:
    
        print(Fore.CYAN + "getInputs.py:")
        test_statistics(session)
        test_player_info(session)
        test_recent_form(session)
        test_h2h(session)