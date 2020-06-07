import asyncio
import logging
import os
from pprint import pformat

from clients.fantasy_websocket_client import FantasyWebsocketClient
from clients.result_websocket_client import ResultWebsocketClient
from messages.fantasy_msgs import SubDraft, SubUser
from messages.result_msgs import SubTeam
from utils.utils import simplified_str
from utils.constants import TRUNCATED_MESSAGE_LENGTH


logger = logging.getLogger(__name__)


class PlayerHandler:

    def __init__(self):
        self.result_client = ResultWebsocketClient(os.getenv('ADDRESS', '0.0.0.0'))
        # better to init to None, than empty list/dict, as then more obvious when someone
        # forgets to await start()
        self.teams_and_players = None
        self.players = None
        self.simplified_player_names_to_id = None

    # cannot call async funcs in __init__ so need to split into 2-steps
    async def start(self):
        logger.info("Starting PlayerHandler")
        asyncio.create_task(self.result_client.run())
        teams_and_players_resp = await self.result_client.send_sub_teams(SubTeam(toggle=True))
        self.teams_and_players = teams_and_players_resp["data"]
        # a double loop, get all the players, in all the teams
        self.players = [p["player"] for t in self.teams_and_players for p in t["players"]]
        logger.info("PlayerHandler start: players added")
        logger.debug(self.players)
        self.simplified_player_names_to_id = {simplified_str(p["names"][0]["name"]): p["player_id"] for p in self.players}
        logger.info("Loaded PlayerHandler")


class FantasyHandler:

    def __init__(self):
        self.client = FantasyWebsocketClient(os.getenv('ADDRESS', '0.0.0.0'))
        self.users = None
        self.discord_user_id_to_fantasy_id = None

    async def start(self):
        """
        Start running client and run initial set up

        Atm, User init stuff is hadnled here wheras draft init is handled in 
        init_listener. Will probs make sense to either have all start here or
        all start in init_listener. Depends on whether we want bot to know when we 
        have inited or not I think.
        """
        logger.info("FantasyHandler Starting")
        asyncio.create_task(self.client.run())
        self.users = (await self.client.send_sub_users(SubUser(toggle=True)))["data"]["users"]
        logger.info(f"FantasyHandler received {len(self.users)} users")
        logger.debug(f'FantasyHandler users received: {pformat(self.users)}')
        self.discord_user_id_to_fantasy_id = {u["meta"]["discord_id"]: u["external_user_id"] for u in self.users}
        logger.info("FantasyHandler Loaded")

    async def init_listener(self,
            init_draft_callback, new_draft_callback, new_pick_callback,
            init_users_callback, update_users_callback
        ):
        """
        Converted to now listen to user updates too. Fine for now but pretty
        unweildy. Probably better to split sub-events, and route the messages
        into separate queues for each message-type

        TODO this kind of gets "detached" and never cleaned-up/returned.
        As it's meant to run forever that's probably ok
        but could be improved by "top level" function running client and passing into this func,
        then in main can asyncio.gather() on the client + other futures.

        Draft init handling: We get a list of drafts: {
            'draft_id': 'eb824c78-164b-4973-bfac-b283f6e0705f',
            'league_id': 'b3c223bf-0409-4b54-88c7-bbb937c8111c',
            'meta': {},
            'period_id': '4b86d0e3-b6f6-482f-ae3f-5f6caa2afdc2',
            'team_drafts': [{
                'active_picks': [],
                'draft_choices': [],
                'external_user_id': '92de6fac-7df2-49ba-92d7-fff27f5b4d75',
                'fantasy_team_id': '5a4adfa5-2600-4236-9180-103f39435d90',
                'meta': {'discord_id': 143464912868474880},                   'name': 'ctpeepee#1273_team',
                'team_draft_id': '3dbc3d01-b11e-4a58-847a-30a191070523'
                }, ...]
        }

        Im imagining the discord bot calls and uses this.
        the discord bot would define callbacks for when a new draft set
        (i.e. make a channel for the draft)
        as well as for pick-updates
        (if people don't pick in time, it will autopick for them, and that will get published....
        the publishes for picks that people actively made can probably be ignored, as will have handled the response)

        Draft init callback, is for when bot crashes/restarts. Might need to set up internal state of drafts/picks,
        so that users can query when their next pick is scheduled, who the next pickers are, players left, etc.
        :param draft_init_callback:
        :param new_draft_callback:
        :param new_pick_callback:
        :return:
        """
        drafts_resp = await self.client.send_sub_drafts(
            SubDraft(all=True)
        )
        drafts = drafts_resp["data"]
        logger.error(pformat(drafts))

        init_draft_callback(drafts)
        # ! Was already beign subbed to in start !
        # # subscribe to users
        # users_resp = await self.client.send_sub_users(
        #     SubUser(toggle=True)
        # )
        # users = users_resp["data"]["users"]  # do we ever need the other "data"?
        # init_users_callback(users)
        while True:
            new_msg = await self.client.sub_events.get()
            logger.info(f"Fantasy received new msg: {str(new_msg)[:TRUNCATED_MESSAGE_LENGTH]}")
            logger.debug(f"Full message {pformat(new_msg)}")
            if new_msg["message_type"] == "draft":
                new_draft_callback(new_msg)
            elif new_msg["message_type"] == "pick":
                new_pick_callback(new_msg)
            # elif new_msg["message_type"] == "user":
            #     update_users_callback(new_msg)

# TODO For now it's ok to just do a `send_get_latest_leaderboards` on every !leaderboard command,
# However this could be cached by utilising listening to new stat-updates, to trigger a cached-leaderboard-clear.
# async def leaderboard_listen(init_callback, update_callback):
#     # For

# TODO could also listen to new match/player results so could update in chat when a match ended and points attributed.