import asyncio
import datetime
import logging
import uuid

from clients.fantasy_websocket_client import FantasyWebsocketClient

import os
import dotenv

from data.dota_ids import FANTASY_LEAGUE_ID
from messages.fantasy_msgs import PeriodUpdate, SubLeague
from utils.constants import DATE_FMT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dotenv.load_dotenv()
ADDRESS = os.getenv('ADDRESS', '0.0.0.0')


# Probably a better way to do this, but hack for now.
async def update_period(new_draft_start: datetime.datetime, new_draft_lockdown: datetime.datetime, period_id=None):
    fantasy_client = FantasyWebsocketClient(ADDRESS)
    asyncio.create_task(fantasy_client.run())
    if not period_id:
        league_info = await fantasy_client.send_sub_leagues(SubLeague(sub_league_ids=[FANTASY_LEAGUE_ID], all=False))
        print([period["period_id"] for period in league_info["data"][0]["periods"]])
        period_id = input("Which id would you like to update").strip()
    period_updates = [
        PeriodUpdate(str(period_id), draft_start=new_draft_start.strftime(DATE_FMT), draft_lockdown=new_draft_lockdown.strftime(DATE_FMT))
    ]
    await fantasy_client.send_update_periods(period_updates)

asyncio.run(
    update_period(
        datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(seconds=20),
        datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(seconds=10)
    )
)
