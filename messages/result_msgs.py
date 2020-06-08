import uuid
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

# https://realpython.com/python-data-classes/

# Subscriptions


@dataclass
class SubTeam:
    """
    Subs to receive Team messages
    """
    toggle: bool


@dataclass
class SubCompetition:
    """
    Subs to receive Competition messages
    """
    all: bool
    # Because cant have mutable [] as default
    sub_competition_ids: Optional[List[str]] = None
    unsub_competition_ids: Optional[List[str]] = None


# Insert/Updates
@dataclass
class TeamSeriesResult:
    series_id: str
    team_id: str
    result: str
    meta: dict = field(default_factory=dict)


@dataclass
class TeamMatchResult:
    match_id: str
    team_id: str
    result: str
    meta: dict = field(default_factory=dict)


@dataclass
class PlayerResult:
    match_id: str
    player_id: str
    result: dict
    meta: dict = field(default_factory=dict)


@dataclass
class Match:
    match_id: str
    name: str
    # Timespans are str's as can't implicitly json convert datetimes (could make a custom serializer though)
    timespan: Tuple[str, str]
    series_id: Optional[str] = None
    meta: dict = field(default_factory=dict)
    player_results: Optional[List[PlayerResult]] = None
    team_match_results: Optional[List[TeamMatchResult]] = None


@dataclass
class Series:
    series_id: str
    name: str
    timespan: Tuple[str, str]
    competition_id: Optional[str] = None
    meta: dict = field(default_factory=dict)
    matches: Optional[List[Match]] = None
    team_results: Optional[List[TeamSeriesResult]] = None


@dataclass
class Competition:
    competition_id: str
    name: str
    timespan: Tuple[str, str]
    meta: dict = field(default_factory=dict)
    series: Optional[List[Series]] = None


@dataclass
class PlayerPosition:
    position: str
    timespan: Tuple[str, str]
    player_id: Optional[str] = None


@dataclass
class PlayerName:
    name: str
    timespan: Tuple[str, str]
    player_id: Optional[str] = None


@dataclass
class Player:
    player_id: str
    meta: dict = field(default_factory=dict)
    names: Optional[List[PlayerName]] = None
    positions: Optional[List[PlayerPosition]] = None


@dataclass
class TeamName:
    name: str
    timespan: Tuple[str, str]
    team_id: Optional[str] = None


@dataclass
class TeamPlayer:
    team_id: str
    timespan: Tuple[str, str]
    # player-id present when inserting
    player_id: Optional[str] = None
    # player presenting in published messages
    player: Optional[Player] = None

@dataclass
class Team:
    team_id: str
    meta: dict = field(default_factory=dict)
    names: Optional[List[TeamName]] = None
    players: Optional[List[TeamPlayer]] = None
