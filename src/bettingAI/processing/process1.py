"""
Program that processes the raw match data from the database to be used in model1
"""
import traceback

import sqlalchemy
from sqlalchemy import text
from tqdm.auto import tqdm

from bettingAI.processing.queries import query_rawMatches
from bettingAI.processing.features import features_for_model1, labels
from bettingAI.googleCloud.databaseClasses import Processed1
from bettingAI.googleCloud.initPostgreSQL import initSession

def main(session: sqlalchemy.orm.Session) -> None:
    
    # STEP 1 - GET MATCH IDS OF ALL MATCHES IN COMPLETE SEASONS
    rawMatches = session.execute(query_rawMatches()).fetchall()
    # Fetch all processed matches
    processedMatches = session.execute(text(
        "SELECT DISTINCT match_id FROM processed_for_model1"
    )).fetchall()
    print(
        f"""
        Total raw matches       -> {len(rawMatches)}
        Total proccesed matches -> {len(processedMatches)}
        Matches to process      -> {len(rawMatches) - len(processedMatches)}
        """)
    
    processedMatches = set([match[0] for match in processedMatches]) # convert processedMatches to a set for faster lookup
    rawMatches = [match for match in rawMatches if match[0] not in processedMatches] # filter out the matches that have already been processed

    for matchID, teamID, opponentID, leagueID, season, date in tqdm(rawMatches, desc="Processing matches"):
        try:
            team1 = Processed1(
                match_id = matchID,
                league_id = leagueID,
                inputs = features_for_model1(teamID, opponentID, leagueID, season, "home", date, session),
                labels = labels(matchID, teamID, session)
            )
            team2 = Processed1(
                match_id = matchID,
                league_id = leagueID,
                inputs = features_for_model1(opponentID, teamID, leagueID, season, "away", date, session),
                labels = labels(matchID, opponentID, session)
            )
            session.add(team1)
            session.add(team2)
            session.commit()
        except ValueError:
            continue
        except Exception as e:
            session.rollback()
            print(f"Could not commit {matchID} -> {e}")
    
if __name__ == "__main__":
    session = initSession()
    main(session)