from scraper import *
import json

#links = get_match_links(LEAGUES[1]["teams"][0]["id"], LEAGUES[1]["teams"][0]["UrlName"])
#print(get_match_info(links[2]))

file = open("leagues.json")
data = json.load(file)

print(data)
exit()

for league in LEAGUES:
    for team in league["teams"]:
        print(team)
        #player_links = get_player_links(team["id"])
        #for link in player_links[6:15]:
        #    print(link)
        #    get_player_bio(link)
        #exit()
        links = get_match_links(team["id"], team["UrlName"])
        for i in range(len(links)):
            get_match_info(links[i])

        
