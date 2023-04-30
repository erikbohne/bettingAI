import os
import sys

sys.path.append(os.path.join("..", "writer"))
from databaseClasses import *

from sqlalchemy import and_, or_

def query_H2H(teamID, opponentID, date, session):
    
    matches = session.query(Matches).filter(
        and_(
            or_(
                and_(Matches.home_team_id == teamID, Matches.away_team_id == opponentID),
                and_(Matches.home_team_id == opponentID, Matches.away_team_id == teamID),
            ),
            Matches.date < date
        )
    ).order_by(Matches.date.desc()).all()
    if matches:
        return matches 
    else:
        return None