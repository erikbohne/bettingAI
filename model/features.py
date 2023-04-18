import os
import sys

sys.path.append(os.path.join("..", "googleCloud"))
from initPostgreSQL import initPostgreSQL

sys.path.append(os.path.join("..", "writer"))
from databaseClasses import *

from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

from getInputs import *


def main():
    
    # TODO Connect to database
    engine = initPostgreSQL()
    Base.metadata.bind = engine
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # TODO get a list of all teams
    teams = session.query(Teams).all()
    
    # TODO Extract features
    season = "2022-2023"
    features = []
    for team in teams:
        if team.league_id != 47: # focus in premier league for now
            continue
        
        # Init team features dict
        teamFeatures = {}
        teamFeatures["teamID"] = team.id
        teamFeatures["teamName"] = team.name
        
        # Get statistics from team and season
        for side in ["home", "away"]:
            teamFeatures[f"{side}_avg_{side}_goals"] = get_average_goals_season(team.id, season, side, session)
            teamFeatures[f"{side}_avg_conceded"] = get_average_conceded_season(team.id, season, side, session)
            teamFeatures[f"{side}_avg_goaldiff"] = get_average_goaldiff_season(team.id, season, side, session)
            for outcome in ["win", "draw", "loss"]:
                teamFeatures[f"{side}_{outcome}_rate"] = get_outcome_rate(team.id, season, side, outcome, session)
            teamFeatures[f"{side}_clean_sheet_rate"] = get_clean_sheet_rate(team.id, season, side, session)
        
        features.append(teamFeatures)
    
    for feature in features:
        print(feature)
        print("")
        


if __name__ == "__main__":
    main()