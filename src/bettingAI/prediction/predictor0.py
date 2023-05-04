"""
Program to test model0 on round 27 in Premier League 2023
"""
from bettingAI.googleCloud.initPostgreSQL import initSession
from tensorflow.keras.models import load_model
import matplotlib.pyplot as plt
from sqlalchemy import text
import numpy as np
import json

def main(model, session):
    
    with open("odds_pl_22_23.json") as f:
        rounds = json.load(f)
    rounds = rounds["ROUNDS"]
    
    placed_bets = 0
    bet_won = 0
    money_won = 0
    history = []
    
    for round in rounds:
        
        for match in rounds[round]:
            # Retrieve the input features for the match
            match_input = session.execute(text(f"SELECT inputs FROM processed_for_model0 WHERE match_id = {match}")).first()

            if match_input:
            
                # Calculate probabilities using the pre-trained model
                input_data = np.array(match_input[0]).reshape(1, -1)  # Reshape the input data into the expected format
                probabilities = model.predict(input_data)  # Get the predicted probabilities for the match
                real_odds = calculate_real_odds(probabilities[0])
                
                # Compare and find value in Norsk Tipping Odds
                advice = find_value(real_odds, rounds[round][match][:3])
                
                for i, recommendation in enumerate(advice):
                    if recommendation == "Value":
                        placed_bets += 1
                        
                        if rounds[round][match][3] == i:
                            bet_won += 1
                            money_won += (rounds[round][match][i] - 1) * 250
                            print(match, rounds[round][match][i])
                        else:
                            money_won -= 250
                        
                        history.append(money_won)   
    #print(history)                   
    print(f"Result -> {placed_bets} ({(bet_won / placed_bets):.2f}) and balance {money_won}")
            
            
if __name__ == "__main__":
    session = initSession()
    model = load_model('../model/models/model.h5')
    main(model, session)