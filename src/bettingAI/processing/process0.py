"""
Program that processes the raw match data from the database to be used in model0
"""
import sqlalchemy
from sqlalchemy import text
from tqdm.auto import tqdm

from bettingAI.googleCloud.initPostgreSQL import initSession
from bettingAI.googleCloud.databaseClasses import Processed
from features import features_for_model0, labels

def main(session: sqlalchemy.orm.Session) -> None:
    """Main function for processing raw match data and generating processed data for the model.

    Steps performed by the function:
    1. Retrieve the raw match IDs and processed match IDs from the database to determine which matches to process.
    2. Filter out the matches that have already been processed.
    3. Iterate over the remaining raw matches and generate processed data for each team involved in the match.
    4. Create Processed objects with the necessary data (match ID, league ID, inputs, labels) for each team.
    5. Add the Processed objects to the session and commit the changes to the database.

    Parameters:
    - session: SQLAlchemy session object for interacting with the database.

    Note: The function assumes that the necessary helper functions (features_for_model0, labels) are available.
    """
    # Get the raw match ids and processed match ids to figure out what matches to process
    rawMatches = session.execute(text("SELECT id, home_team_id, away_team_id, league_id, season, date FROM matches")).fetchall()
    processedMatches = session.execute(text("SELECT DISTINCT match_id FROM processed_for_model0")).fetchall()
    print(
        f"""
        Total raw matches       -> {len(rawMatches)}
        Total proccesed matches -> {len(processedMatches)}
        Matches to process      -> {len(rawMatches) - len(processedMatches)}
        """)
    
    processedMatchIDs = set([match[0] for match in processedMatches]) # convert processedMatches to a set for faster lookup
    rawMatches = [match for match in rawMatches if match[0] not in processedMatchIDs] # filter out the matches that have already been processed
            
    for matchID, teamID, opponentID, leagueID, season, date in tqdm(rawMatches, desc="Processing matches"):
        team1 = Processed(
            match_id = matchID,
            league_id = leagueID,
            inputs = features_for_model0(teamID, opponentID, season, "home", date, session),
            labels = labels(matchID, teamID, session)
        )
        team2 = Processed(
            match_id = matchID,
            league_id = leagueID,
            inputs = features_for_model0(opponentID, teamID, season, "away", date, session),
            labels = labels(matchID, opponentID, session)
        )
        try:
            session.add(team1)
            session.add(team2)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Could not commit {matchID} -> {e}")
    

if __name__ == "__main__":
    session = initSession()
    main(session)