import cProfile
import pstats
from io import StringIO

from model0 import initSession
from features import features_for_model0

from datetime import datetime

date = datetime(year=2023, month=4, day=26)
session = initSession()

team1, team2, season, side = 8586, 10260, "2022-2023", "home"

def wrapper():
    date = datetime(year=2023, month=4, day=26)
    session = initSession()
    team1, team2, season, side = 8586, 10260, "2022-2023", "home"
    
    return features_for_model0(team1, team2, season, side, date, session)

profiler_output = StringIO()
profiler = cProfile.Profile()
profiler.run('wrapper()', profiler_output)
profiler_output.seek(0)

# Create a pstats.Stats object to analyze and filter the profiler output
stats = pstats.Stats(profiler_output)

# Set the sorting criteria to cumulative time and display the top N contributors
N = 50  # Number of top contributors to display
stats.sort_stats('cumtime').print_stats(N)