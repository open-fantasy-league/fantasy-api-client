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


# pub struct ApiLeaderboardLatest {
#     pub leaderboard_id: Uuid,
#     pub league_id:      Uuid,
#     pub name:           String,
#     pub meta: serde_json::Value,
#     pub leaderboard: Vec<ApiLatestStat>,
# }
@dataclass
class Leaderboard:
    leaderboard_id: str
    league_id: str
    name: str
    timespan: Optional[Tuple[str, str]] = None
    meta: dict = field(default_factory=dict)
    leaderboard: Optional[List[Stat]] = None


# pub struct ApiLatestStat {
#     #[sql_type = "sql_types::Uuid"]
#     pub player_id: Uuid,
#     #[sql_type = "sql_types::Uuid"]
#     pub leaderboard_id: Uuid,
#     #[sql_type = "sql_types::Double"]
#     pub points: f64,
# }
@dataclass
class LatestStat:
    player_id: str
    leaderboard_id: str
    points: float = 0.0,
