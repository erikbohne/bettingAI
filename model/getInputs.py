import os
import sys

sys.path.append(os.path.join("..", "writer"))
from databaseClasses import *

from sqlalchemy.sql import func
from sqlalchemy import and_, or_


def get_average_goals_season(teamID, season, side, session):
    """
    Returns average goals for a team in a given season based on the side (home or away)
    """
    if side not in ["home", "away"]:
        raise ValueError(f"Invalid side argument '{side}'. Valid options are 'home' and 'away'")

    # Filter matches based on the side
    team_side_filter = Matches.home_team_id == teamID if side == "home" else Matches.away_team_id == teamID

    # Query all matches in which the team played during the specified season and side
    team_matches = session.query(Matches).filter(
        and_(
            team_side_filter,
            Matches.season == season
        )
    ).all()

    if len(team_matches) == 0:
        raise ValueError(f"No {side} matches found for teamID = {teamID} and season = {season}")

    # Calculate the total goals scored by the team
    total_goals = sum(
        match.home_goals if match.home_team_id == teamID else match.away_goals
        for match in team_matches
    )

    # Calculate the average goals scored per match
    average_goals = total_goals / len(team_matches) if team_matches else 0

    return average_goals

def get_average_conceded_season(teamID, season, side, session):
    """
    Returns average conceded goals for a team in a given season based on the side (home or away)
    """
    if side not in ["home", "away"]:
        raise ValueError(f"Invalid side argument '{side}'. Valid options are 'home' and 'away'")

    # Filter matches based on the side
    team_side_filter = Matches.home_team_id == teamID if side == "home" else Matches.away_team_id == teamID

    # Query all matches in which the team played during the specified season and side
    team_matches = session.query(Matches).filter(
        and_(
            team_side_filter,
            Matches.season == season
        )
    ).all()

    if len(team_matches) == 0:
        raise ValueError(f"No {side} matches found for teamID = {teamID} and season = {season}")

    # Calculate the total conceded goals by the team
    total_conceded_goals = sum(
        match.away_goals if match.home_team_id == teamID else match.home_goals
        for match in team_matches
    )

    # Calculate the average conceded goals per match
    average_conceded_goals = total_conceded_goals / len(team_matches) if team_matches else 0

    return average_conceded_goals
  
def get_average_goaldiff_season(teamID, season, side, session):
    """
    Returns average goal difference for a team in a given season based on the side (home or away)
    """
    if side not in ["home", "away"]:
        raise ValueError(f"Invalid side argument '{side}'. Valid options are 'home' and 'away'")
    
    # Filter matches based on the side
    team_side_filter = Matches.home_team_id == teamID if side == "home" else Matches.away_team_id == teamID

    # Query all matches in which the team played during the specified season and side
    team_matches = session.query(Matches).filter(
        and_(
            team_side_filter,
            Matches.season == season
        )
    ).all()

    if len(team_matches) == 0:
        raise ValueError(f"No {side} matches found for teamID = {teamID} and season = {season}")

    # Calculate the total goal difference for the team
    total_goal_difference = sum(
        (match.home_goals - match.away_goals) if match.home_team_id == teamID
        else (match.away_goals - match.home_goals)
        for match in team_matches
    )

    # Calculate the average goal difference per match
    average_goal_difference = total_goal_difference / len(team_matches) if team_matches else 0

    return average_goal_difference

def get_outcome_rate(teamID, season, side, outcome, session):
    """
    Returns the win, draw, or loss rate for a team in a given season based on the side (home or away)
    """
    outcomes = {"win": "W", "draw": "D", "loss": "L"}

    if outcome not in outcomes:
        raise ValueError(f"Invalid outcome '{outcome}'. Allowed values: 'win', 'draw', 'loss'")

    if side not in ["home", "away"]:
        raise ValueError(f"Invalid side argument '{side}'. Valid options are 'home' and 'away'")
    
    # Filter matches based on the side
    team_side_filter = Matches.home_team_id == teamID if side == "home" else Matches.away_team_id == teamID

    # Query all matches in which the team played during the specified season and side
    team_matches = session.query(Matches).filter(
        and_(
            team_side_filter,
            Matches.season == season
        )
    ).all()

    if len(team_matches) == 0:
        raise ValueError(f"No {side} matches found for teamID = {teamID} and season = {season}")

    # Calculate the outcome count (win, draw, or loss)
    outcome_count = 0
    for match in team_matches:
        goal_difference = (match.home_goals - match.away_goals) if match.home_team_id == teamID else (match.away_goals - match.home_goals)
        if goal_difference > 0 and outcomes[outcome] == "W":
            outcome_count += 1
        elif goal_difference == 0 and outcomes[outcome] == "D":
            outcome_count += 1
        elif goal_difference < 0 and outcomes[outcome] == "L":
            outcome_count += 1
            
    # Calculate the outcome rate
    outcome_rate = outcome_count / len(team_matches)

    return outcome_rate

def get_clean_sheet_rate(teamID, season, side, session):
    """
    Returns the clean sheet rate for a team in a given season based on the side (home or away)
    """
    if side not in ["home", "away"]:
        raise ValueError(f"Invalid side argument '{side}'. Valid options are 'home' and 'away'")

    # Filter matches based on the side
    team_side_filter = Matches.home_team_id == teamID if side == "home" else Matches.away_team_id == teamID

    # Query all matches in which the team played during the specified season and side
    team_matches = session.query(Matches).filter(
        and_(
            team_side_filter,
            Matches.season == season
        )
    ).all()

    if len(team_matches) == 0:
        raise ValueError(f"No {side} matches found for teamID = {teamID} and season = {season}")

    # Calculate the number of clean sheets
    clean_sheet_count = 0
    for match in team_matches:
        if match.home_team_id == teamID and match.away_goals == 0:
            clean_sheet_count += 1
        elif match.away_team_id == teamID and match.home_goals == 0:
            clean_sheet_count += 1

    # Calculate the clean sheet rate
    clean_sheet_rate = clean_sheet_count / len(team_matches)

    return clean_sheet_rate
