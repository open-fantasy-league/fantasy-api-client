import asyncio
import websockets
import json
import uuid
import sys
import datetime

existing_uuid = ['a67dd7fa-2ccf-4d31-b42c-365d59af3066', '78206abb-6658-4ded-a2bc-e19c99644e51']
DATE_FMT = "%Y-%m-%dT%H:%M:%S%z"

def result_msgs():
    ids = [str(uuid.uuid4()), str(uuid.uuid4())]
    insert_msg = {
                    "message_id": str(uuid.uuid4()),
                    "method": "Competition",
                    "data": [
                        {"competition_id": ids[0], "name": "dog", "meta": {"jim": "jones"}, "timespan": ["2019-08-15T17:41:18+00:00", "2019-08-16T17:41:18+00:00"], "series": []},
                        {"competition_id": ids[1], "name": "woof", "meta": {},"timespan": ["2019-08-15T17:41:18+00:00", "2019-08-16T17:41:18+00:00"], "series": []}
                    ]
                }
    upd_msg = {
                    "message_id": str(uuid.uuid4()),
                    "method": "CompetitionUpdate",
                    "data": [{"competition_id": ids[0], "name": "twat", "timespan": ["2019-08-15T17:41:18+00:00", "2019-08-16T17:41:18+00:00"]}, 
                    #{"competition_id": ids[1], "name": "woof", "meta": {},"timespan": ["2019-08-15T17:41:18+00:00", "2019-08-16T17:41:18+00:00"]}
                    ]
                }

    return insert_msg, upd_msg


def fantasy_msgs():
    lid = str(uuid.uuid4())
    uids = [str(uuid.uuid4()) for _ in range(8)]

    msg1 = {
            "message_id": str(uuid.uuid4()),
            "method": "League",
            "data": [
                #{"name": "cat", "meta": {}, "team_size": 5, "squad_size": 10, "competition_id": existing_uuid[0]},
                {"league_id": lid, "name": "test", "meta": {}, "team_size": 5, "squad_size": 5, "competition_id": existing_uuid[0],
                 "max_squad_players_same_team": 4, "max_squad_players_same_position": 2, "max_team_players_same_position": 2, "max_team_players_same_team": 2
                 },
            ]}
    msg2 = {
            "message_id": str(uuid.uuid4()),
            "method": "LeagueUpdate",
            "data":
                [{"league_id": lid, "name": "updated", "meta": {}, "squad_size": 10, "competition_id": existing_uuid[0]}],
            }

    msg3 = {
            "message_id": str(uuid.uuid4()),
            "method": "ExternalUser",
            "data":
                [{"external_user_id": uid, "name": "name" + uid[:6], "meta": {}} for uid in uids],
            }

    msg4 = {
            "message_id": str(uuid.uuid4()),
            "method": "FantasyTeam",
            "data":
                [{"fantasy_team_id": str(uuid.uuid4()), "external_user_id": uid, "meta": {}, "name": "tpain" + uid[:5], "league_id": lid} for uid in uids],
            }
    print((datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=0.5)).strftime(DATE_FMT))
    msg5 = {
            "message_id": str(uuid.uuid4()),
            "method": "Period",
            "data":
                [{"period_id": str(uuid.uuid4()), "league_id": lid, "name": "day 1", "meta": {}, "competition_id": existing_uuid[0],
                 "timespan": ["2019-08-15T17:41:18+00:00", "2019-08-16T17:41:18+00:00"], "points_multiplier": 1.0,
                 "teams_per_draft": 3, "draft_interval_secs": 10, "draft_start": (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=0.5)).strftime(DATE_FMT),
                  "draft_lockdown": (
                              datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=0.2)).strftime(
                      DATE_FMT)
                 },
                 {"period_id": str(uuid.uuid4()), "league_id": lid, "name": "day 2", "meta": {}, "competition_id": existing_uuid[0],
                  "timespan": ["2019-09-15T17:41:18+00:00", "2019-09-16T17:41:18+00:00"], "points_multiplier": 1.0,
                  "teams_per_draft": 2, "draft_interval_secs": 10,
                  "draft_start": (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=3)).strftime(DATE_FMT),
                  "draft_lockdown": (
                          datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=0.2)).strftime(
                      DATE_FMT)
                  }
                 ],
            }
    msg6 = {
            "message_id": str(uuid.uuid4()),
            "method": "StatMultiplier",
            "data":
                [{"league_id": lid, "name": "kills", "meta": {}, "multiplier": 2.0},
                 {"league_id": lid, "name": "assists", "meta": {}, "multiplier": 1.0},
                 {"league_id": lid, "name": "deaths", "meta": {}, "multiplier": -1.5},
                 ],
            }
    return [msg1, msg2, msg3, msg4, msg5, msg6]

def leaderboard_msgs():
    ids = []
    return []


async def test(port, msgs):
    async with websockets.connect('ws://0.0.0.0:{}/echo'.format(port)) as websocket:
        
        print("Connected")

        async def sender():
            for msg in msgs:
                print(json.dumps(msg))
                await websocket.send(json.dumps(msg))
                await asyncio.sleep(2)

        async def listener():
            while True:
                response = await websocket.recv()
                print("RESPONSE: {}".format(response))
                print("\n\n")
                await asyncio.sleep(0.0)
        t1 = asyncio.create_task(sender())
        t2 = asyncio.create_task(listener())
        await t1
        await t2
        await asyncio.sleep(10000)


loop = asyncio.get_event_loop()
all_ = asyncio.gather(test(3001, result_msgs()), test(3003, fantasy_msgs()), test(3002, leaderboard_msgs()))
#all_ = asyncio.gather(test(3001, result_msgs()), test(3002, leaderboard_msgs()))
loop.run_until_complete(all_)
