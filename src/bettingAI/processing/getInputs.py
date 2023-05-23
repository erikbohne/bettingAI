from typing import List, Tuple, Dict, Union, Any
import itertools
from datetime import datetime, timedelta

from sqlalchemy import and_, or_, text
from sqlalchemy.orm.session import Session

from bettingAI.googleCloud.databaseClasses import *
from bettingAI.processing.helpers import euros_to_number, get_outcome

# Main info
def get_match_info(team_id: int, opponent_id: int, league_id: int, match_date: str, season: str, session: Session):
    # Fetch the games played and points for all teams in the league up to the match date
    query = text("""
        SELECT
            teams.id AS team_id,
            COUNT(matches.id) AS games_played,
            SUM(
                CASE 
                    WHEN matches.home_goals > matches.away_goals AND teams.id = matches.home_team_id THEN 3 
                    WHEN matches.home_goals = matches.away_goals THEN 1
                    WHEN matches.home_goals < matches.away_goals AND teams.id = matches.away_team_id THEN 3
                    ELSE 0 
                END
            ) AS points
        FROM matches
        JOIN teams ON (matches.home_team_id = teams.id OR matches.away_team_id = teams.id)
        WHERE matches.date < :match_date AND matches.season = :season AND matches.league_id = :league_id
        GROUP BY teams.id
    """)

    result = session.execute(query, {"match_date": match_date, "season": season, "league_id": league_id})

    # Create the teams_stats dictionary
    teams_stats = {}
    for row in result:
        id = row[0]
        games_played = row[1]
        points = row[2]
        teams_stats[id] = {'games_played': games_played, 'points': points}

    if len(teams_stats.keys()) not in [16, 18, 20]:
        raise ValueError("Could not create complete table (most commonly because it's the first match)")

    this_team_stats = teams_stats[team_id]
    
    # Calculate the league rank of each team
    ranking = sorted(teams_stats.items(), key=lambda x: x[1]['points'], reverse=True)
    place = 1
    for team, _ in ranking:
        if team == team_id:
            this_team_rank = place
        elif team == opponent_id:
            opponent_rank = place
        place += 1

    return [
        this_team_stats['games_played'] / 38,
        this_team_rank,
        opponent_rank
    ]

