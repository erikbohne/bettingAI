from colorama import Fore

from bettingAI.writer.gather import *
from bettingAI.writer.scraper import *



# Testing functions from scraper.py
print(Fore.CYAN + "scraper.py :")

# Testing tokenize_page()
try:
    tokenize_page("https://www.fotmob.com/leagues/73/overview/europa-league")
    print(Fore.GREEN + "    tokenize_page()")
except Exception as e:
    print(Fore.RED + f"    tokenize_page() -> {e}")
    
# Testing get_match_links()
try:
    get_match_links("47", "2015-2016") # Testing premier league 2015-2016
    get_match_links("53", "2016-2017") # Testing ligue 1 2016-2017
    get_match_links("54", "2017-2018") # Testing bundesliga 2017-2018
    print(Fore.GREEN + "    get_match_links()")
except Exception as e:
    print(Fore.RED + f"    get_match_links() -> {e}")
    
# Testing get_player_links()
try:
    IDs = [9825, 8634, 10249]
    completed = 0
    for teamID in IDs:
        if len(get_player_links(teamID)) > 0: # Testing on teams
            completed += 1
        else:
            raise ValueError("Returning empty list")
    print(Fore.GREEN + f"    get_player_links() {completed}/{len(IDs)}")
except Exception as e:
    print(Fore.RED + f"    get_player_links() {completed}/{len(IDs)} -> {e}")

# Testing get_match_info()
try:
    get_match_info("/match/3901212/matchfacts/arsenal-vs-leeds-united") # Testing on a Premier league match
    get_match_info("/match/3918204/matchfacts/elche-vs-barcelona") # Testing on a LaLiga match
    get_match_info("/match/3919315/matchfacts/napoli-vs-milan") # Testing on a Serie-A match
    print(Fore.GREEN + "    get_match_info()")
except Exception as e:
    print(Fore.RED + f"    get_match_info() -> {e}")
    
# Testing get_player_bio()
try:
    get_player_bio("/players/737066/erling-braut-haaland") # testing on Erlig Braut Haaland
    get_player_bio("/players/31097/luka-modric") # testing on Luka Modric
    get_player_bio("/players/740944/leo-stigard") # testing on Leo Østigard
    print(Fore.GREEN + "    get_player_bio()")
except Exception as e:
    print(Fore.RED + "  get_player_bio()")
    print(e)
    

# Testing functions from gather.py
print("")
print(Fore.CYAN + "gather.py :")

# Testing gather_dtg()
try:
    dtg = gather_dtg(tokenize_page("https://www.fotmob.com/match/3901212/matchfacts/arsenal-vs-leeds-united", match=True)[:50])
    if dtg == dt.datetime(2023, 4, 1, 14, 0, 0):
        print(Fore.GREEN + "    gather_dtg()")
    else:
        raise ValueError("Returning wrong dtg")
except Exception as e:
    print(Fore.RED + f"    gather_dtg() -> {e}")
    
# Testing gather_league()
try:
    league = gather_league(tokenize_page("https://www.fotmob.com/match/3901212/matchfacts/arsenal-vs-leeds-united", match=True)[10:100])
    if league["name"] == "Premier League" and league["id"] == "47":
        print(Fore.GREEN + "    gather_league()")
    else:
        print(Fore.RED + f"    gather_league() expected 'Permier League' and 'id' -> got {league['name']} and {league['id']}")
except Exception as e:
    print(Fore.RED + f"    gather_league() -> {e}")
    
# Testing gather_main_info()
try:
    mainInfo = gather_main_info(tokenize_page("https://www.fotmob.com/match/3901212/matchfacts/arsenal-vs-leeds-united", match=True)[:150])
    if mainInfo == {'hometeam': 'Arsenal', 'awayteam': 'Leeds United', 'homescore': '4', 'awayscore': '1', 'homegd': 3, 'awaygd': -3}:
        print(Fore.GREEN + "    gather_main_info()")
except Exception as e:
    print(Fore.RED + f"    gather_main_info() -> {e}")
    
