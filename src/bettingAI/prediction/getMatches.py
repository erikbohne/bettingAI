"""
Program to get info about upcoming matches
"""
from bettingAI.googleCloud.initPostgreSQL import initSession
from bettingAI.writer.scraper import get_match_links, get_next_match_info
from bettingAI.processing.features import features_for_model0
from bettingAI.writer.databaseClasses import Upcoming
from tensorflow.keras.models import load_model
from tqdm.auto import tqdm
from helpers import *

# Odds API
from bettingAI.oddsapi.odds import get_odds

from datetime import datetime
import numpy as np
import traceback

odds = [1.97, 3.75, 3.40]

def main(session):

    # Find matches one week ahead of time
    links, matches = [], []
    for id, season in [(47, "2022-2023")]:
        links += get_match_links(id, season)
    

    for link in tqdm(links):
        info = get_next_match_info(link)
        if type(info) == dict:
            matchID = link.split("/")[2]
            matches.append([info["leagueID"], matchID, info["teamID"], info["opponentID"], "2022-2023", "home", info["date"]])
    
    # Process the date for prediction
    inputs = {} # init the dict to store inputs
    for leagueID, matchID, teamID, opponentID, season, side, date in matches:
        inputs[matchID] = {}
        inputs[matchID]["info"] = {
            "leagueID": leagueID,
            "teamID": teamID,
            "opponentID": opponentID,
            "date": date
        }
        inputs[matchID]["features"] = features_for_model0(int(teamID), int(opponentID), season, side, date, session)
    
    # Predict and label
    model = load_model('../model/models/model2.h5') # import model
    
    odds = {}
    for leagueID in ["47"]:
        odds[leagueID] = get_odds(leagueID)
        
    team_names = get_team_names(session)
    
    for match in inputs.keys(): # iterate over each match
        input_data = np.array(inputs[match]["features"]).reshape(1, -1)  # Reshape the input data into the expected format
        probabilities = model.predict(input_data)
        real_odds = calculate_real_odds(probabilities[0])
        
        
        # Get the team names from the team IDs
        home_team_name = team_names[int(inputs[match]["info"]["teamID"])]
        away_team_name = team_names[int(inputs[match]["info"]["opponentID"])]
        
        matched_odds = None
        for match_name, unibet_odds in odds[inputs[match]["info"]["leagueID"]].items():
            team1, team2 = match_name.split(" vs ")
            if match_team_names(home_team_name, team1) and match_team_names(away_team_name, team2):
                matched_odds = unibet_odds
                break
                
        if matched_odds:
            advice, strength = find_value(real_odds, [matched_odds['h'], matched_odds['d'], matched_odds['a']])
        else:
            continue
        
        try:
            upcoming = Upcoming(
                date=inputs[match]["info"]["date"],
                league_id=inputs[match]["info"]["leagueID"],
                match_id=match,
                home_team_id=inputs[match]["info"]["teamID"],
                away_team_id=inputs[match]["info"]["opponentID"],
                h=round(matched_odds['h'], 2),
                u=round(matched_odds['d'], 2),
                b=round(matched_odds['a'], 2),
                strength=round(strength, 2),
                value=advice,
            )
            session.add(upcoming)
            session.commit()
        except Exception as e:
            session.rollback()
            print(e)
            traceback.print_exc()
        
if __name__ == "__main__":
    session = initSession()
    main(session)