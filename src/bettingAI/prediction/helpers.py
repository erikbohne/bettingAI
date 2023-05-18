from typing import Dict, List, Tuple, Optional
import sqlalchemy
from sqlalchemy import text
import textdistance
import traceback
from datetime import datetime, timedelta
import tensorflow as tf
import numpy as np

from bettingAI.googleCloud.databaseClasses import Upcoming, Bets, Performance
from bettingAI.processing.features import features_for_model0
from bettingAI.writer.scraper import get_match_info


def add_match_to_bets(
    session: sqlalchemy.orm.Session, 
    match: object, 
    bet_type: str, 
    advice: str, 
    strength: float, 
    bookmaker_odds: list[float]
    ) -> None:
    """
    Add a match to the Bets table in the database.

    This function takes the provided match details, constructs a Bets object, 
    and then attempts to add it to the database. If an error occurs during this process,
    it will roll back the session and print the exception.

    Args:
        session (Session): SQLAlchemy Session object connected to the database.
        match (object): A match object with at least an attribute 'match_id'.
        bet_type (str): Type of the bet to be placed.
        advice (str): The advice for the bet.
        strength (float): The strength of the bet.
        bookmaker_odds (List[float]): A list of odds provided by the bookmaker for the bet.

    Returns:
        None
    """
    try:
        session.add(
        Bets(
        match_id=match.match_id,
        bet_type=bet_type,
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

def add_match_to_upcoming(
    session: sqlalchemy.orm.Session,
    match: object,
    inputs: list
    ) -> None:
    """
    Add a match to the Upcoming table in the database.

    This function takes the provided match and corresponding inputs, constructs an Upcoming 
    object, and then attempts to add it to the database. If an error occurs during this process,
    it will roll back the session and print the exception.

    Args:
        session (Session): SQLAlchemy Session object connected to the database.
        match (object): A match object with at least an attribute 'match_id'.
        inputs (List): A list of inputs for the upcoming match.

    Returns:
        None
    """
    try:
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
        
def calculate_advice_and_strength(
    match: object, 
    odds: list, 
    team_names: list, 
    model: tf.keras.Model, 
    session: sqlalchemy.orm.Session
    ) -> Tuple[
        Optional[str], 
        Optional[float], 
        Optional[List[float]]]:
    """
    Calculate the betting advice, strength, and bookmaker odds for a given match.

    Args:
        match (object): A match object containing details of a specific match.
        odds (List): A list of odds for the match.
        team_names (List): A list of team names for the match.
        model (tf.keras.Model): A TensorFlow model to predict the match outcome.
        session (sqlalchemy.orm.Session): SQLAlchemy Session object connected to the database.

    Returns:
        Tuple[Optional[str], Optional[float], Optional[List[float]]]: A tuple containing 
        advice (str or None), strength (float or None), and bookmaker odds (list of floats or None).
        Returns (None, None, None) if no matched odds are found.
    """
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

def calculate_real_odds(
    probabilities: List[float]
    ) -> List[float]:
    """
    Calculate real odds distribution based on the given probabilities.
    
    Args:
        probabilities (List[float]): A list of probabilities.

    Returns:
        List[float]: A list of real odds calculated from the given probabilities.
    """
    real_odds = []
    for probability in probabilities:
        real_odds.append(1 / probability)
    
    return real_odds

def find_value(
    real_odds: List[float], 
    bookmaker: List[float]
    ) -> Tuple[str, float]:
    """
    Determine the outcome with the highest expected value and its value.

    This function calculates the expected value of each possible outcome based on the 
    given real and bookmaker odds. It then returns the outcome with the highest 
    expected value, as well as the strength of the bet (calculated as the expected value).

    Args:
        real_odds (List[float]): A list of real odds. These represent the "true" odds 
        of each outcome, as determined by some model or other source of information.
        bookmaker (List[float]): A list of bookmaker odds. These are the odds being 
        offered by the bookmaker for each outcome.

    Returns:
        Tuple[str, float]: The outcome with the highest expected value (one of "H", "U", 
        or "B") and its value (a measure of the strength of the bet).
    """
    outcomes = ["H", "U", "B"]
    max_expected_value = 0
    max_expected_outcome = ""
    bet_strength = 0

    for real_odds, odds, outcome in zip(real_odds, bookmaker, outcomes):
        expected_value = (odds / real_odds)

        if expected_value > max_expected_value:
            max_expected_value = expected_value
            max_expected_outcome = outcome
            bet_strength = expected_value

    return max_expected_outcome, bet_strength

def get_bets_for_match(
    session: sqlalchemy.orm.Session,
    match_id: int
    ) -> List[object]:
    """
    Fetches the bets associated with a particular match from the database.

    This function queries the database for all bets placed on a specific match,
    identified by its match_id. It returns a list of all such bets.

    Args:
        session (sqlalchemy.orm.Session): The database session to use for the query.
        match_id (int): The ID of the match to fetch bets for.

    Returns:
        List[object]: A list of SQLAlchemy ResultProxy objects representing the bets
        associated with the specified match.
    """
    return session.execute(text(
        "SELECT id as id, strength as strength FROM bets WHERE match_id = :match_id;"
    ),
        {
            'match_id': match_id
        }
    ).fetchall()
    
def get_played_matches(
    session: sqlalchemy.orm.Session,
    two_hours_ago: datetime
    ) -> List[object]:
    """
    Fetches the matches that were played up to two hours ago from the database.

    This function queries the database for all matches that occurred up to two hours ago,
    as defined by the 'two_hours_ago' parameter. It returns a list of such matches.

    Args:
        session (sqlalchemy.orm.Session): The database session to use for the query.
        two_hours_ago (datetime): The datetime object representing the cutoff time for considering
                                   a match as having been 'played'.

    Returns:
        List[object]: A list of SQLAlchemy ResultProxy objects representing the matches
        that were played up to two hours ago.
    """
    return session.execute(text("""
        SELECT upcoming.match_id
        FROM upcoming
        JOIN schedule ON upcoming.match_id = schedule.match_id
        WHERE schedule.date <= :two_hours_ago
    """
    ), 
    {
        'two_hours_ago': two_hours_ago, 
    })

def get_team_names(
    session: sqlalchemy.orm.Session
    ) -> Dict[int, str]:
    """
    Fetches team names from the database and returns them as a dictionary.

    This function queries the database for team names, and returns a dictionary where 
    the keys are team IDs and the values are the corresponding team names.

    Args:
        session (Session): SQLAlchemy Session object connected to the database.

    Returns:
        Dict[int, str]: A dictionary where the keys are team IDs and the values are the 
        corresponding team names.
    """
    query = text("SELECT id, name FROM teams")
    result = session.execute(query)
    team_names = {}
    for row in result:
        team_names[row[0]] = row[1]
    return team_names

def get_upcoming_matches(
    session: sqlalchemy.orm.Session,
    today: datetime,
    delta: datetime
    ) -> List[object]:
    """
    Fetches the matches scheduled between 'today' and 'delta' days ahead from the database.

    This function queries the database for all matches that are scheduled to occur between 
    the current day (as defined by 'today') and a certain number of days ahead (as defined by 'delta'). 
    It returns a list of such matches.

    Args:
        session (sqlalchemy.orm.Session): The database session to use for the query.
        today (datetime): The datetime object representing the current day.
        delta (datetime): The datetime object representing the cutoff day for considering 
                          a match as 'upcoming'.

    Returns:
        List[object]: A list of SQLAlchemy ResultProxy objects representing the matches
        that are scheduled between 'today' and 'delta' days ahead.
    """
    return session.execute(text(
        "SELECT * FROM schedule WHERE date >= :today AND date <= :delta;"
    ), 
    {
        'today': today, 
        'delta': delta
    })
    
def get_upcoming_match_ids(
    session: sqlalchemy.orm.Session
    ) -> List[int]:
    """
    Fetches all match IDs from the 'Upcoming' table in the database.

    This function performs a query to the database to retrieve all match IDs 
    present in the 'Upcoming' table and returns them as a list of integers.

    Args:
        session (sqlalchemy.orm.Session): The database session to use for the query.

    Returns:
        List[int]: A list of integers representing all match IDs in the 'Upcoming' table.
    """
    return set([match[0] for match in session.execute(text(
        "SELECT match_id FROM upcoming;"
    )).fetchall()])  # Format the queried ids

def match_team_names(
    team1: str,
    team2: str,
    threshold: float = 0.7
    ) -> bool:
    """
    Checks if two team names are similar based on a set threshold.

    This function calculates the Jaro-Winkler similarity between two team names. 
    If the calculated similarity is greater than or equal to the given threshold, 
    the function returns True, indicating the two team names are considered similar. 
    Otherwise, it returns False.

    Args:
        team1 (str): The name of the first team.
        team2 (str): The name of the second team.
        threshold (float, optional): The similarity threshold. Defaults to 0.7.

    Returns:
        bool: True if the team names are considered similar, False otherwise.
    """
    similarity = textdistance.jaro_winkler(team1.lower(), team2.lower())
    return similarity >= threshold

def remove_played_matches(
    session: sqlalchemy.orm.Session
    ) -> None:
    """
    Clean up the 'Upcoming' table by removing matches that have already been played and 
    migrating them to the 'Performance' table in the database.

    The function identifies matches that have taken place up to two hours ago and are still 
    present in the 'Upcoming' table. For each such match, it retrieves the associated bets, 
    determines the outcome of these bets based on the actual match result, and then creates 
    corresponding records in the 'Performance' table. The entries for these matches are then 
    deleted from both the 'Upcoming' and 'Bets' tables.

    Args:
        session (sqlalchemy.orm.Session): The SQLAlchemy Session object for database interaction.

    Returns:
        None
    """
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

def update_bets(
    session: sqlalchemy.orm.Session, 
    bet: object, 
    advice: str, 
    strength: float, 
    bookmaker_odds: list[float]
    ) -> None:
    """
    Update existing bet records in the Bets table.

    This function updates the odds, advice, strength, and change in strength of a given bet 
    in the Bets table of the database, based on the provided parameters.

    Args:
        session (sqlalchemy.orm.Session): The SQLAlchemy Session object for database interaction.
        bet (object): The bet record to be updated.
        advice (str): The updated advice for the bet.
        strength (float): The updated strength value for the bet.
        bookmaker_odds (list[float]): The updated odds from the bookmaker.

    Returns:
        None
    """
    try:
        session.execute(text(
            "UPDATE bets SET odds = :new_odds, value = :value, strength = :new_strength, change =:change WHERE id = :bet_id;"
        ),
            {
                'value': advice,
                'new_strength': round(strength, 2),
                'new_odds': bookmaker_odds,
                'bet_id': bet.id,
                'change': round((strength - bet.strength), 2)
            }
        )
        session.commit()
    except Exception as e:
        session.rollback()
        print(e)
        traceback.print_exc()