def get_combined_team_stats(
    team_ids: List[int],
    season: str,
    sides: List[str],
    date: datetime,
    session: Session
) -> List[float]:
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
                "no_goals_count": 0,  # New statistic
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

                if goals_scored == 0:
                    stats["no_goals_count"] += 1 

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

                for count_key in ["win_count", "draw_count", "loss_count", "clean_sheet_count", "no_goals_count"]:
                    rate_key = count_key.replace("_count", "_rate")
                    stats[rate_key] = stats[count_key] / match_count
        
    teamFeatures = {}

    for stat_type in ["total_goals", "total_conceded_goals", "total_goal_difference", "win_rate", "draw_rate", "loss_rate", "clean_sheet_rate", "no_goals_rate"]:
        teamFeatures[f"team_side1_{stat_type}_season"] = team_stats[team_ids[0]][sides[0]][stat_type]
        teamFeatures[f"team_side2_{stat_type}_season"] = team_stats[team_ids[0]][sides[1]][stat_type]
        teamFeatures[f"opponent_side1_{stat_type}_season"] = team_stats[team_ids[1]][sides[1]][stat_type]
        teamFeatures[f"opponent_side2_{stat_type}_season"] = team_stats[team_ids[1]][sides[0]][stat_type]

    data_points = [
        teamFeatures["team_side1_total_goals_season"],
        teamFeatures["team_side2_total_goals_season"],
        teamFeatures["opponent_side1_total_goals_season"],
        teamFeatures["opponent_side2_total_goals_season"],
        teamFeatures["team_side1_total_conceded_goals_season"],
        teamFeatures["team_side2_total_conceded_goals_season"],
        teamFeatures["opponent_side1_total_conceded_goals_season"],
        teamFeatures["opponent_side2_total_conceded_goals_season"],
        teamFeatures["team_side1_total_goal_difference_season"],
        teamFeatures["team_side2_total_goal_difference_season"],
        teamFeatures["opponent_side1_total_goal_difference_season"],
        teamFeatures["opponent_side2_total_goal_difference_season"],
        teamFeatures["team_side1_win_rate_season"],
        teamFeatures["team_side2_win_rate_season"],
        teamFeatures["opponent_side1_win_rate_season"],
        teamFeatures["opponent_side2_win_rate_season"],
        teamFeatures["team_side1_clean_sheet_rate_season"],
        teamFeatures["team_side2_clean_sheet_rate_season"],
        teamFeatures["opponent_side1_clean_sheet_rate_season"],
        teamFeatures["opponent_side2_clean_sheet_rate_season"],
        teamFeatures["team_side1_no_goals_rate_season"],
        teamFeatures["team_side2_no_goals_rate_season"],
        teamFeatures["opponent_side1_no_goals_rate_season"],
        teamFeatures["opponent_side2_no_goals_rate_season"],
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
def get_recent_stats(team_id: int, opponent_id: int, season: str, date: datetime, session: Session) -> List[float]:
    # Get last 10 games for both teams before the given date
    team_matches = (
        session.query(Matches)
        .filter(
            and_(
                or_(Matches.home_team_id == team_id, Matches.away_team_id == team_id),
                Matches.date < date,
                Matches.season == season,
            )
        )
        .order_by(Matches.date.desc())
        .limit(10)
        .all()
    )

    opponent_matches = (
        session.query(Matches)
        .filter(
            and_(
                or_(Matches.home_team_id == opponent_id, Matches.away_team_id == opponent_id),
                Matches.date < date,
            )
        )
        .order_by(Matches.date.desc())
        .limit(10)
        .all()
    )

    def calculate_stats(matches: List[Matches], team_id: int) -> List[float]:
        stats = []

        for num_games in [3, 5, 10]:
            games = matches[:num_games]
            goals_scored = sum(match.home_goals if match.home_team_id == team_id else match.away_goals for match in games) / num_games
            no_goal_games = sum(1 for match in games if (match.home_goals if match.home_team_id == team_id else match.away_goals) == 0) / num_games
            goals_diff = sum((match.home_goals - match.away_goals) if match.home_team_id == team_id else (match.away_goals - match.home_goals) for match in games) / num_games
            goals_conceded = sum(match.away_goals if match.home_team_id == team_id else match.home_goals for match in games) / num_games

            stats.extend([goals_scored, no_goal_games, goals_diff, goals_conceded])

        return stats

    team_stats = calculate_stats(team_matches, team_id)
    opponent_stats = calculate_stats(opponent_matches, opponent_id)
    
    return team_stats + opponent_stats

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

def get_points_won_ratio_1(
    teamIDs: List[int],
    matches: List
) -> Dict[int, Tuple[float, float, float]]:
    """Returns the points won ratio for the teams in the last 3, 5, and 10 matches.

    Args:
        teamIDs (List[int]): The IDs of the teams.
        matches (List): The list of matches to consider.

    Returns:
        Dict[int, Tuple[float, float, float]]: A dictionary where the keys are team IDs and
        the values are tuples of points won ratio for the last 3, 5, and 10 matches.
    """
    # Initialize the points won and match count dictionaries
    team_points_won = {teamID: {3: 0, 5: 0, 10: 0} for teamID in teamIDs}
    match_count = {teamID: {3: 0, 5: 0, 10: 0} for teamID in teamIDs}

    # Loop through all matches
    for index, match in enumerate(matches):
        # Loop through both team IDs (home and away teams)
        for teamID in teamIDs:
            # If the team is the home team
            if match.home_team_id == teamID:
                won = match.home_goals > match.away_goals
                draw = match.home_goals == match.away_goals
            # If the team is the away team
            elif match.away_team_id == teamID:
                won = match.away_goals > match.home_goals
                draw = match.away_goals == match.home_goals
            else:
                continue

            # Calculate points won in the match
            points = 3 if won else 1 if draw else 0

            # Calculate points won for the last 3, 5, 10 matches
            for interval in [3, 5, 10]:
                if match_count[teamID][interval] < interval:
                    team_points_won[teamID][interval] += points
                    match_count[teamID][interval] += 1

    # Calculate points won ratio
    team_points_won_ratio = {teamID: {3: 0.0, 5: 0.0, 10: 0.0} for teamID in teamIDs}

    datapoints = []
    for teamID in teamIDs:
        for interval in [3, 5, 10]:
            if match_count[teamID][interval] > 0:
                datapoints.append(team_points_won[teamID][interval] / (3 * match_count[teamID][interval]))
    
    return datapoints

def get_teams_outcome_streak(
    teamIDs: List[int],
    matches: List
) -> Dict[int, int]:
    """Returns the winning/losing streak going into a match for multiple teams.

    Args:
        teamIDs (List[int]): The IDs of the teams.
        matches (List): The list of matches.

    Returns:
        Dict[int, int]: A dictionary with the teamID as key and the streak as value.
    """
    def get_outcome(match, teamID):
        if match.home_team_id == teamID:
            return 1 if match.home_goals > match.away_goals else -1 if match.home_goals < match.away_goals else 0
        elif match.away_team_id == teamID:
            return 1 if match.away_goals > match.home_goals else -1 if match.away_goals < match.home_goals else 0
        else:
            return False
    
    teams_outcome_streak = {teamID: 0 for teamID in teamIDs}

    streaks = []
    for teamID in teamIDs:
        if len(matches) == 0:
            teams_outcome_streak[teamID] = 0
            continue
        
        streak = 0
        for match in matches:
            outcome = get_outcome(match, teamID)
            if outcome:
                if outcome == 0:  # If the match was a draw
                    break
                elif outcome > 0 and streak >= 0:  # If the streak continues or just starts
                    streak += outcome
                elif outcome < 0 and streak <= 0:
                    streak += outcome
                else:  # If the streak breaks (a win after a loss or a loss after a win)
                    break

        streaks.append(streak / 10)
    
    return streaks

def get_teams_home_away_form(
    teams_side: Dict[int, str],
    matches: List
) -> Dict[int, float]:
    """
    Returns the form from the last 5 home/away matches as wins/total.

    Args:
        teams_side (Dict[int, str]): A dictionary with the teamID as key and the side as value.
        matches (List): The list of matches.

    Returns:
        Dict[int, float]: A dictionary with the teamID as key and the win rate as value.
    
    Raises:
        ValueError: If the side value is not 'home' or 'away'.
    """
    teams_form = {teamID: 0.0 for teamID in teams_side.keys()}

    datapoints = []
    for teamID in teams_side.keys():
        # Filter matches based on teamID
        filtered_matches = [
            match
            for match in matches
            if (match.home_team_id == teamID or match.away_team_id == teamID)
        ]

        # Keep only the last 5 matches
        filtered_matches = filtered_matches[:5]

        wins = 0
        total_matches = len(filtered_matches)

        for match in filtered_matches:
            if match.home_team_id == teamID and match.home_goals > match.away_goals:
                wins += 1
            elif match.away_team_id == teamID and match.away_goals > match.home_goals:
                wins += 1

        win_rate = (wins / total_matches) if total_matches > 0 else 0
        datapoints.append(win_rate)
        
    return datapoints


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

def get_average_goals_per_match(
    teamID: int,
    matches: List[Any]
) -> float:
    """
    Returns the average goals scored in matches between teamID and opponentID.

    Args:
        matches (List): The list of matches.
        teamID (int): The team id.

    Returns:
        float: The average goals scored per match.
    """
    if matches is None:
        return 0

    total_goals = 0
    for match in matches:
        if match.home_team_id == teamID:
            total_goals += match.home_goals
        else:
            total_goals += match.away_goals

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

def get_over_under_rates(matches: List[Any]) -> List[float]:
    """Returns the percentage of matches where total goals scored is over 0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5.

    Args:
        matches (List[Any]): The list of matches.

    Returns:
        List[float]: The list of percentages of matches with more than 0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5 total goals respectively.
    """
    if matches is None:
        return [0]*7

    rates = [0]*7
    total_matches = len(matches)

    for match in matches:
        total_goals = match.home_goals + match.away_goals
        for i, goal_limit in enumerate([0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5]):
            if total_goals > goal_limit:
                rates[i] += 1

    for i in range(7):
        rates[i] = rates[i] / total_matches if total_matches > 0 else 0

    return rates

def get_h2h_1(
    matches,
    teamID,
    date,
    thisSide
):
    datapoints = []
    outcomes = get_outcome_distribution(teamID, matches)
    datapoints += [
        outcomes["win"], outcomes["draw"], outcomes["loss"],
        get_side_distribution(teamID, thisSide, matches),
        get_recent_encounters(teamID, date, matches),
        get_average_goals_per_match(teamID, matches),
        get_average_goals_conceded_per_match(teamID, matches),
        get_average_goal_difference_match(teamID, matches),
        get_btts_rate(matches),
        get_clean_sheet_rate_h2h(teamID, matches),
        get_outcome_streak_h2h(teamID, matches)
    ]
    
    datapoints += get_over_under_rates(matches)

    return datapoints

# Time and date
def get_time_and_date_features(match_date: datetime):
    """Computes time and date related features."""
    time_of_day = match_date.hour / 24  # 0.0 - 1.0
    day_of_week = match_date.weekday() / 7  # 0.0 - 1.0
    quarter_of_year = ((match_date.month - 1) // 3 + 1) / 4  # 0.25, 0.5, 0.75, 1.0
    is_weekend = int(day_of_week * 7 >= 5)  # 0 = weekday, 1 = weekend
    return time_of_day, day_of_week, quarter_of_year, is_weekend


# Condition
def get_condition_features(teamID: int, opponentID: int, match_date: datetime, matches: List[Any]):
    """Computes condition related features."""

    def calculate_metrics(team_id: int, opponent_id: int = None):
        last_match_date, last_win_date, last_loss_date, matches_since_win, matches_since_loss, last_match_with_opponent_date = None, None, None, 0, 0, None
        volatility_score = calculate_volatility_score()

        for match in matches:
            if match.home_team_id == team_id or match.away_team_id == team_id:
                if last_match_date is None:
                    last_match_date = match.date

                if match.home_team_id == team_id:
                    won = match.home_goals > match.away_goals
                    lost = match.home_goals < match.away_goals
                else:
                    won = match.away_goals > match.home_goals
                    lost = match.home_goals > match.away_goals

                if won and last_win_date is None:
                    last_win_date = match.date
                elif lost and last_loss_date is None:
                    last_loss_date = match.date

                if last_win_date is None:
                    matches_since_win += 1
                if last_loss_date is None:
                    matches_since_loss += 1

            if opponent_id and ((match.home_team_id == team_id and match.away_team_id == opponent_id) or (match.away_team_id == team_id and match.home_team_id == opponent_id)):
                if last_match_with_opponent_date is None:
                    last_match_with_opponent_date = match.date

        if last_match_date is None or last_win_date is None or last_loss_date is None:
            raise ValueError("No previous matches")

        return {
            "days_since_last_match": (match_date - last_match_date).days / 7,
            "days_since_last_win": (match_date - last_win_date).days / 28,
            "matches_since_last_win": matches_since_win / 4,
            "days_since_last_loss": (match_date - last_loss_date).days / 28,
            "matches_since_last_loss": matches_since_loss / 4,
            "days_since_last_match_against_opponent": (match_date - last_match_with_opponent_date).days / 140 if last_match_with_opponent_date else None,
            "volatility_score": volatility_score,
        }

    team_metrics = calculate_metrics(teamID, opponentID)
    opponent_metrics = calculate_metrics(opponentID, teamID)

    return list(team_metrics.values()) + list(opponent_metrics.values())




# League features
def get_league_features(league_id: int, season: str, session: Any) -> List[float]:
    """Computes league related features."""
    
    league = session.query(Leagues).filter_by(id=league_id).first()

    if not league:
        raise ValueError(f"No league found with id {league_id}")  # League not found

    matches = (
        session.query(Matches)
        .filter_by(league_id=league_id, season=season)
        .all()
    )

    if not matches:
        raise ValueError(f"No matches found for league with id {league_id} in season {season}") 

    total_matches = len(matches)
    total_goals = sum([match.home_goals + match.away_goals for match in matches])
    avg_goals = total_goals / (2 * total_matches) # average goals per team per match

    home_wins = sum([1 for match in matches if match.home_goals > match.away_goals])
    away_wins = sum([1 for match in matches if match.home_goals < match.away_goals])
    draws = total_matches - home_wins - away_wins

    home_win_rate = home_wins / total_matches
    draw_rate = draws / total_matches
    away_win_rate = away_wins / total_matches

    over_goals_rate = []
    for i in range(7):  # for over 0.5 to over 6.5
        over_goals = sum([1 for match in matches if match.home_goals + match.away_goals > (i + 0.5)])
        over_goals_rate.append(over_goals / total_matches)

    return [league.level, avg_goals, home_win_rate, draw_rate, away_win_rate] + over_goals_rate

    
# Volatility score
def calculate_volatility_score():
    return 69

if __name__ == "__main__":
    raise SyntaxError("getInputs.py is only a file containing feature extraction functions.")