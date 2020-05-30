import asyncio

from clients.fantasy_websocket_client import FantasyWebsocketClient
from messages.fantasy_msgs import SubDraft


async def draft_listen(draft_init_callback, new_draft_callback, new_pick_callback):
    """
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
    fantasy_client = FantasyWebsocketClient()
    # TODO this kind of gets "detached" and never cleaned-up/returned.
    # As it's meant to run forever that's probably ok
    # but could be improved by "top level" function running client and passing into this func,
    # then in main can asyncio.gather() on the client + other futures.
    asyncio.create_task(fantasy_client.run())
    drafts = await fantasy_client.send_sub_drafts(
        SubDraft(all=True)
    )
    draft_init_callback(drafts)
    while True:
        new_msg = fantasy_client.sub_events.get()
        print(f"Draft listener received new msg: {new_msg}")
        if new_msg["message_type"] == "draft":
            new_draft_callback(new_msg)
        elif new_msg["message_type"] == "pick":
            new_pick_callback(new_msg)


# TODO For now it's ok to just do a `send_get_latest_leaderboards` on every !leaderboard command,
# However this could be cached by utilising listening to new stat-updates, to trigger a cached-leaderboard-clear.
# async def leaderboard_listen(init_callback, update_callback):
#     # For

# TODO could also listen to new match/player results so could update in chat when a match ended and points attributed.