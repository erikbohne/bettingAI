"""
Program that runs every 24 hours to update the predictions and upcoming matches using model 1
"""
from typing import List
from datetime import datetime, timedelta

import sqlalchemy
import tensorflow as tf
from tensorflow.keras.models import load_model

from bettingAI.googleCloud.initPostgreSQL import initSession
from bettingAI.processing.features import features_for_model0, features_for_model1
from bettingAI.oddsapi.odds import get_odds
from bettingAI.prediction.helpers import *

def upcoming(
    session: sqlalchemy.orm.Session,
    model: tf.keras.Model
) -> None:
    """
    Update the 'Upcoming' and 'Bets' tables in the database with match predictions for upcoming games.

    This function identifies matches scheduled for the next five days and updates their corresponding records 
    in the 'Upcoming' and 'Bets' tables. If a match is already listed in the 'Upcoming' table, the function 
    checks if there are existing bet predictions for it. If there are, it updates these predictions; if not, 
    it creates new ones. If a match is not yet listed in the 'Upcoming' table, the function adds it, along 
    with the corresponding bet predictions.

    Once all updates and additions have been made, the function calls `remove_played_matches` to clean up 
    the 'Upcoming' table by removing matches that have already been played and migrating them to the 
    'Performance' table.

    Args:
        session (sqlalchemy.orm.Session): The SQLAlchemy Session object for database interaction.
        model (tf.keras.Model): The TensorFlow Keras model to be used for match predictions.

    Returns:
        None
    """
    # Find matches 5 days in ahead of time
    today = datetime.today()
    delta = today + timedelta(days=5)
    matches = get_upcoming_matches(session, today, delta)

    # Get a list of all match_ids in the Upcoming table
    upcoming_matches = get_upcoming_match_ids(session)

    team_names = get_team_names(session)

    # Extract all distinct league_id values from matches
    distinct_league_ids = [47, 53, 54, 55, 59]
    
    # Get the live odds for all the leagues we need odds for
    live_odds = {league_id: get_odds(str(league_id)) for league_id in distinct_league_ids}
    timestamp = datetime.now()

    # Iterate over matches
    for match in matches:
        if match.league_id == 87 or match.league_id is None:
            continue
        if match.match_id in upcoming_matches:
            # Check if we can update the bets for the match
            bets = get_bets_for_match(session, match.match_id, 1)
            if len(bets) == 0:  # if an upcoming match doesn't have a bet prediction
                # Add match to Bets
                for type in ["HUB"]:
                    advice, strength, bookmaker_odds, real_odds, probabilities, kelly = calculate_advice_and_strength(
                        match,
                        live_odds[match.league_id],
                        team_names,
                        model,
                        1,
                        session
                    )

                    if advice is not None and strength is not None:
                        add_match_to_bets(
                            session, 
                            match, 
                            1, 
                            type, 
                            advice, 
                            strength, 
                            bookmaker_odds,
                            real_odds,
                            probabilities,
                            kelly
                        )
                        track_odds(
                            session,
                            1,
                            timestamp, 
                            match.match_id, 
                            type, 
                            advice, 
                            strength, 
                            bookmaker_odds, 
                            real_odds, 
                            probabilities, 
                            kelly
                        )
                
            for bet in bets:
                advice, strength, bookmaker_odds, real_odds, probabilities, kelly = calculate_advice_and_strength(
                    match,
                    live_odds[match.league_id],
                    team_names,
                    model,
                    1,
                    session,
                    )
                if advice is None:
                    continue
                
                update_bets(
                    session, 
                    bet, 
                    advice, 
                    strength, 
                    bookmaker_odds,
                    real_odds,
                    probabilities,
                    kelly
                )
                track_odds(
                            session,
                            1,
                            timestamp, 
                            match.match_id, 
                            bet.type, 
                            advice, 
                            strength, 
                            bookmaker_odds, 
                            real_odds, 
                            probabilities, 
                            kelly
                        )
        else:
            # Add match to Upcoming
            inputs0 = features_for_model0(
                        int(match.home_team_id), 
                        int(match.away_team_id), 
                        match.season, 
                        "home", 
                        match.date, 
                        session
                        )
            inputs1 = features_for_model1(
                        int(match.home_team_id), 
                        int(match.away_team_id), 
                        match.league_id, 
                        match.season,
                        "home", 
                        match.date, 
                        session
                        )
            add_match_to_upcoming(session, match, inputs0, inputs1)
        
            # Add match to Bets
            for type in ["HUB"]:
                advice, strength, bookmaker_odds, real_odds, probabilities, kelly = calculate_advice_and_strength(
                    match,
                    live_odds[match.league_id],
                    team_names,
                    model,
                    1,
                    session
                    )

                if advice is not None and strength is not None:
                    add_match_to_bets(
                            session, 
                            match, 
                            1, 
                            type, 
                            advice, 
                            strength, 
                            bookmaker_odds,
                            real_odds,
                            probabilities,
                            kelly
                        )
                    track_odds(
                            session,
                            1,
                            timestamp, 
                            match.match_id, 
                            type, 
                            advice, 
                            strength, 
                            bookmaker_odds, 
                            real_odds, 
                            probabilities, 
                            kelly
                        )

    print("Done adding and updating")
    exit()
    remove_played_matches(session)
    print("Done removing played matches and placing them to the performance table")
    
if __name__ == "__main__":
    # import models
    model1 = load_model('../model/models/model1.h5')

    # initialize session with db
    session = initSession()

    # run program
    upcoming(session, model1)