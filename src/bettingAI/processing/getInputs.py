from typing import List, Tuple, Dict, Union, Any
import itertools
from datetime import datetime, timedelta

from sqlalchemy import and_, or_
from sqlalchemy.orm.session import Session

from bettingAI.googleCloud.databaseClasses import *
from bettingAI.processing.helpers import euros_to_number, get_outcome


def get_combined_team_stats(
    team_ids: List[int],
    season: str,
    sides: List[str],
    date: datetime,
    session: Session
) -> List[float]:
    """Returns all the features needed from a match for model0 training.

    Args:
        team_ids (List[int]): A list of two team IDs.
        season (str): The season for which to retrieve the team stats.
        sides (List[str]): A list of two sides, representing "home" and "away".
        date (datetime.datetime): The date used to filter matches.
        session (Session): The SQLAlchemy session object.

    Returns:
        List[float]: A list of floating-point values representing the team features.
    """
    if len(team_ids) != 2 or len(sides) != 2:
        raise ValueError("Expected 2 team_ids and 2 sides")

    for side in sides:
        if side not in ["home", "away"]:
            raise ValueError(
                f"Invalid side argument '{side}'. Valid options are 'home' and 'away'"
            )

    matches = (
        session.query(Matches)
        .filter(
            and_(
                or_(
                    Matches.home_team_id.in_(team_ids), Matches.away_team_id.in_(team_ids)
                ),
                Matches.season == season,
                Matches.date < date,
            )
        )
        .all()
    )

    team_stats = {
        team_id: {
            side: {
                "match_count": 0,
                "total_goals": 0,
                "total_conceded_goals": 0,
                "total_goal_difference": 0,
                "win_count": 0,
                "draw_count": 0,
                "loss_count": 0,
                "clean_sheet_count": 0,
            }
            for side in sides
        }
        for team_id in team_ids
    }

    for match in matches:
        for team_id, side in itertools.product(team_ids, sides):
            is_home = match.home_team_id == team_id
            is_away = match.away_team_id == team_id
            side_filter = is_home if side == "home" else is_away

            if side_filter:
                stats = team_stats[team_id][side]
                stats["match_count"] += 1

                goals_scored = match.home_goals if is_home else match.away_goals
                goals_conceded = match.away_goals if is_home else match.home_goals

                stats["total_goals"] += goals_scored
                stats["total_conceded_goals"] += goals_conceded
                stats["total_goal_difference"] += goals_scored - goals_conceded

                if goals_scored > goals_conceded:
                    stats["win_count"] += 1
                elif goals_scored == goals_conceded:
                    stats["draw_count"] += 1
                else:
                    stats["loss_count"] += 1

                if goals_conceded == 0:
                    stats["clean_sheet_count"] += 1

    for team_id in team_ids:
        for side in sides:
            stats = team_stats[team_id][side]
            match_count = stats["match_count"]

            if match_count > 0:
                for key in [
                    "total_goals",
                    "total_conceded_goals",
                    "total_goal_difference",
                ]:
                    stats[key] /= match_count

                for key in ["win_count", "draw_count", "loss_count", "clean_sheet_count"]:
                    stats[key] = stats[key] / match_count

    teamFeatures = {}
    # Extracting the stats for each team
    for stat_type in [
        "match_count",
        "total_goals",
        "total_conceded_goals",
        "total_goal_difference",
        "win_count",
        "draw_count",
        "loss_count",
        "clean_sheet_count",
    ]:
        teamFeatures[f"team_side1_{stat_type}_season"] = team_stats[team_ids[0]][
            sides[0]
        ][stat_type]
        teamFeatures[f"team_side2_{stat_type}_season"] = team_stats[team_ids[0]][
            sides[1]
        ][stat_type]
        teamFeatures[f"opponent_side1_{stat_type}_season"] = team_stats[team_ids[1]][
            sides[1]
        ][stat_type]
        teamFeatures[f"opponent_side2_{stat_type}_season"] = team_stats[team_ids[1]][
            sides[0]
        ][stat_type]

    # Calculating the average values
    for stat_type in ["total_goals", "total_conceded_goals", "total_goal_difference"]:
        avg_type = stat_type.replace("total_", "average_")
        teamFeatures[f"team_side1_{avg_type}_season"] = (
            teamFeatures[f"team_side1_{stat_type}_season"]
            / teamFeatures["team_side1_match_count_season"]
            if teamFeatures["team_side1_match_count_season"] > 0
            else 0
        )
        teamFeatures[f"team_side2_{avg_type}_season"] = (
            teamFeatures[f"team_side2_{stat_type}_season"]
            / teamFeatures["team_side2_match_count_season"]
            if teamFeatures["team_side2_match_count_season"] > 0
            else 0
        )
        teamFeatures[f"opponent_side1_{avg_type}_season"] = (
            teamFeatures[f"opponent_side1_{stat_type}_season"]
            / teamFeatures["opponent_side1_match_count_season"]
            if teamFeatures["opponent_side1_match_count_season"] > 0
            else 0
        )
        teamFeatures[f"opponent_side2_{avg_type}_season"] = (
            teamFeatures[f"opponent_side2_{stat_type}_season"]
            / teamFeatures["opponent_side2_match_count_season"]
            if teamFeatures["opponent_side2_match_count_season"] > 0
            else 0
        )

    # Calculating the win, draw, loss, and clean sheet rates
    for stat_type in ["win_count", "draw_count", "loss_count", "clean_sheet_count"]:
        rate_type = stat_type.replace("_count", "_rate")
        teamFeatures[f"team_side1_{rate_type}_season"] = teamFeatures[
            f"team_side1_{stat_type}_season"
        ]
        teamFeatures[f"team_side2_{rate_type}_season"] = teamFeatures[
            f"team_side2_{stat_type}_season"
        ]
        teamFeatures[f"opponent_side1_{rate_type}_season"] = teamFeatures[
            f"opponent_side1_{stat_type}_season"
        ]
        teamFeatures[f"opponent_side2_{rate_type}_season"] = teamFeatures[
            f"opponent_side2_{stat_type}_season"
        ]

    # Adding win rate features
    teamFeatures["team_side1_winrate_season"] = (
        teamFeatures["team_side1_win_count_season"]
        / teamFeatures["team_side1_match_count_season"]
        if teamFeatures["team_side1_match_count_season"] != 0
        else 0
    )
    teamFeatures["team_side2_winrate_season"] = (
        teamFeatures["team_side2_win_count_season"]
        / teamFeatures["team_side2_match_count_season"]
        if teamFeatures["team_side2_match_count_season"] != 0
        else 0
    )
    teamFeatures["opponent_side1_winrate_season"] = (
        teamFeatures["opponent_side1_win_count_season"]
        / teamFeatures["opponent_side1_match_count_season"]
        if teamFeatures["opponent_side1_match_count_season"] != 0
        else 0
    )
    teamFeatures["opponent_side2_winrate_season"] = (
        teamFeatures["opponent_side2_win_count_season"]
        / teamFeatures["opponent_side2_match_count_season"]
        if teamFeatures["opponent_side2_match_count_season"] != 0
        else 0
    )

    data_points = [
        teamFeatures["team_side1_average_goals_season"],
        teamFeatures["team_side2_average_goals_season"],
        teamFeatures["opponent_side1_average_goals_season"],
        teamFeatures["opponent_side2_average_goals_season"],
        teamFeatures["team_side1_average_conceded_goals_season"],
        teamFeatures["team_side2_average_conceded_goals_season"],
        teamFeatures["opponent_side1_average_conceded_goals_season"],
        teamFeatures["opponent_side2_average_conceded_goals_season"],
        teamFeatures["team_side1_average_goal_difference_season"],
        teamFeatures["team_side2_average_goal_difference_season"],
        teamFeatures["opponent_side1_average_goal_difference_season"],
        teamFeatures["opponent_side2_average_goal_difference_season"],
        teamFeatures["team_side1_winrate_season"],
        teamFeatures["team_side2_winrate_season"],
        teamFeatures["opponent_side1_winrate_season"],
        teamFeatures["opponent_side2_winrate_season"],
        teamFeatures["team_side1_clean_sheet_rate_season"],
        teamFeatures["team_side2_clean_sheet_rate_season"],
        teamFeatures["opponent_side1_clean_sheet_rate_season"],
        teamFeatures["opponent_side2_clean_sheet_rate_season"],
    ]

    return data_points

