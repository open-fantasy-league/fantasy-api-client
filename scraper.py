import json
import os
import time
import traceback

import requests

from clients.result_websocket_client import ResultWebsocketClient
from messages.result_msgs import SubCompetition

APIKEY = os.environ.get("APIKEY")
if not APIKEY:
    raise Exception("Must set APIKEY env var")

LEAGUE_LISTING_URL = "http://api.steampowered.com/IDOTA2Match_570/GetLeagueListing/v0001?key={key}"
MATCH_LISTING_URL = "http://api.steampowered.com/IDOTA2Match_570/GetMatchHistory/v0001?key={key}&league_id={league_id}"
MATCH_DETAILS_URL = "http://api.steampowered.com/IDOTA2Match_570/GetMatchDetails/v0001?key={key}&league_id={match_id}"
MATCH_DETAILS_OPEN_DOTA_URL = "https://api.opendota.com/api/matches/{match_id}"

FANTASY_RESULT_ADDR = '0.0.0.0'
FANTASY_RESULT_PORT = 3001

result_client = ResultWebsocketClient('0.0.0.0', 3001)
result_client_fut = result_client.run()

DOTA_TO_FANTASY_LEAGUE_IDS = {24: 'weird uuid'}
DOTA_TO_FANTASY_MATCH_IDS = {24: 'weird uuid'}
FANTASY_TO_DOTA_MATCH_IDS = {'weird uuid': 24}


def rate_limited_retrying_request(url, sleep=1, max_tries=4):
    tries = 0
    resp = None
    while resp is None:
        try:
            tries += 1
            resp = requests.get(url)
        except Exception:
            traceback.print_exc()
            sleep *= 4
            if tries > max_tries:
                raise Exception("Failed getting url {} after max tries {}".format(url, max_tries))
        finally:
            time.sleep(sleep)
    return json.loads(resp)


async def get_league_results(league_id, tstamp_from=0):
    match_list = rate_limited_retrying_request(MATCH_LISTING_URL.format(key=APIKEY, league_id=league_id))
    fantasy_competition_hierarchy = await result_client.send_sub_competitions(
        SubCompetition(all=False, sub_competition_ids=[DOTA_TO_FANTASY_LEAGUE_IDS[league_id]])
    )
    fantasy_matches = (s["matches"] for s in fantasy_competition_hierarchy["data"][0]["series"])
    # Filter out matches that already have their results set
    match_ids = (FANTASY_TO_DOTA_MATCH_IDS[m["match_id"]] for m in fantasy_matches if len(m["team_match_results"]) == 0)
    matches_to_scrape = [m['match_id'] for m in match_list if m['match_id'] in match_ids and m['start_time'] >= tstamp_from]
    # TODO handle the dodgy api matches/remakes
    for match_id in matches_to_scrape:
        match_resp = rate_limited_retrying_request(MATCH_DETAILS_URL.format(key=APIKEY, match_id=match_id))
        odota_match_resp = rate_limited_retrying_request(MATCH_DETAILS_OPEN_DOTA_URL.format(match_id=match_id))
        players = []
        for player in odota_match_resp['players']:
            pickee = {"id": player["account_id"], "isTeamOne": player["isRadiant"],
                      'stats': [
                              {'field': 'kills', 'value': player["kills"]},
                              {'field': 'assists', 'value': player["assists"]},
                              {'field': 'deaths', 'value': player["deaths"]},
                              {'field': 'last hits', 'value': player["last_hits"]},
                              {'field': 'denies', 'value': player["denies"]},
                              {'field': 'first blood', 'value': player["firstblood_claimed"]},
                              # {'field': 'stun', 'value': player["stuns"]},
                              {'field': 'teamfight participation', 'value': player["teamfight_participation"]},
                              {'field': 'GPM', 'value': player["gold_per_min"]},
                              {'field': 'towers', 'value': player["towers_killed"]},
                              {'field': 'observer wards', 'value': player["obs_placed"]},
                              {'field': 'dewards', 'value': player["observer_kills"]},
                              {'field': 'camps stacked', 'value': player["camps_stacked"]},
                              {'field': 'runes', 'value': player["rune_pickups"]},
                              {'field': 'roshans', 'value': player["roshan_kills"]},
                          ]
                      }
            if player["account_id"] in valid_pickee_ids:
                players.append(pickee)