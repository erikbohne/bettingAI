import os
import sys

sys.path.append(os.path.join("..", "writer"))
from databaseClasses import *
from helpers import euros_to_number, get_outcome

from sqlalchemy.sql import func
from sqlalchemy import and_, or_
from datetime import timedelta

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

# Player info
def get_average_player_rating(teamID, session):
    """
    Returns the average player rating for a team
    """
    # Fetch all player ratings from players in a team
    playerRatings = [row.rating for row in session.query(Players).filter(Players.team_id == teamID).all()]
    
    return sum(playerRatings) / len(playerRatings) if len(playerRatings) > 0 else 0
    
def get_average_player_age(teamID, session):
    """
    Returns the average player age for a team
    """
    # Fetch all players age from players in a team
    playerAges = [row.age for row in session.query(Players).filter(Players.team_id == teamID).all()]
    playerAges = [age for age in playerAges if age != 0]

    return sum(playerAges) / len(playerAges)
    
def get_average_player_height(teamID, session):
    """
    Returns the average player height for a team
    """
    # Fetch all players height from players in a team
    playerHeights = [row.height for row in session.query(Players).filter(Players.team_id == teamID).all()]
    playerHeights = [height for height in playerHeights if height != 0]

    return sum(playerHeights) / len(playerHeights)
    
def get_average_player_value(teamID, session):
    """
    Returns the average player market value for a team
    """
    # Fetch all players height from players in a team
    playerVals = [row.market_val for row in session.query(Players).filter(Players.team_id == teamID).all()]
    playerVals = [euros_to_number(value) for value in playerVals if value != 0]

    return int(sum(playerVals) / len(playerVals))

# Recent form
def get_points_won_ratio(teamID, date, session):
    """
    Returns the points won ratio for teamID the last 3, 5 and 10 matches
    """
    matches = session.query(Matches).filter(
        and_(
            or_(Matches.home_team_id == teamID, Matches.away_team_id == teamID),
            Matches.date < date
        )
    ).order_by(Matches.date.desc()).limit(10).all()

    points_won = {3: 0, 5: 0, 10: 0}
    match_count = {3: 0, 5: 0, 10: 0}

    for index, match in enumerate(matches):
        if match.home_team_id == teamID:
            won = match.home_goals > match.away_goals
            draw = match.home_goals == match.away_goals
        else:
            won = match.away_goals > match.home_goals
            draw = match.away_goals == match.home_goals

        points = 3 if won else 1 if draw else 0

        for interval in [3, 5, 10]:
            if index < interval:
                points_won[interval] += points
                match_count[interval] += 1

    points_won_ratio = {}
    for interval in [3, 5, 10]:
        points_won_ratio[interval] = (
            points_won[interval] / (3 * match_count[interval]) if match_count[interval] > 0 else 0
        )

    return points_won_ratio

def get_outcome_streak(teamID, date, session):
    """
    Returns the winning/losing streak going in to a match
    """            
    matches = session.query(Matches).filter(
        or_(
            Matches.home_team_id == teamID,
            Matches.away_team_id == teamID
        ),
        Matches.date < date
    ).order_by(Matches.date.desc()).all()

    if len(matches) == 0:
        return 0

    streak = 0
    current_outcome = get_outcome(matches[0], teamID)
    if current_outcome == 0:
            return 0

    for match in matches:
        outcome = get_outcome(match, teamID)
        if outcome == current_outcome:
            streak += outcome
        else:
            break

    return streak

def get_home_away_form(teamID, side, date, session):
    """
    Returns the form from the last 5 home/away matches as wins/total
    """
    if side not in ["home", "away"]:
        raise ValueError("Invalid side value. Accepted values are 'home' or 'away'.")

    team_column = "home_team_id" if side == "home" else "away_team_id"
    opponent_column = "away_team_id" if side == "home" else "home_team_id"

    matches = (
        session.query(Matches)
        .filter(
            and_(
                getattr(Matches, team_column) == teamID,
                Matches.date < date
            )
        )
        .order_by(Matches.date.desc())
        .limit(5)
        .all()
    )

    wins = 0
    total_matches = len(matches)

    for match in matches:
        if side == "home" and match.home_goals > match.away_goals:
            wins += 1
        elif side == "away" and match.away_goals > match.home_goals:
            wins += 1

    win_rate = (wins / total_matches) if total_matches > 0 else 0

    return win_rate

