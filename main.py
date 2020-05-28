import asyncio

from fake_data import *
from clients.result_websocket_client import ResultWebsocketClient


async def setup_competitions():
    await result_client.send_insert_competitions(EXAMPLE_COMPS)
    await result_client.send_insert_series(EXAMPLE_SERIES)
    await result_client.send_insert_matches(EXAMPLE_MATCHES)
    await result_client.send_insert_teams(EXAMPLE_PLAYERS)
    await result_client.send_insert_players(EXAMPLE_TEAMS)
    await result_client.send_insert_team_players(EXAMPLE_TEAM_PLAYERS)


async def setup_fantasy():
    await result_client.send_insert_competitions(EXAMPLE_COMPS)
    await result_client.send_insert_series(EXAMPLE_SERIES)
    await result_client.send_insert_matches(EXAMPLE_MATCHES)
    await result_client.send_insert_teams(EXAMPLE_PLAYERS)
    await result_client.send_insert_players(EXAMPLE_TEAMS)
    await result_client.send_insert_team_players(EXAMPLE_TEAM_PLAYERS)


loop = asyncio.get_event_loop()
result_client = ResultWebsocketClient('0.0.0.0', 3001)
result_client_fut = result_client.run()  # starts doing the run, function. returns a future that we can `wait` on it's result


# gather will sit and wait for all futures passed to it to finished,
# can pass pre-created future, i.e. 1st arg, or call a function creating a future, i.e. 2nd arg
all_ = asyncio.gather(result_client_fut, setup_competitions())
#all_ = asyncio.gather(test(3001, result_msgs()), test(3003, fantasy_msgs()), test(3002, leaderboard_msgs()))
#all_ = asyncio.gather(test(3001, result_msgs()), test(3002, leaderboard_msgs()))
loop.run_until_complete(all_)
