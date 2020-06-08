import asyncio
import datetime
import logging
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
from messages.result_msgs import SubCompetition, TeamMatchResult, PlayerResult, SubTeam, Match, Series
from utils.constants import DATE_FMT
from data.dota_ids import FANTASY_COMPETITION_ID, FANTASY_USER_LEADERBOARD_ID, FANTASY_PLAYER_LEADERBOARD_ID

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dotenv.load_dotenv()
APIKEY = os.getenv("STEAMAPIKEY")
if not APIKEY:
    raise Exception("Must set STEAMAPIKEY .env var")

LEAGUE_LISTING_URL = "http://api.steampowered.com/IDOTA2Match_570/GetLeagueListing/v0001?key={key}"
MATCH_LISTING_URL = "http://api.steampowered.com/IDOTA2Match_570/GetMatchHistory/v0001?key={key}&league_id={league_id}"
MATCH_DETAILS_URL = "http://api.steampowered.com/IDOTA2Match_570/GetMatchDetails/v0001?key={key}&match_id={match_id}"
MATCH_DETAILS_OPEN_DOTA_URL = "https://api.opendota.com/api/matches/{match_id}"

DOTA_TO_FANTASY_LEAGUE_IDS = {12027: FANTASY_COMPETITION_ID}


async def get_league_results(result_client, fantasy_client, leaderboard_client, league_id, tstamp_from=0):
    fantasy_competitition_id = DOTA_TO_FANTASY_LEAGUE_IDS[league_id]
    match_list = rate_limited_retrying_request(MATCH_LISTING_URL.format(key=APIKEY, league_id=league_id))["result"]["matches"]
    fantasy_competition_hierarchy = (await result_client.send_sub_competitions(
        SubCompetition(all=False, sub_competition_ids=[fantasy_competitition_id])
    ))["data"]
    fantasy_teams_and_players = (await result_client.send_sub_teams(
        SubTeam(toggle=True)
    ))["data"]
    DOTA_TO_FANTASY_TEAM_IDS = {t["meta"]["dota_id"]: t["team_id"] for t in fantasy_teams_and_players}
    DOTA_TO_FANTASY_PLAYER_IDS = {p["player"]["meta"]["dota_id"]: p["team_id"] for t in fantasy_teams_and_players for p in t["players"]}

    fantasy_matches = (s["matches"] for s in fantasy_competition_hierarchy[0]["series"])
    fantasy_leagues = await fantasy_client.send_sub_leagues(
        SubLeague(all=True)
    )
    fantasy_league = next(f for f in fantasy_leagues["data"] if f["competition_id"] == fantasy_competitition_id)
    teams = {t["fantasy_team_id"]: t for t in fantasy_league["fantasy_teams"]}
    # Filter out matches that already have their results set
    existing_match_ids = (m["meta"]["dota_id"] for m in fantasy_matches if len(m["team_results"]) != 0)
    matches_to_scrape = [m['match_id'] for m in match_list if m['match_id'] not in existing_match_ids and m['start_time'] >= tstamp_from]
    # TODO handle the dodgy api matches/remakes
    match_inserts = []
    series_inserts = []
    logging.info(f"matches_to_scrape: {matches_to_scrape}")
    for match_id in [5455384177]:#matches_to_scrape:
        leaderboards = await leaderboard_client.send_get_latest_leaderboards([FANTASY_USER_LEADERBOARD_ID, FANTASY_PLAYER_LEADERBOARD_ID])
        user_points = next(l for l in leaderboards["data"] if "User Points" in l["name"])["leaderboard"]
        user_points_dict = {p["player_id"]: p for p in user_points}
        player_points = next(l for l in leaderboards["data"] if "Player Points" in l["name"])["leaderboard"]
        player_points_dict = {p["player_id"]: p for p in player_points}
        # TODO search for match with correct teams.
        # For now dont put matches into db preemptively, just add when we get results.
        # throw the team names in meta?
        fantasy_match_id = uuid.uuid4()
        fantasy_series_id = uuid.uuid4()
        match_resp = rate_limited_retrying_request(MATCH_DETAILS_URL.format(key=APIKEY, match_id=match_id))
        odota_match_resp = rate_limited_retrying_request(MATCH_DETAILS_OPEN_DOTA_URL.format(match_id=match_id))
        player_results = []

        #

        # TODO use match start to find period and thus find period-multiplier
        team_match_results = []
        radiant_fantasy_id = DOTA_TO_FANTASY_TEAM_IDS[odota_match_resp["radiant_team_id"]]
        dire_fantasy_id = DOTA_TO_FANTASY_TEAM_IDS[odota_match_resp["dire_team_id"]]
        radiant_meta = {"kills": odota_match_resp["radiant_score"], "dota_id": match_id}
        dire_meta = {"kills": odota_match_resp["dire_score"], "dota_id": match_id}

        team_match_results.append(TeamMatchResult(
            fantasy_match_id, radiant_fantasy_id, "1" if odota_match_resp["radiant_win"] else "0", radiant_meta
        ))
        team_match_results.append(TeamMatchResult(
            fantasy_match_id, dire_fantasy_id, "0" if odota_match_resp["radiant_win"] else "1", dire_meta
        ))
        user_points = defaultdict(float)
        # TODO unhardcode
        period_multiplier = 1.0
        now = datetime.datetime.now(datetime.timezone.utc).strftime(DATE_FMT)

        start_time = datetime.datetime.fromtimestamp(odota_match_resp["start_time"], datetime.timezone.utc)
        end_time = start_time + datetime.timedelta(seconds=odota_match_resp["duration"])
        series_inserts.append(Series(
            fantasy_series_id, f'{odota_match_resp["radiant_team"]["name"]} v {odota_match_resp["dire_team"]["name"]}',
            (start_time.strftime(DATE_FMT), end_time.strftime(DATE_FMT)),
            competition_id=FANTASY_COMPETITION_ID
        ))
        match_inserts.append(Match(
            fantasy_match_id, f'{odota_match_resp["radiant_team"]["name"]} v {odota_match_resp["dire_team"]["name"]}',
            (start_time.strftime(DATE_FMT), end_time.strftime(DATE_FMT)),
            fantasy_series_id,
            meta={"dota_id": match_id}
        ))
        for player in odota_match_resp['players']:
            parse_player(
                player, fantasy_league, fantasy_match_id, DOTA_TO_FANTASY_PLAYER_IDS, period_multiplier,
                player_results, teams,
                user_points, user_points_dict, player_points_dict
            )

        for val in user_points_dict.values():
            val["timestamp"] = now

        for val in player_points_dict.values():
            val["timestamp"] = now

        await result_client.send_insert_series(series_inserts)
        await result_client.send_insert_matches(match_inserts)
        # TODO can do 2 below at same time. not sequentially.
        await result_client.send_insert_team_match_results(team_match_results)
        await result_client.send_insert_player_results(player_results)
        # The way we update users/player points means this func shouldnt ever be run concurrently/parallelised across diff matches
        await leaderboard_client.send_insert_stat(
            [Stat(user["leaderboard_id"], user["player_id"], now, user["points"]) for user in user_points_dict.values()]
        )
        await leaderboard_client.send_insert_stat(
            [Stat(x["leaderboard_id"], x["player_id"], now, x["points"]) for x in
             player_points_dict.values()]
        )