# Player info
def get_average_player_rating(
    teamID: int,
    session: Session
) -> float:
    """Returns the average player rating for a team.

    Args:
        teamID (int): The ID of the team.
        session (Session): The SQLAlchemy session object.

    Returns:
        float: The average player rating.
    """
    # Fetch all player ratings from players in a team
    playerRatings = [
        row.rating
        for row in session.query(Players).filter(Players.team_id == teamID).all()
    ]

    return sum(playerRatings) / len(playerRatings) if len(playerRatings) > 0 else 0

def get_average_player_age(
    teamID: int,
    session: Session
) -> float:
    """Returns the average player age for a team.

    Args:
        teamID (int): The ID of the team.
        session (Session): The SQLAlchemy session object.

    Returns:
        float: The average player age.
    """
    # Fetch all players age from players in a team
    playerAges = [
        row.age for row in session.query(Players).filter(Players.team_id == teamID).all()
    ]
    playerAges = [age for age in playerAges if age != 0]

    return sum(playerAges) / len(playerAges)

def get_average_player_height(
    teamID: int,
    session: Session
) -> float:
    """Returns the average player height for a team.

    Args:
        teamID (int): The ID of the team.
        session (Session): The SQLAlchemy session object.

    Returns:
        float: The average player height.
    """
    # Fetch all players height from players in a team
    playerHeights = [
        row.height
        for row in session.query(Players).filter(Players.team_id == teamID).all()
    ]
    playerHeights = [height for height in playerHeights if height != 0]

    return sum(playerHeights) / len(playerHeights)

