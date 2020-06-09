import asyncio
import datetime
import logging
import os
import uuid
from pprint import pformat
from typing import Dict, Optional, List

from clients.fantasy_websocket_client import FantasyWebsocketClient
from clients.result_websocket_client import ResultWebsocketClient
from clients.leaderboard_websocket_client import LeaderboardWebsocketClient
from messages.leaderboard_msgs import SubLeague
from messages.fantasy_msgs import SubDraft, SubUser, SubLeague, FantasyTeam, ExternalUser
from messages.result_msgs import SubTeam
from utils.errors import ApiException
from utils.utils import simplified_str
from utils.constants import TRUNCATED_MESSAGE_LENGTH, DATE_FMT

logger = logging.getLogger(__name__)

ZERO_TIME_DELTA = datetime.timedelta(0)


class LeaderboardHandler:

    def __init__(self):
        self.client = LeaderboardWebsocketClient(os.getenv('ADDRESS', '0.0.0.0'))
        self.leaderboards = None

    async def start(self):
        """
        Start running client and run initial set up
        """
        logger.info('LeaderboardHandler starting')
        asyncio.create_task(self.client.run())
        logger.info("FantasyHandler Loaded")

    async def init_listener(self, init_leaderboard_callback, update_leaderboard_callback):
        """
        Docstring

        Resp of form:
        {
            'data': [{
            'leaderboard_id': '0ce24e8c-cede-4c0a-9493-a1b5a3b6dee1',
            'league_id': 'b3c223bf-0409-4b54-88c7-bbb937c8111c',
            'meta': {},
            'name': 'Blast Bounty Hunt Player Points',
            'stats': [{
                        'leaderboard_id': '0ce24e8c-cede-4c0a-9493-a1b5a3b6dee1',
                        'meta': {},
                        'player_id': 'bfece248-b37f-43aa-9a2b-99a839776afc',
                        'points': 244.15099,
                        'timestamp': '2020-06-07T20:13:47Z'
                    }, ...]
            }, ...],
            'message_id': '3480e839-f6c5-427d-a014-83a8e1733af5',
            'message_type': 'SubLeague',
            'mode': 'resp'
        }
        """
        logger.info("LeaderboardHandler:init_listener: send sub leagues")
        leagues_resp = await self.client.send_sub_leagues(SubLeague(all=True))
        if leagues_resp["mode"] != "resp":
            logger.error("LeaderboardHandler:init_listener: invalid response")
            return
        self.leaderboards = leagues_resp["data"]
        logger.info("LeaderboardHandler:init_listener: init leaderboard callback")
        await init_leaderboard_callback(self.leaderboards)
        # updates
        logger.info("LeaderboardHandler:init_listener: start listening")


        while True:
            new_msg = await self.client.sub_events.get()
            logger.info(f"LeaderboardHandler:listener: Received new msg: {str(new_msg)[:TRUNCATED_MESSAGE_LENGTH]}")
            logger.debug(f"LeaderboardHandler:listener: Full message {pformat(new_msg)}")
            # we shuold only get one type of message
            #     pub struct ApiLeaderboardLatest {
            #         pub leaderboard_id: Uuid,
            #         pub league_id:      Uuid,
            #         pub name:           String,
            #         pub meta: serde_json::Value,
            #         pub leaderboard: Vec<ApiLatestStat>,
            #     }
            #     pub struct ApiLatestStat {
            #         #[sql_type = "sql_types::Uuid"]
            #         pub player_id: Uuid,
            #         #[sql_type = "sql_types::Uuid"]
            #         pub leaderboard_id: Uuid,
            #         #[sql_type = "sql_types::Double"]
            #         pub points: f64,
            #     }
            if new_msg["message_type"] == "leaderboard_latest":
                # TODO update self.leaderboards with what has changed
                # TODO update callback only leaderboards that have changed
                updated_leaderboards = self.leaderboards
                update_leaderboard_callback(updated_leaderboards)
            else:
                logger.error(f'LeaderboardHandler:listener: Unexpected message type: {new_msg["message_type"]}')


