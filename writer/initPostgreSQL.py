import sys

from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.schema import UniqueConstraint

from colorama import Fore
from writer import initPostgreSQL


def init_database():
    """
    Creates tables for the database
    """
    print(Fore.CYAN + "Initiliazing database tabels...")
    
    # Establish connection to the database
    connection = initPostgreSQL()
    if connection is None:
        sys.exit(Fore.RED + "-> Could not connect to PostgreSQL")
    else:
        print(Fore.GREEN + "-> Connected to PostgreSQL")
    
    # Declarative API
    Base = declarative_base()
    
    class Leagues(Base):
        __tablename__ = "leagues"
        id = Column(Integer, primary_key=True)
        name = Column(String, nullable=False)
        country = Column(String, nullable=False)
        n_teams = Column(Integer, nullable=False)
        level = Column(Integer, nullable=False)
        
        __table_args__ = (UniqueConstraint("id", "name", name="unique_league_in_leagues"),)
    
    class Teams(Base):
        __tablename__ = "teams"
        id = Column(Integer, primary_key=True)
        name = Column(String, nullable=False)
        stadium = Column(String, nullable=False)
        league_id = Column(Integer, ForeignKey('leagues.id'))
        
        __table_args__ = (UniqueConstraint("id", "name", name="unique_team_in_teams"),)
        
    class Players(Base):
        __tablename__ = "players"
        id = Column(Integer, primary_key=True)
        team_id = Column(Integer, ForeignKey('teams.id'))
        
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
        
        # Relationships
        playerstats = relationship("PlayerStats", back_populates="player")
        team = relationship("Teams")
        
        __table_args__ = (UniqueConstraint("id", "name", name = "unique_player_in_players"),)
        
    class PlayerStats(Base):
        __tablename__ = "playerstats"
        id = Column(Integer, primary_key=True)
        player_id = Column(Integer, ForeignKey('players.id'))
        match_id = Column(Integer, ForeignKey('matches.id'))
        player = relationship("Players", back_populates="playerstats")
        match = relationship("Matches", back_populates="playerstats")
    
    class Matches(Base):
        __tablename__ = "matches"
        id = Column(Integer, primary_key=True)
        home_team_id = Column(Integer, ForeignKey('teams.id'))
        away_team_id = Column(Integer, ForeignKey('teams.id'))
        league_id = Column(Integer, ForeignKey('leagues.id'))
        date = Column(TIMESTAMP, nullable=False)
        playerstats = relationship("PlayerStats", back_populates="match")
        matchstats = relationship("MatchStats", back_populates="match")
        
        __table_args__ = (UniqueConstraint("id", name="unique_match_in_matches"),)
        
    class MatchStats(Base):
        __tablename__ = "matchstats"
        id = Column(Integer, primary_key=True)
        match_id = match_id = Column(Integer, ForeignKey('matches.id'))
        match = relationship("Matches", back_populates="matchstats")
        side = Column(String)
        
        # Shots
        total_shots = Column(Integer)
        shots_off_target = Column(Integer)
        shots_on_target = Column(Integer)
        blocked_shots = Column(Integer)
        hit_woodwork = Column(Integer)
        shots_inside_box = Column(Integer)
        shots_outside_box = Column(Integer)
        
        # Excpected goals
        xG_total = Column(Float)
        xG_first_half = Column(Float)
        xG_second_half = Column(Float)
        xG_open_play = Column(Float)
        xG_set_play = Column(Float)
        xGOT = Column(Float)
        
        # Passes
        accurate_passes = Column(Integer)
        accuracy = Column(Integer)
        own_half = Column(Integer)
        opposition_half = Column(Integer)
        accurate_long_balls = Column(Integer)
        accurate_crosses = Column(Integer)
        throws = Column(Integer)
        
        # Defence
        tackles_won = Column(Integer)
        accuracy_tackles = Column(Integer)
        interceptions = Column(Integer)
        blocks = Column(Integer)
        clearances = Column(Integer)
        keeper_saves = Column(Integer)
        
        # Dicipline
        yellow_cards = Column(Integer)
        red_cards = Column(Integer)
        
        # Duels
        duels_won = Column(Integer)
        ground_duels_won = Column(Integer)
        aerial_duels_won = Column(Integer)
        successfull_dribbles = Column(Integer)
     
    #Base.metadata.drop_all(connection)   
    Base.metadata.create_all(connection)
        
        
        
if __name__ == "__main__":
    init_database()