def parse_player(
        player, fantasy_league, fantasy_match_id, DOTA_TO_FANTASY_PLAYER_IDS, period_multiplier, player_results, teams,
        user_points, user_points_dict, player_points_dict
):
    fantasy_player_id = DOTA_TO_FANTASY_PLAYER_IDS[player["account_id"]]
    player_result = {"points": 0.0}
    print(fantasy_league["stat_multipliers"])
    for stat in fantasy_league["stat_multipliers"]:
        odta_stats = {
            "first blood": "firstblood_claimed",
            "stun": "stuns",
            "GPM": "gold_per_min",
            "last hits": "last_hits",
            "runes": "rune_pickups",
            "roshans": "roshans_killed",
            "towers": "towers_killed",
            "dewards": "observer_kills",
            "observer wards": "obs_placed",
        }
        # TODO uncrappify
        odota_stat_name = odta_stats.get(stat["name"], stat["name"]).replace(" ", "_")
        player_result[stat["name"]] = player[odota_stat_name]
        player_result["points"] += (
                stat["multiplier"] * player[odota_stat_name] + period_multiplier
        )
    player_results.append(PlayerResult(
        fantasy_match_id, fantasy_player_id, player_result
    ))
    for team_id, team in teams.items():
        if fantasy_player_id in team:
            user_points[team_id] += player_result["points"]
            try:
                user_points_dict[team_id]["points"] += player_result["points"]
            except KeyError:
                new_user = {"player_id": team_id, "points": player_result["points"]}
                user_points_dict[team_id] = new_user

    try:
        player_points_dict[fantasy_player_id]["points"] += player_result["points"]
    except KeyError:
        new_player = {"player_id": fantasy_player_id, "points": player_result["points"]}
        player_points_dict[fantasy_player_id] = new_player


async def main():
    # ran into this fun issue defining them outside main, loose in the file
    # https://stackoverflow.com/a/55918049/3920439
    result_client = ResultWebsocketClient()
    fantasy_client = FantasyWebsocketClient()
    leaderboard_client = LeaderboardWebsocketClient()
    # can asyncio.gather
    asyncio.create_task(result_client.run())
    asyncio.create_task(fantasy_client.run())
    asyncio.create_task(leaderboard_client.run())
    await get_league_results(result_client, fantasy_client, leaderboard_client, 12027)


if __name__ == "__main__":
    asyncio.run(main())
