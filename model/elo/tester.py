from elo import updateElo

team1 = 1200
team2 = 1000

new_home_elo, new_away_elo = updateElo(team1, team2, "H")

print(f"team1 : {team1} -> {new_home_elo}")
print(f"team2 : {team2} -> {new_away_elo}")