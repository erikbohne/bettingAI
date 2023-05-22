from typing import List, Optional, Any
from sqlalchemy.orm.session import Session
from sqlalchemy import and_, or_, text

from bettingAI.googleCloud.databaseClasses import *


def query_recent_form(
    teamID: int, 
    opponentID: int, 
    date: Any, 
    session: Session
) -> List[Any]:
    """Queries and returns recent matches involving teamID and opponentID before the specified date.

    Args:
        teamID (int): The ID of the team.
        opponentID (int): The ID of the opponent team.
        date (Any): The specified date to filter the matches.
        session (Session): The SQLAlchemy session object for database access.

    Returns:
        List[Any]: The list of recent matches involving the team and opponent before the specified date.
    """
    matches = (
        session.query(Matches)
        .filter(
            and_(
                or_(
                    Matches.home_team_id.in_([teamID, opponentID]),
                    Matches.away_team_id.in_([teamID, opponentID]),
                ),
                Matches.date < date,
            )
        )
        .order_by(Matches.date.desc())
        .all()
    )

    return matches

def query_H2H(
    teamID: int,
    opponentID: int, 
    date: Any, 
    session: Session
) -> Optional[List[Any]]:
    """Queries and returns head-to-head matches between teamID and opponentID before the specified date.

    Args:
        teamID (int): The ID of the team.
        opponentID (int): The ID of the opponent team.
        date (Any): The specified date to filter the matches.
        session (Session): The SQLAlchemy session object for database access.

    Returns:
        Optional[List[Any]]: The list of head-to-head matches between the team and opponent before the specified date,
        or None if no matches are found.
    """
    matches = (
        session.query(Matches)
        .filter(
            and_(
                or_(
                    and_(
                        Matches.home_team_id == teamID, Matches.away_team_id == opponentID
                    ),
                    and_(
                        Matches.home_team_id == opponentID, Matches.away_team_id == teamID
                    ),
                ),
                Matches.date < date,
            )
        )
        .order_by(Matches.date.desc())
        .all()
    )
    if matches:
        return matches
    else:
        return None

def query_rawMatches():
    return text(
        """
        SELECT 
            m.id, 
            m.home_team_id, 
            m.away_team_id,
            m.league_id,
            m.season,
            m.date
        FROM matches m
        WHERE m.season = '2022-2023' AND league_id = 47
        ORDER BY date DESC
        """
    )
    
    return text(
        """
        SELECT 
            m.id, 
            m.home_team_id, 
            m.away_team_id,
            m.league_id,
            m.season,
            m.date
        FROM matches m
        JOIN (
            SELECT 
                l.id as league_id,
                l.name as league_name, 
                m.season, 
                COUNT(*) as num_matches, 
                l.n_teams * (l.n_teams - 1) as expected_matches
            FROM 
                matches m
            JOIN
                leagues l
            ON
                m.league_id = l.id
            GROUP BY 
                l.id, l.name, 
                m.season
            HAVING
                COUNT(*) >= (l.n_teams * (l.n_teams - 1) - 10)
        ) s
        ON m.league_id = s.league_id AND m.season = s.season
        """
    )