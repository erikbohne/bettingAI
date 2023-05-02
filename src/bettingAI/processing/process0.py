"""
Program that processes the raw match data from the database to be used in model0
"""
from sqlalchemy import text
from tqdm.auto import tqdm

from bettingAI.googleCloud.initPostgreSQL import initSession
from bettingAI.writer.databaseClasses import Processed
from features import features_for_model0, labels

def main(session):
    
    # Get the raw match ids and processed match ids to figure out what matches to process
    rawMatches = session.execute(text("SELECT id, home_team_id, away_team_id, season, date FROM matches WHERE matches.league_id = 47")).fetchall()
    processedMatches = session.execute(text("SELECT DISTINCT match_id FROM processed_for_model0")).fetchall()
    print(
        f"""
        Total raw matches       -> {len(rawMatches)}
        Total proccesed matches -> {len(processedMatches)}
        Matches to process      -> {len(rawMatches) - len(processedMatches)}
        """)
    
    processedMatchIDs = set([match[0] for match in processedMatches]) # convert processedMatches to a set for faster lookup
    rawMatches = [match for match in rawMatches if match[0] not in processedMatchIDs] # filter out the matches that have already been processed
            
    for matchID, teamID, opponentID, season, date in tqdm(rawMatches, desc="Processing matches"):
        team1 = Processed(
            match_id = matchID,
            inputs = features_for_model0(teamID, opponentID, season, "home", date, session),
            labels = labels(matchID, teamID, session)
        )
        team2 = Processed(
            match_id = matchID,
            inputs = features_for_model0(opponentID, teamID, season, "away", date, session),
            labels = labels(matchID, opponentID, session)
        )
        try:
            session.add(team1, team2)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Could not commit {matchID} -> {e}")
    

if __name__ == "__main__":
    session = initSession()
    main(session)