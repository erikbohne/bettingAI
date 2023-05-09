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

from datetime import datetime
import numpy as np

odds = [1.97, 3.75, 3.40]

def main(session):
    #model = load_model('../model/models/model4.h5') # import model
    #inputs = features_for_model0(int(8456), int(8654), "2022-2023", "home", datetime(year=2023, month=5, day=3), session)
    #input_data = np.array(inputs).reshape(1, -1)  # Reshape the input data into the expected format
    #probabilities = model.predict(input_data)
    #real_odds = calculate_real_odds(probabilities[0])
    #print(real_odds)
    #exit()

    # TODO Find matches one week ahead of time
    links, matches = [], []
    for id, season in [(47, "2022-2023"), (59, "2023")]:
        links += get_match_links(id, season)
    

    for link in tqdm(links):
        info = get_next_match_info(link)
        if type(info) == dict:
            matchID = link.split("/")[2]
            matches.append([matchID, info["teamID"], info["opponentID"], "2022-2023", "home", info["date"]])
    
    # Process the date for prediction
    inputs = {} # init the dict to store inputs
    for matchID, teamID, opponentID, season, side, date in matches:
        inputs[matchID] = {}
        inputs[matchID]["info"] = {
            "teamID": teamID,
            "opponentID": opponentID,
            "date": date
        }
        inputs[matchID]["features"] = features_for_model0(int(teamID), int(opponentID), season, side, date, session)
    
    # Predict and label
    model = load_model('../model/models/model2.h5') # import model
    
    for match in inputs.keys(): # iterate over each match
        input_data = np.array(inputs[match]["features"]).reshape(1, -1)  # Reshape the input data into the expected format
        probabilities = model.predict(input_data)
        real_odds = calculate_real_odds(probabilities[0])
                
        # Compare and find value in Norsk Tipping Odds
        #advice = find_value(real_odds, odds)
        
        try:
            upcoming = Upcoming(
                date=inputs[match]["info"]["date"],
                match_id=match,
                home_team_id=inputs[match]["info"]["teamID"],
                away_team_id=inputs[match]["info"]["opponentID"],
                h=round(real_odds[0], 2),
                u=round(real_odds[1], 2),
                b=round(real_odds[2], 2),
                value="NO VALUE",
            )
            session.add(upcoming)
            session.commit()
        except Exception as e:
            session.rollback()
            print(e)
        
if __name__ == "__main__":
    session = initSession()
    main(session)