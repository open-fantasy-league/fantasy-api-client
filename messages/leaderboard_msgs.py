from collections import namedtuple
import uuid
from dataclasses import dataclass, field
from typing import Optional, List, Tuple


# Subscriptions


@dataclass
class SubLeague:
    all: bool
    sub_league_ids: Optional[List[uuid]] = None
    unsub_league_ids: Optional[List[uuid]] = None


@dataclass
class SubLeaderboard:
    all: bool
    sub_leaderboard_ids: Optional[List[uuid]] = None
    unsub_leaderboard_ids: Optional[List[uuid]] = None


@dataclass
class Leaderboard:
    leaderboard_id: uuid
    league_id: uuid
    name: str
    timespan: Tuple[str, str]
    meta: dict = field(default_factory=dict)


@dataclass
class Stat:
    leaderboard_id: uuid
    player_id: uuid
    name: str
    timestamp: str
    points: float
    meta: dict = field(default_factory=dict)
    league_id: Optional[uuid] = None
