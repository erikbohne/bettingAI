"""
Program that processes the raw match data from the database to be used in model1
"""
import sqlalchemy
from sqlalchemy import text
from tqdm.auto import tqdm

from bettingAI.processing.queries import query_rawMatches
from bettingAI.processing.features import features_for_model1
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
            print(matchID, date, teamID, opponentID)
            home_features = features_for_model1(
                teamID, opponentID, leagueID, season, "home", date, session
            )
            print(home_features[28:])
            print(len(home_features))
            exit()
        except Exception as e:
            print(e)
        try:
            print(matchID)
            home_features = features_for_model1(
                opponentID, teamID, leagueID, season, "away", date, session
            )
            print(len(home_features))
        except Exception as e:
            print(e)
    
if __name__ == "__main__":
    session = initSession()
    main(session)