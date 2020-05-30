from collections import namedtuple
import uuid
from dataclasses import dataclass, field
from typing import Optional, List, Tuple


# Subscriptions


@dataclass
class SubLeague:
    """
    Subs to receive Leaderboard messages
    """
    all: bool
    sub_league_ids: Optional[List[uuid.UUID]] = None
    unsub_league_ids: Optional[List[uuid.UUID]] = None


@dataclass
class SubLeaderboard:
    """
    Subs to receive Leaderboard messages
    """
    all: bool
    sub_leaderboard_ids: Optional[List[uuid.UUID]] = None
    unsub_leaderboard_ids: Optional[List[uuid.UUID]] = None


@dataclass
class Stat:
    leaderboard_id: uuid.UUID
    player_id: uuid.UUID
    name: str
    timestamp: str
    points: float
    meta: dict = field(default_factory=dict)
    league_id: Optional[uuid.UUID] = None


@dataclass
class Leaderboard:
    leaderboard_id: uuid.UUID
    league_id: uuid.UUID
    name: str
    timespan: Tuple[str, str]
    meta: dict = field(default_factory=dict)
    stats: Optional[List[Stat]] = None