def get_average_player_value(
    teamID: int,
    session: Session
) -> int:
    """Returns the average player market value for a team.

    Args:
        teamID (int): The ID of the team.
        session (Session): The SQLAlchemy session object.

    Returns:
        int: The average player market value.
    """
    # Fetch all players height from players in a team
    playerVals = [
        row.market_val
        for row in session.query(Players).filter(Players.team_id == teamID).all()
    ]
    playerVals = [
        euros_to_number(value)
        for value in playerVals
        if value != 0 and any(char.isdigit() for char in value)
    ]

    return int(sum(playerVals) / len(playerVals))


# Recent form
def get_points_won_ratio(
    teamID: int,
    matches: List
) -> Tuple[float, float, float]:
    """Returns the points won ratio for a team in the last 3, 5, and 10 matches.

    Args:
        teamID (int): The ID of the team.
        matches (List): The list of matches to consider.

    Returns:
        Tuple[float, float, float]: The points won ratio for the last 3, 5, and 10 matches.
    """
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
            points_won[interval] / (3 * match_count[interval])
            if match_count[interval] > 0
            else 0
        )

    return points_won_ratio[3], points_won_ratio[5], points_won_ratio[10]


def get_outcome_streak(
    teamID: int,
    matches: List
) -> int:
    """Returns the winning/losing streak going into a match.

    Args:
        teamID (int): The ID of the team.
        matches (List): The list of matches.

    Returns:
        int: The winning/losing streak.
    """
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

def get_home_away_form(
    teamID: int,
    side: str,
    matches: List
) -> float:
    """
    Returns the form from the last 5 home/away matches as wins/total.

    Args:
        teamID (int): The ID of the team.
        side (str): The side (either 'home' or 'away').
        matches (List): The list of matches.

    Returns:
        float: The win rate.
    
    Raises:
        ValueError: If the side value is not 'home' or 'away'.
    """
    if side not in ["home", "away"]:
        raise ValueError("Invalid side value. Accepted values are 'home' or 'away'.")

    # Filter matches based on teamID and side
    filtered_matches = [
        match
        for match in matches
        if (match.home_team_id == teamID and side == "home")
        or (match.away_team_id == teamID and side == "away")
    ]

    # Keep only the last 5 matches
    filtered_matches = filtered_matches[:5]

    wins = 0
    total_matches = len(filtered_matches)

    for match in filtered_matches:
        if side == "home" and match.home_goals > match.away_goals:
            wins += 1
        elif side == "away" and match.away_goals > match.home_goals:
            wins += 1

    win_rate = (wins / total_matches) if total_matches > 0 else 0

    return win_rate


# H2H
def get_outcome_distribution(
    teamID: int,
    matches: List
) -> Dict[str, Union[int, float]]:
    """Returns an outcome distribution between two teams from all 
    matches they've played together before the inputted date.

    Args:
        teamID (int): The ID of the team.
        matches (List): The list of matches.

    Returns:
        Dict[str, Union[int, float]]: The outcome distribution containing
        the counts and ratios of wins, draws, and losses.
    """
    outcome_distribution = {"win": 0, "draw": 0, "loss": 0}

    if matches is None:
        return outcome_distribution

    for match in matches:
        outcome = get_outcome(match, teamID)

        if outcome == 1:
            outcome_distribution["win"] += 1
        elif outcome == -1:
            outcome_distribution["loss"] += 1
        else:
            outcome_distribution["draw"] += 1

    total = sum(outcome_distribution[result] for result in outcome_distribution.keys())
    if total == 0:
        return 0
    for key in outcome_distribution.keys():
        outcome_distribution[key] /= total

    return outcome_distribution

def get_side_distribution(
    teamID: int, 
    side: str, 
    matches: List
) -> float:
    """Returns the winning rate of teamID at home and away when playing against opponentID.

    Args:
        teamID (int): The ID of the team.
        side (str): The side to consider ("home" or "away").
        matches (List): The list of matches.

    Returns:
        float: The winning rate of teamID at the specified side.
    """
    if matches is None:
        return 0

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

    if side == "home":
        return distribution["home_win_rate"]
    else:
        return distribution["away_win_rate"]

