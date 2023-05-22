from typing import Any, List, Union
import sqlalchemy

from bettingAI.googleCloud.databaseClasses import *
from bettingAI.processing.getInputs import *
from bettingAI.processing.queries import *


def features_for_model0(
    teamID: int,
    opponentID: int,
    season: str,
    thisSide: str,
    date: str,
    session: Any
) -> List[float]:
    """Returns all the features needed from a match for model0 training.

    Parameters:
    - teamID (int): The ID of the team.
    - opponentID (int): The ID of the opponent team.
    - season (str): The season of the match.
    - thisSide (str): The side of the team (home or away).
    - date (str): The date of the match.
    - session (Any): SQLAlchemy session object for interacting with the database.

    Returns:
    - features (List[float]): A list of float values representing the features.
    """
    otherSide = "away" if thisSide == "home" else "home"

    # Init team features
    teamFeatures = {}

    # Season stats teamID, season, side, date, session
    team_ids = [teamID, opponentID]
    sides = [thisSide, otherSide]
    features = get_combined_team_stats(team_ids, season, sides, date, session)

    # Recent form
    matches = query_recent_form(teamID, opponentID, date, session)
    (
        teamFeatures["team_points_rate_3"],
        teamFeatures["team_points_rate_5"],
        teamFeatures["team_points_rate_10"],
    ) = get_points_won_ratio(teamID, matches)
    (
        teamFeatures["opponent_points_rate_3"],
        teamFeatures["opponent_points_rate_5"],
        teamFeatures["opponent_points_rate_10"],
    ) = get_points_won_ratio(opponentID, matches)

    teamFeatures["team_outcome_streak"] = get_outcome_streak(teamID, matches)
    teamFeatures["opponent_outcome_streak"] = get_outcome_streak(opponentID, matches)

    teamFeatures["home_side_form"] = get_home_away_form(teamID, thisSide, matches)
    teamFeatures["away_side_form"] = get_home_away_form(opponentID, otherSide, matches)

    # H2H
    matches = query_H2H(teamID, opponentID, date, session)
    outcomes = get_outcome_distribution(teamID, matches)
    (
        teamFeatures["outcome_win"],
        teamFeatures["outcome_draw"],
        teamFeatures["outcome_loss"],
    ) = (outcomes["win"], outcomes["draw"], outcomes["loss"])
    teamFeatures["side_distribtuion"] = get_side_distribution(teamID, thisSide, matches)
    teamFeatures["recent_encounters"] = get_recent_encounters(teamID, date, matches)
    teamFeatures["average_goals_per_match"] = get_average_goals_per_match(matches)
    teamFeatures[
        "average_goals_conceded_per_match"
    ] = get_average_goals_conceded_per_match(teamID, matches)
    teamFeatures["average_goal_difference"] = get_average_goal_difference_match(
        teamID, matches
    )
    teamFeatures["btts_rate"] = get_btts_rate(matches)
    teamFeatures["clean_sheet_rate_h2h"] = get_clean_sheet_rate_h2h(teamID, matches)
    teamFeatures["over_under_2_5"] = get_over_under_2_5(matches)
    teamFeatures["outcome_streak_h2h"] = get_outcome_streak_h2h(teamID, matches)

    for key in teamFeatures.keys():
        features.append(teamFeatures[key])

    return features

def features_for_model1(
    teamID: int,
    opponentID: int,
    leagueID: int,
    season: str,
    thisSide: str,
    match_date: str,
    session: Any
) -> List[float]:
        
    otherSide = "away" if thisSide == "home" else "home"

    # 0-3 MATCH INFO
    features = [1] if thisSide == "home" else [0] # init features list with home/away
    features += get_match_info(teamID, opponentID, leagueID, match_date, season, session)
    
    # 4-27 SEASON STATS
    team_ids = [teamID, opponentID]
    sides = [thisSide, otherSide]
    features += get_combined_team_stats(team_ids, season, sides, match_date, session)
    
    # 28-61 RECENT FORM
    features += get_recent_stats(teamID, opponentID, season, match_date, session)
    
    # 62-79 H2H
    
    # 80-83 TIME AND DATE
    
    # 84-95 LEAGUE STATISTICS
    
    # 96-110 CONDITION
    
    
    
    return features

def labels(matchID: int,
           team_id: int,
           session: sqlalchemy.orm.Session
) -> List[int]:
    """Returns the labels for the match.

    Parameters:
    - matchID (int): The ID of the match.
    - team_id (int): The ID of the team.
    - session (Session): SQLAlchemy session object for interacting with the database.

    Returns:
    - labels (List[int]): A list of integer labels indicating the match outcomes.
        The labels are as follows:
        - team_win: 1 if the team won, 0 otherwise.
        - draw: 1 if the match ended in a draw, 0 otherwise.
        - team_loss: 1 if the team lost, 0 otherwise.
        - over1_5: 1 if the total goals scored in the match is over 1.5, 0 otherwise.
        - over2_5: 1 if the total goals scored in the match is over 2.5, 0 otherwise.
        - over3_5: 1 if the total goals scored in the match is over 3.5, 0 otherwise.
        - over4_5: 1 if the total goals scored in the match is over 4.5, 0 otherwise.
        - btts: 1 if both teams scored in the match, 0 otherwise.

    """
    # Query the Matches table for the match with the given matchID
    match = session.query(Matches).filter(Matches.id == matchID).one()

    home_goals = match.home_goals
    away_goals = match.away_goals

    if team_id == match.home_team_id:
        team_win = int(home_goals > away_goals)
        team_loss = int(home_goals < away_goals)
    elif team_id == match.away_team_id:
        team_win = int(home_goals < away_goals)
        team_loss = int(home_goals > away_goals)
    else:
        raise ValueError("Invalid team_id. Must be either home_team_id or away_team_id.")

    draw = int(home_goals == away_goals)
    over1_5 = int(home_goals + away_goals > 1.5)
    over2_5 = int(home_goals + away_goals > 2.5)
    over3_5 = int(home_goals + away_goals > 3.5)
    over4_5 = int(home_goals + away_goals > 4.5)
    btts = int(home_goals > 0 and away_goals > 0)

    return [team_win, draw, team_loss, over1_5, over2_5, over3_5, over4_5, btts]


if __name__ == "__main__":
    raise SyntaxError("features.py is only a file containing feature extraction functions.")
