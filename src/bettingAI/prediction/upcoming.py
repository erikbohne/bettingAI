""" 
Program that runs every 24 hours to update the predictions and upcoming matches
"""
from bettingAI.googleCloud.initPostgreSQL import initSession
from bettingAI.writer.databaseClasses import Upcoming, Bets
from bettingAI.processing.features import features_for_model0
from sqlalchemy import text

from tensorflow.keras.models import load_model

# Odds API
from bettingAI.oddsapi.odds import get_odds

import traceback
import copy
import numpy as np
from datetime import datetime, timedelta
from helpers import * # Must be updated to -> from bettingAI.prediction.helpers import *


def upcoming(session, model):
    
    # Find matches 5 days in ahead of time
    today = datetime.today()
    delta = today + timedelta(days=5)
    matches = session.execute(text(
        "SELECT * FROM schedule WHERE date >= :today AND date <= :delta;"
    ), 
    {
        'today': today, 
        'delta': delta
    })
    
    # Get a list of all match_ids in the Upcoming table
    upcoming_matches = session.execute(text(
        "SELECT match_id FROM upcoming;"
    )).fetchall()
    upcoming_matches = set([match[0] for match in upcoming_matches]) # Format the queried ids
    
    team_names = get_team_names(session)
    
    # Extract all distinct league_id values from matches
    #distinct_league_ids = list(set([match.league_id for match in matches]))
    distinct_league_ids = [47]
    # Get the live odds for all the leagues we need odds for
    live_odds = {}
    for league_id in distinct_league_ids:
        live_odds[league_id] = get_odds(str(league_id))

    for match in matches:
        if match.match_id in upcoming_matches:
            # Check if the match is still in the future
            if match.date > datetime.today():
                # Check if we can update the bets for the match
                betID = session.execute(text(
                    "SELECT id FROM bets WHERE match_id = :match_id;"
                ),
                    {
                        'match_id': match.match_id
                    }
                ).fetchall()
                
                advice, strength, bookmaker_odds = calculate_advice_and_strength(
                    match,
                    live_odds[match.league_id],
                    team_names,
                    model,
                    session,
                    )
                
                try:
                    session.execute(text(
                        "UPDATE bets SET odds = :new_odds, value = :value, strength = :new_strength WHERE id = :bet_id;"
                    ),
                        {
                            'value': advice,
                            'new_strength': round(strength, 2),
                            'new_odds': bookmaker_odds,
                            'bet_id': betID[0][0]
                        }
                    )
                    session.commit()
                except Exception as e:
                    session.rollback()
                    print(e)
                    traceback.print_exc()
                    
            else:
                # Find the result of the match
                # Implement the logic to find the match result

                # Add match predictions to the predictions database
                # Implement the logic to add predictions to the database
                pass
        else:
            # Add match to Upcoming
            inputs = features_for_model0(
                        int(match.home_team_id), 
                        int(match.away_team_id), 
                        match.season, 
                        "home", 
                        match.date, 
                        session
                        )
            try: # add to Upcoming table
                session.add(
                    Upcoming(
                    match_id=match.match_id,
                    inputs=inputs
                    )
                )
                session.commit()
            except Exception as e:
                session.rollback()
                print(e)
                traceback.print_exc()
            
            # Add match to Bets
            for type in ["HUB"]:
                advice, strength, bookmaker_odds = calculate_advice_and_strength(
                    match,
                    live_odds[match.league_id],
                    team_names,
                    model,
                    session
                    )

                if advice is not None and strength is not None:
                    
                    try: # add match to Bets table
                        session.add(
                            Bets(
                            match_id=match.match_id,
                            bet_type=type,
                            odds=bookmaker_odds,
                            value=advice,
                            strength=strength
                            )
                        )
                        session.commit()
                    except Exception as e:
                        session.rollback()
                        print(e)
                        traceback.print_exc()
    print("Added and updated upcoming matches :D")
                
def calculate_advice_and_strength(match: object, odds: list, team_names: list, model: object, session: object):
    input_data = np.array(
        features_for_model0(
            int(match.home_team_id),
            int(match.away_team_id),
            match.season,
            "home",
            match.date,
            session
        )
    ).reshape(1, -1)  # Reshape the input data into the expected format

    probabilities = model.predict(input_data)
    real_odds = calculate_real_odds(probabilities[0])

    # Get the team names from the team IDs
    home_team_name = team_names[int(match.home_team_id)]
    away_team_name = team_names[int(match.away_team_id)]

    matched_odds = None
    for match_name, unibet_odds in odds.items():
        team1, team2 = match_name.split(" vs ")
        if match_team_names(home_team_name, team1) and match_team_names(away_team_name, team2):
            matched_odds = unibet_odds
            break

    if matched_odds:
        advice, strength = find_value(real_odds, [matched_odds['h'], matched_odds['d'], matched_odds['a']])
    else:
        return None, None, None

    return advice, strength, [matched_odds['h'], matched_odds['d'], matched_odds['a']]


if __name__ == "__main__":
    
    # import model
    model = load_model('../model/models/model2.h5')
    
    # initialize session with db
    session = initSession()
    
    # run program
    upcoming(session, model)