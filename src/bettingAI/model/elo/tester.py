from elo import updateElo

team1 = 1700
team2 = 800

new_home_elo, new_away_elo = updateElo(team1, team2, "A")

print(f"team1 : {team1} -> {new_home_elo}")
print(f"team2 : {team2} -> {new_away_elo}")
