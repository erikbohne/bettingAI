"""
Program to get info about upcoming matches
"""
from bettingAI.googleCloud.initPostgreSQL import initSession
from bettingAI.writer.scraper import get_match_links, get_next_match_info
from bettingAI.processing.features import features_for_model0
from tensorflow.keras.models import load_model
from tqdm.auto import tqdm
from helpers import *

from datetime import datetime
import numpy as np

odds = [1.97, 3.75, 3.40]

def main(session):

    # TODO Find matches one week ahead of time
    matches = []
    links = get_match_links(47, "2022-2023")
    

    for link in tqdm(links):
        info = get_next_match_info(link)
        if type(info) == dict:
            matchID = link.split("/")[2]
            matches.append([matchID, info["teamID"], info["opponentID"], "2022-2023", "home", info["date"]])
    
    # Process the date for prediction
    inputs = {} # init the dict to store inputs
    for matchID, teamID, opponentID, season, side, date in matches:
        inputs[matchID] = features_for_model0(int(teamID), int(opponentID), season, side, date, session)
    
    # Predict and label
    model = load_model('../model/models/model.h5') # import model
    
    for match in inputs.keys(): # iterate over each match
        input_data = np.array(inputs[match]).reshape(1, -1)  # Reshape the input data into the expected format
        probabilities = model.predict(input_data)
        real_odds = calculate_real_odds(probabilities[0])
                
        # Compare and find value in Norsk Tipping Odds
        advice = find_value(real_odds, odds)
        
        print(f"{match}")
        print(probabilities[0])
        print(real_odds)
        for i, recommendation in enumerate(advice):
            print(f"    {odds[i]} -> {recommendation}")
        print("")
        
if __name__ == "__main__":
    session = initSession()
    main(session)