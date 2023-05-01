import os
import sys

from sqlalchemy import and_, or_

from bettingAI.writer.databaseClasses import *


def query_recent_form(teamID, opponentID, date, session):
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


def query_H2H(teamID, opponentID, date, session):

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
