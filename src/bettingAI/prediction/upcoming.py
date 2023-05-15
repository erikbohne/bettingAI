""" 
Program that runs every 24 hours to update the predictions and upcoming matches
"""
from bettingAI.googleCloud.initPostgreSQL import initSession
from bettingAI.writer.databaseClasses import Upcoming, Bets, Performance
from bettingAI.processing.features import features_for_model0
from bettingAI.writer.scraper import get_match_info
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
    distinct_league_ids = [47, 53, 54, 55, 59]
    # Get the live odds for all the leagues we need odds for
    live_odds = {}
    for league_id in distinct_league_ids:
        live_odds[league_id] = get_odds(str(league_id))

    for match in matches:
        if match.league_id == 87 or match.league_id is None:
            continue
        if match.match_id in upcoming_matches:
            # Check if we can update the bets for the match
            bets = session.execute(text(
                "SELECT id as id, strength as strength FROM bets WHERE match_id = :match_id;"
            ),
                {
                    'match_id': match.match_id
                }
            ).fetchall()
            
            if len(bets) == 0: # if an upcoming match doesnt have a bet prediction
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
                                strength=round(strength, 2),
                                change=1.00
                                )
                            )
                            session.commit()
                        except Exception as e:
                            session.rollback()
                            print(e)
                            traceback.print_exc()
                
            for bet in bets:
                advice, strength, bookmaker_odds = calculate_advice_and_strength(
                    match,
                    live_odds[match.league_id],
                    team_names,
                    model,
                    session,
                    )
                if advice is None:
                    continue
                try:
                    session.execute(text(
                        "UPDATE bets SET odds = :new_odds, value = :value, strength = :new_strength, change =:change WHERE id = :bet_id;"
                    ),
                        {
                            'value': advice,
                            'new_strength': round(strength, 2),
                            'new_odds': bookmaker_odds,
                            'bet_id': bet.id,
                            'change': round((bet.strength - strength), 2)
                        }
                    )
                    session.commit()
                except Exception as e:
                    session.rollback()
                    print(e)
                    traceback.print_exc()
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
                            strength=round(strength, 2),
                            change=1.00
                            )
                        )
                        session.commit()
                    except Exception as e:
                        session.rollback()
                        print(e)
                        traceback.print_exc()
    print("Done adding and updating")
    
    # Find potential matches that are in upcoming table, but played
    two_hours_ago = datetime.now() - timedelta(hours=2)
    
    played_matches = session.execute(text("""
        SELECT upcoming.match_id
        FROM upcoming
        JOIN schedule ON upcoming.match_id = schedule.match_id
        WHERE schedule.date <= :two_hours_ago
    """
    ), 
    {
        'two_hours_ago': two_hours_ago, 
    })
    
    # Query for all betting tips on that match
    for match in played_matches:
        print(match.match_id)
        bets = session.execute(text(
            "SELECT id as id, bet_type as type, odds as odds, value as value FROM bets WHERE match_id = :match_id;"),
            {
                'match_id': match.match_id
            }
        ).fetchall()
        
        # Get the result of the match
        result = get_match_info(f"/match/{match.match_id}", justMain=True)
        
        for bet in bets: # iterate through all betting tips for that match

            if bet.type == "HUB":
                if result["homescore"] > result["awayscore"]:
                    HUB = "H"
                elif result["homescore"] == result["awayscore"]:
                    HUB = "U"
                else:
                    HUB = "B"

            outcome = True if bet.value == HUB else False

            # Add match predictions to the predictions database
            try:
                session.add(Performance(
                    match_id=match.match_id,
                    model_id=0,
                    bet_type=bet.type,
                    bet_outcome=bet.value,
                    odds=bet.odds,
                    placed=250,
                    outcome=outcome
                ))
                session.execute(text(
                    "DELETE FROM bets WHERE id = :id AND bet_type = :type;"),
                    {
                        'id': bet.id,
                        'type': bet.type
                    }
                )
                session.commit()
            except Exception as e:
                session.rollback()
                print(e)
                traceback.print_exc()
        
        # Remove match from Upcoming
        session.execute(text(
            "DELETE FROM upcoming WHERE match_id = :match_id;"),
            {
                'match_id': match.match_id
            }
        )
        session.commit()
        session.close()
    print("Done removing played matches and placing them to the performance table")
                
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