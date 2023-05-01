from typing import Optional, Tuple, Mapping

from bettingAI.writer.databaseClasses import *


def add_team(id: int, name: str, league_id: int, stadium: Optional[str] = "NA") -> Teams:

    team = Teams(id=id, name=name, stadium=stadium, league_id=league_id)

    return team


def add_match(
    id: int, season: str, matchStats: Mapping
) -> Tuple[Matches, MatchStats, MatchStats]:

    # main info
    match = Matches(
        id=id,
        home_team_id=matchStats["maininfo"]["homeID"],
        away_team_id=matchStats["maininfo"]["awayID"],
        league_id=matchStats["league"]["id"],
        season=season,
        date=matchStats["dtg"],
        home_goals=matchStats["maininfo"]["homescore"],
        away_goals=matchStats["maininfo"]["awayscore"],
    )
    if matchStats["statistics"] != {}:
        # home side statistics
        homeSide = MatchStats(
            match_id=id,
            side="home",
            total_shots=matchStats["statistics"]["shots"].get("total shots", [None])[0],
            shots_off_target=matchStats["statistics"]["shots"].get("off target", [None])[
                0
            ],
            shots_on_target=matchStats["statistics"]["shots"].get("on target", [None])[0],
            blocked_shots=matchStats["statistics"]["shots"].get("blocked shot", [None])[
                0
            ],
            hit_woodwork=matchStats["statistics"]["shots"].get("hit woodwork", [None])[0],
            shots_inside_box=matchStats["statistics"]["shots"].get("inside box", [None])[
                0
            ],
            shots_outside_box=matchStats["statistics"]["shots"].get(
                "outside box", [None]
            )[0],
            xG_total=matchStats["statistics"]["xG"].get("expected goals", [None])[0],
            xG_first_half=matchStats["statistics"]["xG"].get("first half", [None])[0],
            xG_second_half=matchStats["statistics"]["xG"].get("second half", [None])[0],
            xG_open_play=matchStats["statistics"]["xG"].get("open play", [None])[0],
            xG_set_play=matchStats["statistics"]["xG"].get("set play", [None])[0],
            xGOT=matchStats["statistics"]["xG"].get("on target", [None])[0],
            accurate_passes=matchStats["statistics"]["passes"].get(
                "accurate passes", [None]
            )[0],
            accuracy=matchStats["statistics"]["passes"].get(
                "accurate passes", [None, None]
            )[1],
            own_half=matchStats["statistics"]["passes"].get("own half", [None])[0],
            opposition_half=matchStats["statistics"]["passes"].get(
                "opposition half", [None]
            )[0],
            accurate_long_balls=matchStats["statistics"]["passes"].get(
                "accurate long balls", [None]
            )[0],
            accurate_crosses=matchStats["statistics"]["passes"].get(
                "accurate crosses", [None]
            )[0],
            throws=matchStats["statistics"]["passes"].get("throws", [None])[0],
            tackles_won=matchStats["statistics"]["defence"].get("tackles won", [None])[0],
            accuracy_tackles=matchStats["statistics"]["defence"].get(
                "tackles won", [None, None]
            )[1],
            interceptions=matchStats["statistics"]["defence"].get(
                "interceptions", [None]
            )[0],
            blocks=matchStats["statistics"]["defence"].get("blocks", [None])[0],
            clearances=matchStats["statistics"]["defence"].get("clearances", [None])[0],
            keeper_saves=matchStats["statistics"]["defence"].get("keeper saves", [None])[
                0
            ],
            yellow_cards=matchStats["statistics"]["cards"].get("yellow cards", [None])[0],
            red_cards=matchStats["statistics"]["cards"].get("red cards", [None])[0],
            duels_won=matchStats["statistics"]["duels"].get("duels won", [None])[0],
            ground_duels_won=matchStats["statistics"]["duels"].get(
                "ground duels", [None]
            )[0],
            aerial_duels_won=matchStats["statistics"]["duels"].get(
                "aerial duels", [None]
            )[0],
            successfull_dribbles=matchStats["statistics"]["duels"].get(
                "successfull dribbles", [None]
            )[0],
        )

        # away side statistics
        awaySide = MatchStats(
            match_id=id,
            side="away",
            total_shots=matchStats["statistics"]["shots"].get(
                "total shots", [None, None]
            )[1],
            shots_off_target=matchStats["statistics"]["shots"].get(
                "off target", [None, None]
            )[1],
            shots_on_target=matchStats["statistics"]["shots"].get(
                "on target", [None, None]
            )[1],
            blocked_shots=matchStats["statistics"]["shots"].get(
                "blocked shot", [None, None]
            )[1],
            hit_woodwork=matchStats["statistics"]["shots"].get(
                "hit woodwork", [None, None]
            )[1],
            shots_inside_box=matchStats["statistics"]["shots"].get(
                "inside box", [None, None]
            )[1],
            shots_outside_box=matchStats["statistics"]["shots"].get(
                "outside box", [None, None]
            )[1],
            xG_total=matchStats["statistics"]["xG"].get("expected goals", [None, None])[
                1
            ],
            xG_first_half=matchStats["statistics"]["xG"].get("first half", [None, None])[
                1
            ],
            xG_second_half=matchStats["statistics"]["xG"].get(
                "second half", [None, None]
            )[1],
            xG_open_play=matchStats["statistics"]["xG"].get("open play", [None, None])[1],
            xG_set_play=matchStats["statistics"]["xG"].get("set play", [None, None])[1],
            xGOT=matchStats["statistics"]["xG"].get("on target", [None, None])[1],
            accurate_passes=matchStats["statistics"]["passes"].get(
                "accurate passes", [None, None, None, None]
            )[2],
            accuracy=matchStats["statistics"]["passes"].get(
                "accurate passes", [None, None, None, None]
            )[3],
            own_half=matchStats["statistics"]["passes"].get("own half", [None, None])[1],
            opposition_half=matchStats["statistics"]["passes"].get(
                "opposition half", [None, None]
            )[1],
            accurate_long_balls=matchStats["statistics"]["passes"].get(
                "accurate long balls", [None, None, None, None]
            )[2],
            accurate_crosses=matchStats["statistics"]["passes"].get(
                "accurate crosses", [None, None, None, None]
            )[2],
            throws=matchStats["statistics"]["passes"].get("throws", [None, None])[1],
            tackles_won=matchStats["statistics"]["defence"].get(
                "tackles won", [None, None, None, None]
            )[2],
            accuracy_tackles=matchStats["statistics"]["defence"].get(
                "tackles won", [None, None, None, None]
            )[3],
            interceptions=matchStats["statistics"]["defence"].get(
                "interceptions", [None, None]
            )[1],
            blocks=matchStats["statistics"]["defence"].get("blocks", [None, None])[1],
            clearances=matchStats["statistics"]["defence"].get(
                "clearances", [None, None]
            )[1],
            keeper_saves=matchStats["statistics"]["defence"].get(
                "keeper saves", [None, None]
            )[1],
            yellow_cards=matchStats["statistics"]["cards"].get(
                "yellow cards", [None, None]
            )[1],
            red_cards=matchStats["statistics"]["cards"].get("red cards", [None, None])[1],
            duels_won=matchStats["statistics"]["duels"].get("duels won", [None, None])[1],
            ground_duels_won=matchStats["statistics"]["duels"].get(
                "ground duels", [None, None, None, None]
            )[2],
            aerial_duels_won=matchStats["statistics"]["duels"].get(
                "aerial duels", [None, None, None, None]
            )[2],
            successfull_dribbles=matchStats["statistics"]["duels"].get(
                "successfull dribbles", [None, None, None, None]
            )[2],
        )

        return match, homeSide, awaySide
    return match, None, None