# TODO could also listen to new match/player results so could update in chat when a match ended and points attributed.
class PlayerHandler:

    def __init__(self):
        self.result_client = ResultWebsocketClient(os.getenv('ADDRESS', '0.0.0.0'))
        # better to init to None, than empty list/dict, as then more obvious when someone
        # forgets to await start()
        self.teams_and_players = None
        self.players = None
        self.player_id_to_names = None
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
        self.player_id_to_names = {p["player_id"]: p["names"][0]["name"] for p in self.players}
        logger.info("Loaded PlayerHandler")


class FantasyHandler:

    def __init__(self):
        self.client = FantasyWebsocketClient(os.getenv('ADDRESS', '0.0.0.0'))
        self.users: Optional[Dict[str, ExternalUser]] = None
        self.discord_user_id_to_fantasy_id = None
        self.league = None
        self.user_id_to_team: Optional[Dict[str, FantasyTeam]] = None
        self.team_id_to_user_id: Dict[str, str] = {}
        self.drafts = None
        self.team_id_to_draft_id = None
        self.draft_ids_to_channel_ids = {}
        self.channel_ids_to_draft_ids = {}
        self.draft_choices = None
        self.draft_players_picked = {}

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
        user_resp = await self.client.send_sub_users(SubUser(toggle=True))
        # WARNING
        # bit of a mess but user-id always uuid, draft_id always str
        self.users = {str(u["external_user_id"]): ExternalUser(**u) for u in user_resp["data"]["users"]}
        logger.info(f"FantasyHandler received {len(self.users)} users")
        logger.debug(f'FantasyHandler users received: {pformat(self.users)}')
        self.discord_user_id_to_fantasy_id = {u.meta["discord_id"]: u.external_user_id for u in self.users.values()}
        league_resp = (await self.client.send_sub_leagues(SubLeague(all=True)))["data"]
        if league_resp:
            self.league = (await self.client.send_sub_leagues(SubLeague(all=True)))["data"][0]
            self.user_id_to_team = {str(t["external_user_id"]): FantasyTeam(**t) for t in self.league["fantasy_teams"]}
            self.team_id_to_user_id = {t["fantasy_team_id"]: t["external_user_id"] for t in self.league["fantasy_teams"]}
        else:
            self.user_id_to_team = {}
            self.league = None

        drafts_resp = await self.client.send_sub_drafts(SubDraft(all=True))
        self.drafts = {draft["draft_id"]: draft for draft in drafts_resp["data"]}
        self.team_id_to_draft_id = {str(team["fantasy_team_id"]): d["draft_id"] for d in self.drafts.values() for team in d["team_drafts"]}
        for draft in self.drafts.values():
            self.draft_ids_to_channel_ids[draft["draft_id"]] = draft["meta"].get("channel_id")
            self.channel_ids_to_draft_ids[draft["meta"].get("channel_id")] = draft["draft_id"]

            self.draft_players_picked[draft["draft_id"]] = {
                pick["player_id"] for td in draft["team_drafts"] for pick in td["active_picks"]
            }

        self.draft_choices = {
            d["draft_id"]: self.sorted_draft_choices(d) for d in self.drafts.values()
        }
        logger.info("FantasyHandler Loaded")

    def sorted_draft_choices(self, draft):
        out = sorted(
                [
                    {"username": self.users[str(t["external_user_id"])].name, "choice": [datetime.datetime.strptime(c, DATE_FMT) for c in choice["timespan"]]}
                    for t in draft["team_drafts"] for choice in t["draft_choices"]
                ],
                key=lambda x: x["choice"][0]
            )
        return out

    @staticmethod
    def printable_time_until_choice(user_and_choice, now):
        choice = user_and_choice["choice"]
        time_until_start = choice[0] - now
        time_until_end = choice[1] - now
        if time_until_start < ZERO_TIME_DELTA:
            # have to recalc otherwise the minus one comes out weird
            return f"{user_and_choice['username']} {time_until_end.seconds}s left"
        else:
            return f"{user_and_choice['username']} can pick in {time_until_end.seconds}s"

    def future_draft_choices(self, draft_id, limit=6, filter_first=True, and_time=False):
        """

        :param draft_id:
        :param limit:
        :param filter_first: hacky way of when someone does a pick, it doesnt return that they still have to pick
        :return:
        """
        choices = self.draft_choices[draft_id]
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        filtered_choices = []
        for c in choices:
            if len(filtered_choices) > limit:
                break
            if c["choice"][-1] > now:
                if and_time:
                    filtered_choices.append(self.printable_time_until_choice(c, now))
                else:
                    filtered_choices.append(c["username"])
        if filter_first:
            filtered_choices = filtered_choices[1:]
        if not filtered_choices:
            return ""
        return "**next picks:**\n\n" + ", ".join(filtered_choices)

    def get_user_team(self, discord_id):
        fantasy_user_id = self.discord_user_id_to_fantasy_id[discord_id]
        return self.user_id_to_team[fantasy_user_id]

    def get_user_by_team_id(self, team_id):
        try:
            user_id = self.team_id_to_user_id[team_id]
        except KeyError:
            raise Exception(f"Could not find user for team_id {team_id}")
        return self.users[user_id]

    async def add_user(self, ctx, user, team, discord_id):
        try:
            await self.client.send_insert_users([user])
            # It's a bit faffy having to update so much state here, but it'll do for now
            self.discord_user_id_to_fantasy_id[discord_id] = user.external_user_id  # update internal state @WEAK
            self.user_id_to_team[user.external_user_id] = team
            self.team_id_to_user_id[team.fantasy_team_id] = user.external_user_id
            self.users[user.external_user_id] = user
            await self.client.send_insert_fantasy_teams([team])
            await ctx.send(f'Congratulations {ctx.author.name} you have succesfully joined the league!')
        except ApiException:
            logger.exception(f'join command incorrect response')
            await ctx.send(f'Sorry {ctx.author.name} something went wrong, please try again or contact an admin')

    async def init_listener(self,
            init_draft_callback, new_draft_callback, new_pick_callback,
            init_users_callback, update_users_callback, player_handler
        ):
        # It's a bit spaghetti putting player_handler into here. Suggests designed wrong, but just want to get it to work for now
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
        # logger.error(pformat(drafts))

        init_draft_callback(drafts)

        while True:
            new_msg = await self.client.sub_events.get()
            logger.info(f"Fantasy received new msg: {new_msg['message_type']}")
            logger.debug(f"Full message {pformat(new_msg)}")
            if new_msg["message_type"] == "draft":
                new_drafts = await self.on_new_draft(new_msg)
                await new_draft_callback(new_drafts)
            elif new_msg["message_type"] == "pick":
                pick = await self.on_new_pick(new_msg, player_handler)
                await new_pick_callback(pick)
            # elif new_msg["message_type"] == "user":
            #     update_users_callback(new_msg)

    async def on_new_draft(self, msg):
        new_drafts = []
        for draft in msg["data"]:
            draft_id = draft["draft_id"]
            if draft_id in self.drafts:
                logger.warning(f'Update for a draft that we already knew about {draft_id}')
                continue

            logger.info("Preparing new draft state/channel")
            self.drafts[draft_id] = draft
            self.draft_choices[draft_id] = self.sorted_draft_choices(draft)
            # WHilst yes this is overwriting the existing value, that's what we want.
            # When the draft for day 2 is created...day 1's draft will be done and dusted,
            # so it's correct to replace it.
            for team in draft["team_drafts"]:
                self.team_id_to_draft_id[str(team["fantasy_team_id"])] = draft_id
            # TODO populate this on_init_draft for if bot crash
            self.draft_players_picked[draft_id] = set()
            new_drafts.append(draft)
        return new_drafts

    async def on_new_pick(self, msg, player_handler):
        for pick in msg["data"]:
            try:
                player_name = player_handler.player_id_to_names[pick["player_id"]]
            except KeyError as e:
                logger.error(f'New pick callback could not find player-id {e}')
                continue
            fantasy_team_id = str(pick["fantasy_team_id"])
            user = self.get_user_by_team_id(fantasy_team_id)
            draft_id = pick["draft_id"]
            logger.info(f'FantasyHandler:on_new_pick: {user.name} picked {player_name} in draft {draft_id}')
            if self.draft_players_picked[draft_id] is None:
                logger.error(f"FantasyHandler:on_new_pick: couldnt find players picked for draft {draft_id}")
            else:
                self.draft_players_picked[draft_id].add(pick["player_id"])
            return (user, draft_id, player_name)
