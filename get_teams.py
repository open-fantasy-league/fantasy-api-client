import json
import uuid

from data.dota_ids import TEAM_IDS_TO_NAMES
from utils.utils import rate_limited_retrying_request


def add_uuid(p):
    p["fantasy_id"] = str(uuid.uuid4())
    return p


def get_data():
    teams = []
    for team_id, team_name in TEAM_IDS_TO_NAMES.items():
        team_info = rate_limited_retrying_request("https://api.opendota.com/api/teams/{}/players".format(team_id))
        team_info = [add_uuid(p) for p in team_info if p['is_current_team_member']]
        teams.append({'name': team_name, 'players': team_info, 'fantasy_id': str(uuid.uuid4())})
    return teams


if __name__ == "__main__":
    teams = get_data()
    with open("data/players.json", "w") as f:
        json.dump(teams, f)
