import asyncio
import datetime
import os
import uuid

import dotenv

from utils.utils import rate_limited_retrying_request
from collections import defaultdict


from clients.fantasy_websocket_client import FantasyWebsocketClient
from clients.leaderboard_websocket_client import LeaderboardWebsocketClient
from clients.result_websocket_client import ResultWebsocketClient
from messages.fantasy_msgs import SubLeague
from messages.leaderboard_msgs import SubLeaderboard, Stat
from messages.result_msgs import SubCompetition, TeamMatchResult, PlayerResult, SubTeam
from utils.constants import DATE_FMT
from data.dota_ids import FANTASY_COMPETITION_ID

dotenv.load_dotenv()
APIKEY = os.getenv("STEAMAPIKEY")
if not APIKEY:
    raise Exception("Must set STEAMAPIKEY .env var")

LEAGUE_LISTING_URL = "http://api.steampowered.com/IDOTA2Match_570/GetLeagueListing/v0001?key={key}"
MATCH_LISTING_URL = "http://api.steampowered.com/IDOTA2Match_570/GetMatchHistory/v0001?key={key}&league_id={league_id}"
MATCH_DETAILS_URL = "http://api.steampowered.com/IDOTA2Match_570/GetMatchDetails/v0001?key={key}&league_id={match_id}"
MATCH_DETAILS_OPEN_DOTA_URL = "https://api.opendota.com/api/matches/{match_id}"


result_client = ResultWebsocketClient()
fantasy_client = FantasyWebsocketClient()
leaderboard_client = LeaderboardWebsocketClient()

DOTA_TO_FANTASY_LEAGUE_IDS = {12027: FANTASY_COMPETITION_ID}


async def get_league_results(league_id, tstamp_from=0):
    fantasy_competitition_id = DOTA_TO_FANTASY_LEAGUE_IDS[league_id]
    match_list = rate_limited_retrying_request(MATCH_LISTING_URL.format(key=APIKEY, league_id=league_id))
    fantasy_competition_hierarchy = await result_client.send_sub_competitions(
        SubCompetition(all=False, sub_competition_ids=[fantasy_competitition_id])
    )
    fantasy_teams_and_players = await result_client.send_sub_teams(
        SubTeam(toggle=True)
    )
    DOTA_TO_FANTASY_TEAM_IDS = {t["meta"]["dota_id"]: t["team_id"] for t in fantasy_teams_and_players}
    DOTA_TO_FANTASY_PLAYER_IDS = {p["meta"]["dota_id"]: p["team_id"] for t in fantasy_teams_and_players for p in t["players"]}

    fantasy_matches = (s["matches"] for s in fantasy_competition_hierarchy["data"][0]["series"])
    fantasy_leagues = await fantasy_client.send_sub_leagues(
        SubLeague(all=True)
    )
    fantasy_league = next(f for f in fantasy_leagues["data"] if f["competition_id"] == fantasy_competitition_id)
    # Filter out matches that already have their results set
    existing_match_ids = (m["meta"]["dota_id"] for m in fantasy_matches if len(m["team_match_results"]) != 0)
    matches_to_scrape = [m['match_id'] for m in match_list if m['match_id'] not in existing_match_ids and m['start_time'] >= tstamp_from]
    # TODO handle the dodgy api matches/remakes
    for match_id in matches_to_scrape:
        leaderboards = await leaderboard_client.send_sub_leaderboards(
            SubLeaderboard(all=True)
        )

        user_points = next(l for l in leaderboards["data"] if l["name"] == "User Points")["stats"][-1]
        user_points_dict = {p["player_id"]: p for p in user_points}
        player_points = next(l for l in leaderboards["data"] if l["name"] == "Player Points")["stats"][-1]
        player_points_dict = {p["player_id"]: p for p in player_points}
        # TODO search for match with correct teams.
        # For now dont put matches into db preemptively, just add when we get results.
        # throw the team names in meta?
        fantasy_match_id = uuid.uuid4()
        match_resp = rate_limited_retrying_request(MATCH_DETAILS_URL.format(key=APIKEY, match_id=match_id))
        odota_match_resp = rate_limited_retrying_request(MATCH_DETAILS_OPEN_DOTA_URL.format(match_id=match_id))
        player_results = []

        #

        # TODO use match start to find period and thus find period-multiplier
        team_match_results = []
        radiant_fantasy_id = DOTA_TO_FANTASY_TEAM_IDS[odota_match_resp["radiant_team_id"]]
        dire_fantasy_id = DOTA_TO_FANTASY_TEAM_IDS[odota_match_resp["dire_team_id"]]
        radiant_meta = {"kills": odota_match_resp["radiant_score"]}
        dire_meta = {"kills": odota_match_resp["dire_score"]}

        team_match_results.append(TeamMatchResult(
            match_id, radiant_fantasy_id, "1" if odota_match_resp["radiant_win"] else "0", radiant_meta
        ))
        team_match_results.append(TeamMatchResult(
            match_id, dire_fantasy_id, "0" if odota_match_resp["radiant_win"] else "1", dire_meta
        ))
        user_points = defaultdict(float)
        user_teams = {'': []}
        period_multiplier = 1.0
        now = datetime.datetime.now(datetime.timezone.utc).strftime(DATE_FMT)
        for player in odota_match_resp['players']:
            fantasy_player_id = DOTA_TO_FANTASY_PLAYER_IDS[player["account_id"]]
            player_result = {"points": 0.0}
            for stat in fantasy_league["stat_multipliers"]:
                player_result[stat["name"]] = player[stat["name"]]
                player_result["points"] += (
                        stat["multiplier"] * player[stat["name"]] + period_multiplier
                )
            player_results.append(PlayerResult(
                fantasy_match_id, fantasy_player_id, player_result
            ))
            for user, team in user_teams.items():
                if fantasy_player_id in team:
                    user_points[user] += player_result["points"]
                    user_points_dict[user]["points"] += player_result["points"]
            player_points_dict[fantasy_player_id]["points"] += player_result["points"]

        for val in user_points_dict.values():
            val["timestamp"] = now

        for val in player_points_dict.values():
            val["timestamp"] = now

        # TODO can do at same time. not sequentially.
        await result_client.send_insert_team_match_results(team_match_results)
        await result_client.send_insert_player_results(player_results)
        # The way we update users/player points means this func shouldnt ever be run concurrently/parallelised across diff matches
        await leaderboard_client.send_insert_stat(
            [Stat(user["leaderboard_id"], user["player_id"], user["name"], now, user["points"]) for user in user_points_dict.values()]
        )
        await leaderboard_client.send_insert_stat(
            [Stat(x["leaderboard_id"], x["player_id"], x["name"], now, x["points"]) for x in
             player_points_dict.values()]
        )


async def main():
    asyncio.create_task(result_client.run())
    asyncio.create_task(fantasy_client.run())
    asyncio.create_task(leaderboard_client.run())
    await get_league_results(12027)


if __name__ == "__main__":
    asyncio.run(main())
