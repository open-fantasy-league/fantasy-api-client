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
    sub_league_ids: Optional[List[str]] = None
    unsub_league_ids: Optional[List[str]] = None


@dataclass
class SubLeaderboard:
    """
    Subs to receive Leaderboard messages
    """
    all: bool
    sub_leaderboard_ids: Optional[List[str]] = None
    unsub_leaderboard_ids: Optional[List[str]] = None


@dataclass
class Stat:
    leaderboard_id: str
    player_id: str
    timestamp: str
    points: float
    meta: dict = field(default_factory=dict)
    league_id: Optional[str] = None


@dataclass
class Leaderboard:
    leaderboard_id: str
    league_id: str
    name: str
    timespan: Tuple[str, str]
    meta: dict = field(default_factory=dict)
    stats: Optional[List[Stat]] = None


@dataclass
class LatestStat:
    player_id: str
    leaderboard_id: str
    points: float = 0.0,
