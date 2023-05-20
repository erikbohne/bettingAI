from sqlalchemy import (
    ARRAY,
    TIMESTAMP,
    Boolean,
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Leagues(Base):
    __tablename__ = "leagues"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    country = Column(String, nullable=False)
    n_teams = Column(Integer, nullable=False)
    level = Column(Integer, nullable=False)
    year_span = Column(Integer, nullable=False)

    __table_args__ = (UniqueConstraint("id", "name", name="unique_league_in_leagues"),)


class Teams(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    stadium = Column(String, nullable=False)
    league_id = Column(Integer, ForeignKey("leagues.id"))

    __table_args__ = (UniqueConstraint("id", "name", name="unique_team_in_teams"),)


class Players(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("teams.id"))

    # Bio
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    country = Column(String, nullable=False)
    market_val = Column(String, nullable=False)  # In Euro
    primary_position = Column(String, nullable=False)

    # Season stats
    played = Column(Integer)
    goals = Column(Integer)
    assists = Column(Integer)
    rating = Column(Float)

    # Relationships
    playerstats = relationship("PlayerStats", back_populates="player")
    team = relationship("Teams")

    __table_args__ = (UniqueConstraint("id", "name", name="unique_player_in_players"),)


class PlayerStats(Base):
    __tablename__ = "playerstats"
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("players.id"))
    match_id = Column(Integer, ForeignKey("matches.id"))
    player = relationship("Players", back_populates="playerstats")
    match = relationship("Matches", back_populates="playerstats")

    rating = Column(Float)
    minutes_played = Column(Integer)
    goals = Column(Integer)
    assists = Column(Integer)
    shots = Column(Integer)
    passes = Column(Integer)
    passes_accuracy = Column(Integer)
    chances_created = Column(Integer)
    touches = Column(Integer)
    passes_into_final_third = Column(Integer)
    dispossesed = Column(Integer)
    tackles_won = Column(Integer)
    tackles_accuracy = Column(Integer)
    recoveries = Column(Integer)
    ground_duels_won = Column(Integer)
    aerial_duels_won = Column(Integer)
    was_fouled = Column(Integer)
    fouls_committed = Column(Integer)

    # Ensure player_id and match_id only can appear once together in the table
    __table_args__ = (
        UniqueConstraint(
            "player_id", "match_id", name="unique_player_match_in_playerstats"
        ),
    )

class Matches(Base):
    __tablename__ = "matches"
    id = Column(Integer, primary_key=True)
    home_team_id = Column(Integer, ForeignKey("teams.id"))
    away_team_id = Column(Integer, ForeignKey("teams.id"))
    league_id = Column(Integer, ForeignKey("leagues.id"))
    season = Column(String, nullable=False)
    date = Column(TIMESTAMP, nullable=False)
    home_goals = Column(Integer)
    away_goals = Column(Integer)

    playerstats = relationship("PlayerStats", back_populates="match")
    matchstats = relationship("MatchStats", back_populates="match")

    __table_args__ = (UniqueConstraint("id", name="unique_match_in_matches"),)


class MatchStats(Base):
    __tablename__ = "matchstats"
    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("matches.id"))
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


# Processed data for model training
class Processed0(Base):
    __tablename__ = "processed_for_model0"
    id = Column(Integer, primary_key=True, autoincrement=True)
    league_id = Column(Integer, ForeignKey("leagues.id"))
    match_id = Column(Integer, ForeignKey("matches.id"))
    inputs = Column(ARRAY(Float))
    labels = Column(ARRAY(Integer))

class Processed1(Base):
    __tablename__ = "processed_for_model1"
    id = Column(Integer, primary_key=True, autoincrement=True)
    league_id = Column(Integer, ForeignKey("leagues.id"))
    match_id = Column(Integer, ForeignKey("matches.id"))
    inputs = Column(ARRAY(Float))
    labels = Column(ARRAY(Integer))


# Tables for data to API
class Performance(Base):
    __tablename__ = "performance"
    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("schedule.match_id"))
    model_id = Column(Integer)
    bet_type = Column(String) # what bet category was it
    bet_outcome = Column(String) # what did we bet on
    odds = Column(ARRAY(Float))
    kelly_fraction = Column(Float)
    placed = Column(Integer)
    outcome = Column(Boolean)
    
class Schedule(Base):
    __tablename__ = "schedule"
    match_id = Column(Integer, primary_key=True)
    date = Column(TIMESTAMP, nullable=False)
    season = Column(String)
    league_id = Column(Integer, ForeignKey("leagues.id"))
    home_team_id = Column(Integer, ForeignKey("teams.id"))
    away_team_id = Column(Integer, ForeignKey("teams.id"))
    
class Upcoming(Base):
    __tablename__ = "upcoming"
    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("schedule.match_id"))
    inputs0 = Column(ARRAY(Float))
    inputs1 = Column(ARRAY(Float))

class Bets(Base):
    __tablename__ = "bets"
    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("schedule.match_id"))
    model_id = Column(Integer)
    bet_type = Column(String)  # hub, btts, over/under
    odds = Column(ARRAY(Float)) # [2.34, 2.50, 1.80] or [1.86, 1.90]
    value = Column(String)
    kelly_fraction = Column(Float)
    strength = Column(Float) # (bookmakers odds) / (ai model odds)
    change = Column(Float) # change in strength from last check