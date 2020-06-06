import asyncio
import datetime
import uuid

from clients.fantasy_websocket_client import FantasyWebsocketClient

import os
import dotenv

from messages.fantasy_msgs import PeriodUpdate
from utils.constants import DATE_FMT

dotenv.load_dotenv()
ADDRESS = os.getenv('ADDRESS', '0.0.0.0')


# Probably a better way to do this, but hack for now.
async def update_period(period_id: str, new_draft_start: datetime.datetime, new_draft_lockdown: datetime.datetime):
    fantasy_client = FantasyWebsocketClient(ADDRESS)
    asyncio.create_task(fantasy_client.run())
    period_updates = [
        PeriodUpdate(uuid.UUID(period_id), draft_start=new_draft_start.strftime(DATE_FMT), draft_lockdown=new_draft_lockdown.strftime(DATE_FMT))
    ]
    await fantasy_client.send_update_periods(period_updates)

asyncio.run(
    update_period(
        "find id from database, or creaate-league, or subLeague response",
        datetime.datetime.now(tz=datetime.timezone.utc),
        datetime.datetime.now(tz=datetime.timezone.utc)
    )
)
