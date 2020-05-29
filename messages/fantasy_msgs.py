import uuid
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

# Subscriptions


@dataclass
class SubUser:
    """
    Subs to receive ExternalUser messages when they update
    """
    toggle: bool


@dataclass
class SubLeague:
    """
    Subs to receive League messages when they update
    """
    all: bool
    sub_league_ids: Optional[List[uuid.UUID]] = None
    unsub_league_ids: Optional[List[uuid.UUID]] = None


@dataclass
class SubDraft:
    """
    Subs to receive Draft messages when they update
    """
    all: bool
    sub_draft_ids: Optional[List[uuid.UUID]] = None
    unsub_draft_ids: Optional[List[uuid.UUID]] = None


# Insert/Updates

@dataclass
class Period:
    period_id: uuid
    name: str
    timespan: Tuple[str, str]
    points_multiplier: float
    teams_per_draft: int
    draft_interval_secs: int
    draft_start: str

    # Draft-lockdown is the time when server locks in users who are playing, and sets the draft choice order.
    # (i.e. anybody who joins league after draft lockdown, doesnt get a draft for that period. they sit out)
    draft_lockdown: str
    meta: dict = field(default_factory=dict)
    league_id: Optional[uuid.UUID] = None


@dataclass
class StatMultiplier:
    name: str
    multiplier: float
    meta: dict = field(default_factory=dict)
    league_id: Optional[uuid.UUID] = None


@dataclass
class FantasyTeam:
    fantasy_team_id: uuid
    external_user_id: uuid
    league_id: uuid
    name: str
    meta: dict = field(default_factory=dict)


@dataclass
class League:
    league_id: uuid
    name: str
    competition_id: uuid
    team_size: int
    squad_size: int
    max_squad_players_same_team: int
    max_squad_players_same_position: int
    max_team_players_same_team: int
    max_team_players_same_position: int
    meta: dict = field(default_factory=dict)
    periods: Optional[List[Period]] = None
    stat_multipliers: Optional[List[StatMultiplier]] = None
    fantasy_teams: Optional[List[FantasyTeam]] = None


@dataclass
class ExternalUser:
    external_user_id: uuid
    name: str
    meta: dict = field(default_factory=dict)


@dataclass
class DraftQueue:
    fantasy_team_id: uuid
    player_ids: List[uuid.UUID]


@dataclass
class Pick:
    """
    A pick in the squad for timespan T. May or may not be in the team, needs an ActivePick entry to be in team.
    """
    pick_id: uuid
    player_id: uuid
    timespan: Tuple[str, str]
    fantasy_team_id: Optional[uuid.UUID] = None
    draft_choice_id: Optional[uuid.UUID] = None


@dataclass
class DraftChoice:
    draft_choice_id: uuid
    timespan: Tuple[str, str]
    pick: Optional[Pick] = None


@dataclass
class ActivePick:
    """
    THis is a pick that is actually in the team, and can score points earned for that player_id during this timespan
    """
    active_pick_id: uuid
    pick_id: uuid
    timespan: Tuple[str, str]


#######################

# Received only
########################


@dataclass
class TeamDraft:
    team_draft_id: uuid
    fantasy_team_id: uuid
    name: str
    external_user_id: uuid
    meta: dict = field(default_factory=dict)
    draft_choices: Optional[List[DraftChoice]] = None
    active_picks: Optional[List[Pick]] = None


@dataclass
class Draft:
    league_id: uuid
    draft_id: uuid
    period_id: uuid
    meta: dict = field(default_factory=dict)
    team_drafts: Optional[List[TeamDraft]] = None
