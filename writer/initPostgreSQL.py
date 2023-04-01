import sys

from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship, declarative_base

from colorama import Fore
from writer import initPostgreSQL


def init_database():
    """
    Creates tables for the database
    """
    print(Fore.CYAN + "Initiliazing database tabels...")
    
    # Establish connection to database
    if not initPostgreSQL():
        sys.exit(Fore.RED + "-> Could not connect to PostgreSQL")
    else:
        cursor = initPostgreSQL() # Assign cursor
        print(Fore.GREEN + "-> Connected to PostgreSQL")
    
    # Declarative API
    Base = declarative_base()
    
    class Leagues(Base):
        __tablename__ = "leagues"
        id = Column(Integer, primary_key=True)
        name = Column(String, nullable=False)
        country = Column(String, nullable=False)
        n_teams = Column(Integer, nullable=False)
    
    class Teams(Base):
        __tablename__ = "teams"
        id = Column(Integer, primary_key=True)
        name = Column(String, nullable=False)
        league_id = Column(Integer, ForeignKey('leagues.id'))
        
    class Players(Base):
        __tablename__ = "players"
        id = Column(Integer, primary_key=True)
        
        # Bio
        name = Column(String, nullable=False)
        age = Column(Integer, nullable=False)
        country = Column(String, nullable=False)
        market_val = Column(Float, nullable=False) # Euro in ...
        preffered_foot = Column(String, nullable=False)
        primary_postition = Column(String, nullable=False)
        
        # Season stats
        played = Column(Integer)
        goals = Column(Integer)
        assists = Column(Integer)
        rating = Column(Float)
        
        team = relationship("Team")
        
    class PlayerStats(Base):
        __tablename__ = "playerstats"
        player_id = Column(Integer, ForeignKey('players.id'))
        match_id = Column(Integer, ForeignKey('matches.id'))
    
    class Matches(Base):
        __tablename__ = "matches"
        id = Column(Integer, primary_key=True)
        home_team_id = Column(Integer, ForeignKey('teams.id'))
        away_team_id = Column(Integer, ForeignKey('teams.id'))
        league_id = Column(Integer, ForeignKey('leagues.id'))
        date = Column(TIMESTAMP, nullable=False)
        
if __name__ == "__main__":
    init_database()