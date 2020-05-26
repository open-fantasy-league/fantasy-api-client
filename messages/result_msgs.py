import uuid
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

# https://realpython.com/python-data-classes/

# Subscriptions


@dataclass
class SubTeam:
    toggle: bool


@dataclass
class SubCompetition:
    all: bool
    # Because cant have mutable [] as default
    sub_competition_ids: Optional[List[uuid]] = None
    unsub_competition_ids: Optional[List[uuid]] = None


# Insert/Updates
@dataclass
class TeamSeriesResult:
    series_id: uuid
    team_id: uuid
    result: str
    meta: dict = field(default_factory=dict)


@dataclass
class TeamMatchResult:
    match_id: uuid
    team_id: uuid
    result: str
    meta: dict = field(default_factory=dict)


@dataclass
class PlayerResult:
    match_id: uuid
    player_id: uuid
    result: dict
    meta: dict = field(default_factory=dict)


@dataclass
class Match:
    match_id: uuid
    name: str
    # Timespans are str's as can't implicitly json convert datetimes (could make a custom serializer though)
    timespan: Tuple[str, str]
    series_id: Optional[uuid] = None
    meta: dict = field(default_factory=dict)
    player_results: Optional[List[PlayerResult]] = None
    team_match_results: Optional[List[TeamMatchResult]] = None


@dataclass
class Series:
    series_id: uuid
    name: str
    timespan: Tuple[str, str]
    competition_id: Optional[uuid] = None
    meta: dict = field(default_factory=dict)
    matches: Optional[List[Match]] = None
    team_results: Optional[List[TeamSeriesResult]] = None


@dataclass
class Competition:
    competition_id: uuid
    name: str
    timespan: Tuple[str, str]
    meta: dict = field(default_factory=dict)
    series: Optional[List[Series]] = None


@dataclass
class PlayerPosition:
    position: str
    timespan: Tuple[str, str]
    player_id: Optional[uuid] = None


@dataclass
class PlayerName:
    name: str
    timespan: Tuple[str, str]
    player_id: Optional[uuid] = None


@dataclass
class Player:
    player_id: uuid
    meta: dict = field(default_factory=dict)
    names: Optional[List[PlayerName]] = None
    positions: Optional[List[PlayerPosition]] = None


@dataclass
class TeamName:
    name: str
    timespan: Tuple[str, str]
    team_id: Optional[uuid] = None


@dataclass
class Team:
    team_id: uuid
    meta: dict = field(default_factory=dict)
    names: Optional[List[TeamName]] = None


@dataclass
class TeamPlayer:
    team_id: uuid
    player_id: uuid
    timespan: Tuple[str, str]
