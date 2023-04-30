from colorama import Fore

from gather import *
from scraper import *



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
    print(Fore.GREEN + "    gather_player_performance()")
except Exception as e:
    print(Fore.RED + f"    gather_player_performance() -> {e}")