# H2H
def get_outcome_distribution(teamID, opponentID, date, session):
    """
    Returns an outcome distribution between two teams from all matches they've played together before the inputted date
    """
    matches = session.query(Matches).filter(
        and_(
            or_(
                and_(Matches.home_team_id == teamID, Matches.away_team_id == opponentID),
                and_(Matches.home_team_id == opponentID, Matches.away_team_id == teamID),
            ),
            Matches.date < date
        )
    ).all()

    outcome_distribution = {"win": 0, "draw": 0, "loss": 0}

    for match in matches:
        outcome = get_outcome(match, teamID)

        if outcome == 1:
            outcome_distribution["win"] += 1
        elif outcome == -1:
            outcome_distribution["loss"] += 1
        else:
            outcome_distribution["draw"] += 1

    total = sum(outcome_distribution[result] for result in outcome_distribution.keys())
    for key in outcome_distribution.keys():
        outcome_distribution[key] /= total
        
    return outcome_distribution

def get_side_distribution(teamID, opponentID, date, session):
    """
    Returns the winning rate of teamID at home and away when playing against opponentID
    """
    matches = session.query(Matches).filter(
        and_(
            or_(
                and_(Matches.home_team_id == teamID, Matches.away_team_id == opponentID),
                and_(Matches.home_team_id == opponentID, Matches.away_team_id == teamID),
            ),
            Matches.date < date
        )
    ).all()

    home_wins = 0
    away_wins = 0
    home_games = 0
    away_games = 0
    for match in matches:
        if match.home_team_id == teamID:
            home_games += 1
            if match.home_goals > match.away_goals:
                home_wins += 1
        else:
            away_games += 1
            if match.home_goals < match.away_goals:
                away_wins += 1

    home_win_rate = home_wins / home_games if home_games > 0 else 0
    away_win_rate = away_wins / away_games if away_games > 0 else 0

    distribution = {
        "home_win_rate": home_win_rate,
        "away_win_rate": away_win_rate,
    }

    return distribution

def get_recent_encounters(teamID, opponentID, date, session):
    """
    Returns the win rate for teamID against opponendID for the last two years
    """
    two_years_ago = date - timedelta(days=365*2)

    matches = session.query(Matches).filter(
        and_(
            or_(
                and_(Matches.home_team_id == teamID, Matches.away_team_id == opponentID),
                and_(Matches.home_team_id == opponentID, Matches.away_team_id == teamID),
            ),
            Matches.date < date,
            Matches.date >= two_years_ago,
        )
    ).all()

    wins = 0
    total_matches = len(matches)
    for match in matches:
        if match.home_team_id == teamID and match.home_goals > match.away_goals:
            wins += 1
        elif match.away_team_id == teamID and match.home_goals < match.away_goals:
            wins += 1

    win_rate = wins / total_matches if total_matches > 0 else 0

    return win_rate

def get_average_goals_per_match(teamID, opponentID, date, session):
    """
    Returns the average goals scored in matches between teamID and opponentID
    """
    matches = session.query(Matches).filter(
        and_(
            or_(
                and_(Matches.home_team_id == teamID, Matches.away_team_id == opponentID),
                and_(Matches.home_team_id == opponentID, Matches.away_team_id == teamID),
            ),
            Matches.date < date
        )
    ).all()

    total_goals = 0
    for match in matches:
        total_goals += match.home_goals + match.away_goals

    if len(matches) > 0:
        average_goals_per_match = total_goals / len(matches)
    else:
        average_goals_per_match = 0

    return average_goals_per_match

def get_average_goals_conceded_per_match(teamID, opponentID, date, session):
    """
    Returns average goals conceded by teamID against opponentID 
    """
    matches = session.query(Matches).filter(
        and_(
            or_(
                and_(Matches.home_team_id == teamID, Matches.away_team_id == opponentID),
                and_(Matches.home_team_id == opponentID, Matches.away_team_id == teamID),
            ),
            Matches.date < date
        )
    ).all()

    goals_conceded = 0
    for match in matches:
        if match.home_team_id == teamID:
            goals_conceded += match.away_goals
        else:
            goals_conceded += match.home_goals

    total_matches = len(matches)
    average_goals_conceded = goals_conceded / total_matches if total_matches > 0 else 0

    return average_goals_conceded