def add_player_performance(
    match_id: int, playerStats: Mapping, player: str
) -> PlayerStats:

    playerPerformance = PlayerStats(
        player_id=playerStats[player]["id"],
        match_id=match_id,
        rating=playerStats[player]["fotmob rating"],
        minutes_played=playerStats[player]["minutes played"],
        goals=playerStats[player]["goals"],
        assists=playerStats[player]["assists"],
        shots=playerStats[player]["shots"],
        passes=playerStats[player]["passes"].split("/")[0],
        passes_accuracy=int(
            float(playerStats[player]["passes"].split("/")[0])
            / float(playerStats[player]["passes"].split("/")[1])
        ),
        chances_created=playerStats[player]["chances created"],
        touches=playerStats[player]["touches"],
        passes_into_final_third=playerStats[player]["passes into final third"],
        dispossesed=playerStats[player]["dispossessed"],
        tackles_won=playerStats[player]["tackles won"].split("/")[0],
        tackles_accuracy=int(
            float(playerStats[player]["tackles won"].split("/")[0])
            / float(playerStats[player]["tackles won"].split("/")[1])
        ),
        recoveries=playerStats[player]["recoveries"],
        ground_duels_won=playerStats[player]["ground duels won"].split("/")[0],
        aerial_duels_won=playerStats[player]["aerial duels won"].split("/")[0],
        was_fouled=playerStats[player]["was fouled"],
        fouls_committed=playerStats[player]["fouls committed"],
    )

    return playerPerformance


def add_player_bio(playerID: int, teamID: int, name: str, stats: Mapping) -> Players:

    playerBio = Players(
        id=playerID,
        team_id=int(teamID),
        name=name if name else "NA",
        age=int(stats["bio"].get("Age")) if stats["bio"].get("Age") else 0,
        country=stats["bio"].get("Country") if stats["bio"].get("Country") else "NA",
        height=int(stats["bio"].get("Height")) if stats["bio"].get("Height") else 0,
        market_val=stats["bio"].get("Market") if stats["bio"].get("Market") else "NA",
        primary_position=stats["bio"].get("position")
        if stats["bio"].get("position")
        else "NA",
        played=int(stats["season"].get("Matches"))
        if stats["season"].get("Matches")
        else 0,
        goals=int(stats["season"].get("Goals")) if stats["season"].get("Goals") else 0,
        assists=int(stats["season"].get("Assists"))
        if stats["season"].get("Assists")
        else 0,
        rating=float(stats["season"].get("FotMob"))
        if stats["season"].get("FotMob")
        else 0.0,
    )

    return playerBio
