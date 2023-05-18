"""
Program to update the database with the latest matches

Ment to be run everyday @ 3 am to catch all the matches played each and everyday.
"""
from bettingAI.googleCloud.initPostgreSQL import initSession
from bettingAI.writer.scraper import get_match_links, get_match_info
from bettingAI.writer.addRow import add_match, add_player_performance

from sqlalchemy import text
import sqlalchemy

import datetime as dt
import logging

def update(session: sqlalchemy.orm.session) -> None:
    """Executes the main logic of the update program.
    
    This functions updates the ...
    
    Args: 
        session (sqlalchemy.orm.session): The database session object used for database operations.
    
    Returns:
        None
    """
    # Import leagues from database
    leagues = session.execute(text(
        "SELECT id as id, name as name, year_span as span FROM leagues;"
    ))
    
    for league in leagues:
        matchesAdded = 0
        
        season = "2023" if league.span == 1 else "2022-2023"
        
        # Fetch a list of all fixtures in the database
        fixtures = session.execute(text(
            "SELECT id FROM matches WHERE league_id = :id AND season = :season;"
            ),
            {
                "id": league.id,
                "season": season
            }
        )
        fixtures = set([id[0] for id in fixtures])
        
        # Fetch the links of all matches in that league in the current season
        all_fixtures = get_match_links(league.id)
        
        for fixture in all_fixtures:
            fixture_id = int(fixture.split("/")[2])
            
            # Make sure the match is not already in the database
            if fixture_id in fixtures:
                continue
            
            # Try to gather info about the current fixture
            matchStats = False
            try:
                matchStats, playerStats = get_match_info(fixture)
            except Exception as e:
                logger.error(e)
            finally:
                if not matchStats: # if game returned false
                    continue
            
            # Add match to the database
            try:
                match, homeSide, awaySide = add_match(fixture_id, season, matchStats)
                session.add(match)
                if homeSide is not None:
                    session.add(homeSide)
                    session.add(awaySide)
                session.commit()
                matchesAdded += 1
            except Exception as e:
                session.rollback()
                logger.error(e)
                
            if playerStats is None:
                continue
            continue
            for player in playerStats.keys():
                try:
                    session.add(add_player_performance(
                        fixture, playerStats, player
                    ))
                    session.commit()
                except Exception as e:
                    session.rollback()
                    logging.error(e)
                    
        print(league.name, matchesAdded)
                    
    logger.info("Update complete")
    
def initLogger() -> logging.Logger:
    """Initializes and configures a logger object for logging messages.

    Returns:
        logging.Logger: The logger object configured with file and console handlers.
    """
    # Create a logger object
    logger = logging.getLogger()

    # Set the logger level to INFO
    logger.setLevel(logging.INFO)

    # Create a handler for writing log messages to a file
    timestamp = dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_handler = logging.FileHandler(f"logs/app_{timestamp}.log")
    file_handler.setLevel(logging.INFO)

    # Create a handler for printing log messages to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Set a formatter for the log messages
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
if __name__ == "__main__":
    session = initSession()
    logger = initLogger()
    logger.info("Session established")
    update(session)