def get_average_goal_difference_match(teamID, opponentID, date, session):
    """
    Returns the average goals scored in matches between teamID and opponentID seen in teamID's perspective
    """
    matches = session.query(Matches).filter(
        and_(
            or_(
                and_(Matches.home_team_id == teamID, Matches.away_team_id == opponentID),
                and_(Matches.home_team_id == opponentID, Matches.away_team_id == teamID),
            ),
            Matches.date < date
        )
    ).all()

    total_goals_difference = 0
    for match in matches:
        if match.home_team_id == teamID:
            total_goals_difference += match.home_goals - match.away_goals
        else:
            total_goals_difference += match.away_goals - match.home_goals

    if len(matches) > 0:
        average_goals_difference = total_goals_difference / len(matches)
    else:
        average_goals_difference = 0

    return average_goals_difference

def get_btts_rate(teamID, opponentID, date, session):
    """
    Returns the percentage of both teams to score (BTTS)
    """
    matches = session.query(Matches).filter(
        and_(
            or_(
                and_(Matches.home_team_id == teamID, Matches.away_team_id == opponentID),
                and_(Matches.home_team_id == opponentID, Matches.away_team_id == teamID),
            ),
            Matches.date < date
        )
    ).all()

    btts_count = 0
    for match in matches:
        if match.home_goals > 0 and match.away_goals > 0:
            btts_count += 1

    num_matches = len(matches)
    btts_rate = btts_count / num_matches if num_matches > 0 else 0

    return btts_rate

def get_clean_sheet_rate_h2h(teamID, opponentID, date, session):
    """
    Returns the clean sheet rate for teamID against opponentID
    """
    matches = session.query(Matches).filter(
        and_(
            or_(
                and_(Matches.home_team_id == teamID, Matches.away_team_id == opponentID),
                and_(Matches.home_team_id == opponentID, Matches.away_team_id == teamID),
            ),
            Matches.date < date
        )
    ).all()

    clean_sheet_count = 0
    for match in matches:
        if match.home_team_id == teamID and match.away_goals == 0:
            clean_sheet_count += 1
        elif match.away_team_id == teamID and match.home_goals == 0:
            clean_sheet_count += 1

    num_matches = len(matches)
    clean_sheet_rate = clean_sheet_count / num_matches if num_matches > 0 else 0

    return clean_sheet_rate

def get_over_under_2_5(teamID, opponentID, date, session):
    """
    Return the percentage of matches where total goals scored is more than 2.5
    """
    matches = session.query(Matches).filter(
        and_(
            or_(
                and_(Matches.home_team_id == teamID, Matches.away_team_id == opponentID),
                and_(Matches.home_team_id == opponentID, Matches.away_team_id == teamID),
            ),
            Matches.date < date
        )
    ).all()

    over_2_5 = 0
    for match in matches:
        total_goals = match.home_goals + match.away_goals
        if total_goals > 2.5:
            over_2_5 += 1

    total_matches = len(matches)
    over_2_5_percentage = over_2_5 / total_matches if total_matches > 0 else 0

    return over_2_5_percentage
    
def get_outcome_streak_h2h(teamID, opponentID, date, session):
    """
    Returns the winning/losing streak teamID against opponentID, going in to a match
    """
    matches = session.query(Matches).filter(
        and_(
            or_(
                and_(Matches.home_team_id == teamID, Matches.away_team_id == opponentID),
                and_(Matches.home_team_id == opponentID, Matches.away_team_id == teamID),
            ),
            Matches.date < date
        )
    ).order_by(Matches.date.desc()).all()

    streak = 0
    outcome = None

    for match in matches:
        if match.home_goals == match.away_goals:
            streak = 0
            break

        if match.home_team_id == teamID:
            won = match.home_goals > match.away_goals
        else:
            won = match.away_goals > match.home_goals

        if outcome is None:
            outcome = won
            streak = 1
        elif outcome == won:
            streak += 1
        else:
            break

    return streak if outcome else -streak
    