# Testing gather_match_statistics()
try:
    matchStats = gather_match_statistics(tokenize_page("https://www.fotmob.com/match/3901212/matchfacts/arsenal-vs-leeds-united", match=True)[:6000])
    if matchStats == {'shots': {'total shots': ['13', '7'], 'off target': ['2', '1'], 'on target': ['6', '5'], 'blocked shot': ['5', '1'], 'hit woodwork': ['0', '0'], 'inside box': ['11', '6'], 'outside box': ['2', '1']}, 'xG': {'expected goals': ['3.78', '0.72'], 'first half': ['1.40', '0.17'], 'second half': ['2.38', '0.56'], 'open play': ['2.49', '0.72'], 'set play': ['0.50', '0.00'], 'penalty': ['0.79', '0.00'], 'on target': ['3.39', '0.48']}, 'passes': {'passes': ['636', '307'], 'accurate passes': ['544', '86', '%', '220', '72'], 'own half': ['227', '118'], 'opposition half': ['317', '102'], 'accurate long balls': ['21', '54', '%', '19', '40'], 'accurate crosses': ['6', '55', '%', '1', '10'], 'throws': ['14', '20']}, 'defence': {'tackles won': ['9', '60', '%', '12', '57'], 'interceptions': ['8', '13'], 'blocks': ['1', '6'], 'clearances': ['17', '13'], 'keeper saves': ['4', '1']}, 'duels': {'duels won': ['60', '50'], 'ground duels': ['40', '51', '%', '38', '49'], 'aerial duels': ['20', '63', '%', '12', '38'], 'successfull dribbles': ['13', '50', '%', '6', '50']}, 'cards': {'yellow cards': ['0', '2'], 'red cards': ['0', '0']}}:
        print(Fore.GREEN + "    gather_match_statistics()")
    else:
        raise ValueError("Wrong output")
except Exception as e:
    print(Fore.RED + f"    gather_match_statistics() -> {e}")
    
# Testing gather_player_bio()
try:
    playerBio = gather_player_bio(tokenize_page("https://www.fotmob.com/players/1129328"))
    print(playerBio)
    playerBio = gather_player_bio(tokenize_page("https://www.fotmob.com/players/737066/erling-braut-haaland"))
    if playerBio['bio'] == {'position': 'CF', 'Height': '194', 'Age': '22', 'Country': 'Norway', 'Shirt': '9', 'Market': '€175M'}:
        print(Fore.GREEN + "    gather_player_bio()")
    else:
        raise ValueError("Returning wrong values")
except Exception as e:
    print(Fore.RED + f"    gather_player_bio() -> {e}")
    
