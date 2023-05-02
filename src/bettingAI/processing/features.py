import os
import sys
from datetime import datetime
from typing import List

from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

from bettingAI.googleCloud.initPostgreSQL import initPostgreSQL
from bettingAI.writer.databaseClasses import *
from bettingAI.processing.getInputs import *
from bettingAI.processing.queries import *


def features_for_model0(teamID, opponentID, season, thisSide, date, session):
    """
    Returns all the features needed from a match for model0 training
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


def features(teamID, opponentID, date, session):

    # Init team features dict
    teamFeatures = {}

    # Get player info
    teamFeatures["home_player_rating"] = get_average_player_rating(teamID, session)
    teamFeatures["away_player_rating"] = get_average_player_rating(opponentID, session)
    teamFeatures["home_player_age"] = get_average_player_age(teamID, session)
    teamFeatures["away_player_age"] = get_average_player_age(opponentID, session)
    teamFeatures["home_player_height"] = get_average_player_height(teamID, session)
    teamFeatures["away_player_height"] = get_average_player_height(opponentID, session)
    teamFeatures["home_player_value"] = get_average_player_value(teamID, session)
    teamFeatures["away_player_value"] = get_average_player_value(opponentID, session)

    # Get recent form statistics from teams
    teamFeatures["home_points_rate"] = get_points_won_ratio(teamID, date, session)
    teamFeatures["away_points_rate"] = get_points_won_ratio(opponentID, date, session)
    teamFeatures["home_outcome_streak"] = get_outcome_streak(teamID, date, session)
    teamFeatures["away_outcome_streak"] = get_outcome_streak(opponentID, date, session)
    teamFeatures["home_side_form"] = get_home_away_form(teamID, "home", date, session)
    teamFeatures["away_side_form"] = get_home_away_form(opponentID, "away", date, session)

    matches = query("H2H", teamID, opponentID, date, session)
    # Get h2h statistics from teams
    teamFeatures["outcome_distribution"] = get_outcome_distribution(teamID, matches)
    teamFeatures["side_distribtuion"] = get_side_distribution(teamID, matches)
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

    return teamFeatures


def labels(matchID: int, team_id: int, session) -> List[int]:
    """
    Returns the labels for the match
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

    # Connect to database
    engine = initPostgreSQL()
    Base.metadata.bind = engine
    Session = sessionmaker(bind=engine)
    session = Session()

    test1 = {
        "teamID": 8456,
        "opponentID": 9825,
        "date": datetime(year=2023, month=4, day=26),
    }

    test = features(session, test1)

    for key in test.keys():
        print(key, test[key])
