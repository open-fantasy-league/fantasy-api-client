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
    period_id: uuid.UUID
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
class PeriodUpdate:
    period_id: uuid.UUID
    name: Optional[str] = None
    timespan: Optional[Tuple[str, str]] = None
    points_multiplier: Optional[float] = None
    teams_per_draft: Optional[int] = None
    draft_interval_secs: Optional[int] = None
    draft_start: Optional[str] = None

    # Draft-lockdown is the time when server locks in users who are playing, and sets the draft choice order.
    # (i.e. anybody who joins league after draft lockdown, doesnt get a draft for that period. they sit out)
    draft_lockdown: Optional[str] = None
    meta: Optional[dict] = None


@dataclass
class StatMultiplier:
    name: str
    multiplier: float
    meta: dict = field(default_factory=dict)
    league_id: Optional[uuid.UUID] = None


@dataclass
class FantasyTeam:
    fantasy_team_id: uuid.UUID
    external_user_id: uuid.UUID
    league_id: uuid.UUID
    name: str
    meta: dict = field(default_factory=dict)


@dataclass
class MaxPlayersPerPosition:
    position: str
    team_max: int
    squad_max: int
    league_id: Optional[uuid.UUID] = None


@dataclass
class League:
    league_id: uuid.UUID
    name: str
    competition_id: uuid.UUID
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
    max_players_per_position: Optional[List[MaxPlayersPerPosition]] = None


@dataclass
class ExternalUser:
    external_user_id: uuid.UUID
    name: str
    meta: dict = field(default_factory=dict)


@dataclass
class DraftQueue:
    fantasy_team_id: uuid.UUID
    player_ids: List[uuid.UUID]


@dataclass
class Pick:
    """
    WARNING! You prob want to use draft_pick instead
    A pick in the squad for timespan T. May or may not be in the team, needs an ActivePick entry to be in team.
    (currently ive hacked server so inserting pick will isnert active-pick)
    """
    pick_id: uuid.UUID
    player_id: uuid.UUID
    timespan: Tuple[str, str]
    fantasy_team_id: Optional[uuid.UUID] = None
    draft_choice_id: Optional[uuid.UUID] = None


@dataclass
class DraftPick:
    """
    Use this over Pick, for when user makes a pick. Pick is more for non-drafty scenarios
    """
    player_id: uuid.UUID
    fantasy_team_id: uuid.UUID
    draft_id: uuid.UUID  # So that it knows what timespan the pick should be valid for.


@dataclass
class DraftChoice:
    draft_choice_id: uuid.UUID
    timespan: Tuple[str, str]
    pick: Optional[Pick] = None


@dataclass
class ActivePick:
    """
    THis is a pick that is actually in the team, and can score points earned for that player_id during this timespan
    """
    active_pick_id: uuid.UUID
    pick_id: uuid.UUID
    timespan: Tuple[str, str]


#######################

# Received only
########################


@dataclass
class TeamDraft:
    team_draft_id: uuid.UUID
    fantasy_team_id: uuid.UUID
    name: str
    external_user_id: uuid.UUID
    meta: dict = field(default_factory=dict)
    draft_choices: Optional[List[DraftChoice]] = None
    active_picks: Optional[List[Pick]] = None


@dataclass
class Draft:
    league_id: uuid.UUID
    draft_id: uuid.UUID
    period_id: uuid.UUID
    meta: dict = field(default_factory=dict)
    team_drafts: Optional[List[TeamDraft]] = None


@dataclass
class DraftUpdate:
    draft_id: uuid.UUID
    meta: dict = field(default_factory=dict)


@dataclass
class ValidPlayer:
    player_id: uuid.UUID
    period_id: uuid.UUID