def get_recent_encounters(
    teamID: int,
    date: datetime, 
    matches: List
) -> float:
    """Returns the win rate for teamID against opponentID for the last two years.

    Args:
        teamID (int): The ID of the team.
        date (datetime): The current date.
        matches (List): The list of matches.

    Returns:
        float: The win rate of teamID against opponentID for the last two years.
    """
    if matches is None:
        return 0

    two_years_ago = date - timedelta(days=365 * 2)

    wins = 0
    total_matches = 0

    for match in matches:
        if match.date < two_years_ago:
            break

        total_matches += 1
        if (match.home_team_id == teamID and match.home_goals > match.away_goals) or (
            match.away_team_id == teamID and match.home_goals < match.away_goals
        ):
            wins += 1

    win_rate = wins / total_matches if total_matches > 0 else 0
    return win_rate


def get_average_goals_per_match(matches: List) -> float:
    """
    Returns the average goals scored in matches between teamID and opponentID.

    Args:
        matches (List): The list of matches.

    Returns:
        float: The average goals scored per match.
    """
    if matches is None:
        return 0

    total_goals = 0
    for match in matches:
        total_goals += match.home_goals + match.away_goals

    if len(matches) > 0:
        average_goals_per_match = total_goals / len(matches)
    else:
        average_goals_per_match = 0

    return average_goals_per_match


def get_average_goals_conceded_per_match(
    teamID: int,
    matches: List[Any]
) -> float:
    """Returns average goals conceded by teamID against opponentID.

    Args:
        teamID (int): The ID of the team.
        matches (List[Any]): The list of matches.

    Returns:
        float: The average goals conceded per match.
    """
    if matches is None:
        return 0

    goals_conceded = 0
    for match in matches:
        if match.home_team_id == teamID:
            goals_conceded += match.away_goals
        else:
            goals_conceded += match.home_goals

    total_matches = len(matches)
    average_goals_conceded = goals_conceded / total_matches if total_matches > 0 else 0

    return average_goals_conceded


def get_average_goal_difference_match(
    teamID: int,
    matches: List[Any]
) -> float:
    """Returns the average goal difference in matches between teamID and opponentID seen from teamID's perspective.

    Args:
        teamID (int): The ID of the team.
        matches (List[Any]): The list of matches.

    Returns:
        float: The average goal difference per match.
    """
    if matches is None:
        return 0

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


def get_btts_rate(matches: List[Any]) -> float:
    """Returns the percentage of matches where both teams score (BTTS).

    Args:
        matches (List[Any]): The list of matches.

    Returns:
        float: The BTTS rate.
    """
    if matches is None:
        return 0

    btts_count = 0
    for match in matches:
        if match.home_goals > 0 and match.away_goals > 0:
            btts_count += 1

    num_matches = len(matches)
    btts_rate = btts_count / num_matches if num_matches > 0 else 0

    return btts_rate


def get_clean_sheet_rate_h2h(
    teamID: int,
    matches: List[Any]
) -> float:
    """Returns the clean sheet rate for teamID against opponentID.

    Args:
        teamID (int): The ID of the team.
        matches (List[Any]): The list of matches.

    Returns:
        float: The clean sheet rate.
    """
    if matches is None:
        return 0

    clean_sheet_count = 0
    for match in matches:
        if match.home_team_id == teamID and match.away_goals == 0:
            clean_sheet_count += 1
        elif match.away_team_id == teamID and match.home_goals == 0:
            clean_sheet_count += 1

    num_matches = len(matches)
    clean_sheet_rate = clean_sheet_count / num_matches if num_matches > 0 else 0

    return clean_sheet_rate


def get_over_under_2_5(matches: List[Any]) -> float:
    """Returns the percentage of matches where total goals scored is more than 2.5.

    Args:
        matches (List[Any]): The list of matches.

    Returns:
        float: The percentage of matches with more than 2.5 total goals.
    """
    if matches is None:
        return 0

    over_2_5 = 0
    for match in matches:
        total_goals = match.home_goals + match.away_goals
        if total_goals > 2.5:
            over_2_5 += 1

    total_matches = len(matches)
    over_2_5_percentage = over_2_5 / total_matches if total_matches > 0 else 0

    return over_2_5_percentage


def get_outcome_streak_h2h(
    teamID: int,
    matches: List[Any]
) -> int:
    """Returns the winning/losing streak of teamID against opponentID going into a match.

    Args:
        teamID (int): The ID of the team.
        matches (List[Any]): The list of matches.

    Returns:
        int: The winning/losing streak of the team. Positive value indicates a winning streak,
            negative value indicates a losing streak, and 0 indicates no streak.
    """
    if matches is None:
        return 0

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

if __name__ == "__main__":
    raise SyntaxError("getInputs.py is only a file containing feature extraction functions.")