# Testing gather_player_performance()
try:
    playerPreformance = gather_player_performance(tokenize_page("https://www.fotmob.com/match/3901212/matchfacts/arsenal-vs-leeds-united", match=False)[2000:])
    if playerPreformance == {'Bukayo Saka': {'fotmob rating': '6.68', 'minutes played': '30', 'goals': '0', 'assists': '0', 'shots': '0', 'passes': '9/12', 'chances created': '0', 'touches': '19', 'passes into final third': '1', 'dispossessed': '0', 'tackles won': '0/1', 'recoveries': '2', 'ground duels won': '3/4', 'aerial duels won': '0', 'was fouled': '1', 'fouls committed': '0', 'id': '961995'}, 'Jorginho': {'fotmob rating': '6.49', 'minutes played': '30', 'goals': '0', 'assists': '0', 'shots': '0', 'passes': '27/31', 'chances created': '0', 'touches': '37', 'passes into final third': '2', 'dispossessed': '0', 'tackles won': '1/1', 'recoveries': '2', 'ground duels won': '2/5', 'aerial duels won': '1/1', 'was fouled': '1', 'fouls committed': '0', 'id': '282775'}, 'Emile Smith Rowe': {'fotmob rating': '0', 'minutes played': '5', 'goals': '0', 'assists': '0', 'shots': '0', 'passes': '1/1', 'chances created': '0', 'touches': '1', 'passes into final third': '1', 'dispossessed': '0', 'tackles won': '1/1', 'recoveries': '1', 'ground duels won': '1/2', 'aerial duels won': '0', 'was fouled': '0', 'fouls committed': '0', 'id': '150591'}, 'Rob Holding': {'fotmob rating': '7.49', 'minutes played': '90', 'goals': '0', 'assists': '0', 'shots': '0', 'passes': '58/69', 'chances created': '0', 'touches': '76', 'passes into final third': '5', 'dispossessed': '0', 'tackles won': '1/1', 'recoveries': '8', 'ground duels won': '1/1', 'aerial duels won': '4/5', 'was fouled': '0', 'fouls committed': '0', 'id': '626667'}, 'Gabriel': {'fotmob rating': '7.66', 'minutes played': '90', 'goals': '0', 'assists': '0', 'shots': '2', 'passes': '77/84', 'chances created': '0', 'touches': '98', 'passes into final third': '9', 'dispossessed': '0', 'tackles won': '0/2', 'recoveries': '5', 'ground duels won': '4/5', 'aerial duels won': '6/9', 'was fouled': '2', 'fouls committed': '0', 'id': '795179'}, 'Oleksandr Zinchenko': {'fotmob rating': '7.48', 'minutes played': '85', 'goals': '0', 'assists': '0', 'shots': '1', 'passes': '79/98', 'chances created': '0', 'touches': '119', 'passes into final third': '7', 'dispossessed': '2', 'tackles won': '0/1', 'recoveries': '7', 'ground duels won': '2/6', 'aerial duels won': '6/8', 'was fouled': '0', 'fouls committed': '1', 'id': '623621'}, 'Martin Ødegaard': {'fotmob rating': '8.32', 'minutes played': '85', 'goals': '0', 'assists': '1', 'shots': '0', 'passes': '45/51', 'chances created': '2', 'touches': '67', 'passes into final third': '6', 'dispossessed': '2', 'tackles won': '3/3', 'recoveries': '6', 'ground duels won': '6/8', 'aerial duels won': '1/1', 'was fouled': '1', 'fouls committed': '0', 'id': '534670'}, 'Thomas Partey': {'fotmob rating': '6.98', 'minutes played': '60', 'goals': '0', 'assists': '0', 'shots': '0', 'passes': '44/46', 'chances created': '0', 'touches': '53', 'passes into final third': '8', 'dispossessed': '0', 'tackles won': '0/1', 'recoveries': '5', 'ground duels won': '1/3', 'aerial duels won': '0', 'was fouled': '0', 'fouls committed': '1', 'id': '434325'}, 'Granit Xhaka': {'fotmob rating': '7.97', 'minutes played': '86', 'goals': '1', 'assists': '0', 'shots': '1', 'passes': '48/51', 'chances created': '1', 'touches': '59', 'passes into final third': '3', 'dispossessed': '1', 'tackles won': '1/1', 'recoveries': '4', 'ground duels won': '1/4', 'aerial duels won': '0/1', 'was fouled': '0', 'fouls committed': '1', 'id': '207236'}, 'Leandro Trossard': {'fotmob rating': '7.82', 'minutes played': '90', 'goals': '0', 'assists': '1', 'shots': '0', 'passes': '33/40', 'chances created': '3', 'touches': '55', 'passes into final third': '2', 'dispossessed': '1', 'tackles won': '0', 'recoveries': '1', 'ground duels won': '0/2', 'aerial duels won': '0', 'was fouled': '0', 'fouls committed': '1', 'id': '318615'}, 'Gabriel Jesus': {'fotmob rating': '9.23', 'minutes played': '60', 'goals': '2', 'assists': '0', 'shots': '4', 'passes': '25/29', 'chances created': '1', 'touches': '52', 'passes into final third': '2', 'dispossessed': '0', 'tackles won': '1/1', 'recoveries': '4', 'ground duels won': '7/12', 'aerial duels won': '0/1', 'was fouled': '2', 'fouls committed': '1', 'id': '576165'}, 'Gabriel Martinelli': {'fotmob rating': '8.2', 'minutes played': '90', 'goals': '0', 'assists': '1', 'shots': '4', 'passes': '32/41', 'chances created': '2', 'touches': '68', 'passes into final third': '2', 'dispossessed': '2', 'tackles won': '0', 'recoveries': '6', 'ground duels won': '7/16', 'aerial duels won': '1/4', 'was fouled': '2', 'fouls committed': '3', 'id': '1021586'}, 'William Saliba': {'fotmob rating': '5.86', 'minutes played': '25', 'goals': '0', 'assists': '0', 'shots': '0', 'passes': '6/7', 'chances created': '0', 'touches': '8', 'passes into final third': '1', 'dispossessed': '0', 'tackles won': '1/1', 'recoveries': '1', 'ground duels won': '1/2', 'aerial duels won': '0', 'was fouled': '0', 'fouls committed': '0', 'id': '150591'}, 'Patrick Bamford': {'fotmob rating': '0', 'minutes played': '5', 'goals': '0', 'assists': '0', 'shots': '0', 'passes': '0/1', 'chances created': '0', 'touches': '4', 'passes into final third': '1', 'dispossessed': '1', 'tackles won': '0/1', 'recoveries': '4', 'ground duels won': '5/8', 'aerial duels won': '0/2', 'was fouled': '0', 'fouls committed': '0', 'id': '952322'}, 'Luis Sinisterra': {'fotmob rating': '6.57', 'minutes played': '65', 'goals': '0', 'assists': '0', 'shots': '0', 'passes': '8/16', 'chances created': '1', 'touches': '32', 'passes into final third': '1', 'dispossessed': '4', 'tackles won': '4/4', 'recoveries': '9', 'ground duels won': '6/13', 'aerial duels won': '3/9', 'was fouled': '2', 'fouls committed': '2', 'id': '846369'}, 'Jack Harrison': {'fotmob rating': '6.23', 'minutes played': '85', 'goals': '0', 'assists': '0', 'shots': '1', 'passes': '17/25', 'chances created': '0', 'touches': '34', 'passes into final third': '5', 'dispossessed': '0', 'tackles won': '0', 'recoveries': '2', 'ground duels won': '0/2', 'aerial duels won': '0', 'was fouled': '0', 'fouls committed': '1', 'id': '751649'}, 'Marc Roca': {'fotmob rating': '7.2', 'minutes played': '90', 'goals': '0', 'assists': '0', 'shots': '0', 'passes': '31/39', 'chances created': '1', 'touches': '57', 'passes into final third': '13', 'dispossessed': '0', 'tackles won': '4/4', 'recoveries': '5', 'ground duels won': '7/9', 'aerial duels won': '1/2', 'was fouled': '3', 'fouls committed': '0', 'id': '640220'}, 'Rasmus Kristensen': {'fotmob rating': '7.67', 'minutes played': '90', 'goals': '1', 'assists': '0', 'shots': '3', 'passes': '11/22', 'chances created': '1', 'touches': '35', 'passes into final third': '4', 'dispossessed': '0', 'tackles won': '1/1', 'recoveries': '4', 'ground duels won': '1/5', 'aerial duels won': '3/6', 'was fouled': '0', 'fouls committed': '1', 'id': '722207'}, 'Junior Firpo': {'fotmob rating': '5.8', 'minutes played': '90', 'goals': '0', 'assists': '0', 'shots': '0', 'passes': '21/29', 'chances created': '0', 'touches': '56', 'passes into final third': '5', 'dispossessed': '1', 'tackles won': '0/3', 'recoveries': '4', 'ground duels won': '3/6', 'aerial duels won': '2/2', 'was fouled': '0', 'fouls committed': '0', 'id': '743192'}, 'Pascal Struijk': {'fotmob rating': '5.65', 'minutes played': '90', 'goals': '0', 'assists': '0', 'shots': '0', 'passes': '28/33', 'chances created': '0', 'touches': '41', 'passes into final third': '3', 'dispossessed': '0', 'tackles won': '0/1', 'recoveries': '3', 'ground duels won': '1/1', 'aerial duels won': '1/2', 'was fouled': '0', 'fouls committed': '0', 'id': '796974'}, 'Robin Koch': {'fotmob rating': '6.28', 'minutes played': '74', 'goals': '0', 'assists': '0', 'shots': '0', 'passes': '23/28', 'chances created': '0', 'touches': '40', 'passes into final third': '4', 'dispossessed': '0', 'tackles won': '1/1', 'recoveries': '2', 'ground duels won': '2/3', 'aerial duels won': '0/1', 'was fouled': '1', 'fouls committed': '1', 'id': '628201'}, 'Luke Ayling': {'fotmob rating': '5.38', 'minutes played': '90', 'goals': '0', 'assists': '0', 'shots': '0', 'passes': '29/33', 'chances created': '0', 'touches': '55', 'passes into final third': '6', 'dispossessed': '0', 'tackles won': '0/2', 'recoveries': '6', 'ground duels won': '3/9', 'aerial duels won': '1/2', 'was fouled': '1', 'fouls committed': '2', 'id': '190666'}, 'Illan Meslier': {'fotmob rating': '4.93', 'minutes played': '90', 'goals': None, 'assists': '0', 'shots': '0', 'passes': '9/12', 'chances created': '0', 'touches': '19', 'passes into final third': '1', 'dispossessed': '0', 'tackles won': '0/1', 'recoveries': '2', 'ground duels won': '3/4', 'aerial duels won': '0', 'was fouled': '1', 'fouls committed': '0', 'id': '961995'}}:
        print(Fore.GREEN + "    gather_player_performance()")
    else:
        print(Fore.RED + f"    gather_player_performance() -> Wrong output")
except Exception as e:
    print(Fore.RED + f"    gather_player_performance() -> {e}")


