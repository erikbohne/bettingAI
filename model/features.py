import os
import sys

sys.path.append(os.path.join("..", "googleCloud"))
from initPostgreSQL import initPostgreSQL

sys.path.append(os.path.join("..", "writer"))
from databaseClasses import *

from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from datetime import datetime

from getInputs import *


def features(session, match):
  
    # Init team features dict
    teamFeatures = {}
    teamFeatures["teamID"] = match.get("teamID")
    teamFeatures["opponentID"] = match.get("opponentID")
    
    # Get player info
    teamFeatures["home_player_rating"] = get_average_player_rating(match.get("teamID"), session)
    teamFeatures["away_player_rating"] = get_average_player_rating(match.get("opponentID"), session)
    teamFeatures["home_player_age"] = get_average_player_age(match.get("teamID"), session)
    teamFeatures["away_player_age"] = get_average_player_age(match.get("opponentID"), session)
    teamFeatures["home_player_height"] = get_average_player_height(match.get("teamID"), session)
    teamFeatures["away_player_height"] = get_average_player_height(match.get("opponentID"), session)
    teamFeatures["home_player_value"] = get_average_player_value(match.get("teamID"), session)
    teamFeatures["away_player_value"] = get_average_player_value(match.get("opponentID"), session)
    
    # Get recent form statistics from teams
    teamFeatures["home_points_rate"] = get_points_won_ratio(match.get("teamID"), match.get("date"), session)
    teamFeatures["away_points_rate"] = get_points_won_ratio(match.get("opponentID"), match.get("date"), session)
    teamFeatures["home_outcome_streak"] = get_outcome_streak(match.get("teamID"), match.get("date"), session)
    teamFeatures["away_outcome_streak"] = get_outcome_streak(match.get("opponentID"), match.get("date"), session)
    teamFeatures["home_side_form"] = get_home_away_form(match.get("teamID"), "home", match.get("date"), session)
    teamFeatures["away_side_form"] = get_home_away_form(match.get("opponentID"), "away", match.get("date"), session)
    
    
    # Get h2h statistics from teams
    teamFeatures["outcome_distribution"] = get_outcome_distribution(match.get("teamID"), match.get("opponentID"), match.get("date"), session)
    teamFeatures["side_distribtuion"] = get_side_distribution(match.get("teamID"), match.get("opponentID"), match.get("date"), session)
    teamFeatures["recent_encounters"] = get_recent_encounters(match.get("teamID"), match.get("opponentID"), match.get("date"), session)
    teamFeatures["average_goals_per_match"] = get_average_goals_per_match(match.get("teamID"), match.get("opponentID"), match.get("date"), session)
    teamFeatures["average_goals_conceded_per_match"] = get_average_goals_conceded_per_match(match.get("teamId"), match.get("opponentID"), match.get("date"), session)
    teamFeatures["average_goal_difference"] = get_average_goal_difference_match(match.get("teamID"), match.get("opponentID"), match.get("date"), session)
    teamFeatures["btts_rate"] = get_btts_rate(match.get("teamID"), match.get("opponentID"), match.get("date"), session)
    teamFeatures["clean_sheet_rate_h2h"] = get_clean_sheet_rate_h2h(match.get("teamID"), match.get("opponentID"), match.get("date"), session)
    teamFeatures["over_under_2_5"] = get_over_under_2_5(match.get("teamID"), match.get("opponentID"), match.get("date"), session)
    teamFeatures["outcome_streak_h2h"] = get_outcome_streak_h2h(match.get("teamID"), match.get("opponentID"), match.get("date"), session)

    
    return teamFeatures
        


if __name__ == "__main__":
    
    # Connect to database
    engine = initPostgreSQL()
    Base.metadata.bind = engine
    Session = sessionmaker(bind=engine)
    session = Session()
    
    test1 = {
        "teamID" : 8456,
        "opponentID" : 9825,
        "date" : datetime(year=2023, month=4, day=26)
    }
    
    test = features(session, test1)
    
    for key in test.keys():
        print(key, test[key])