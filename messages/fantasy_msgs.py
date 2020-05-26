import uuid
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

# Subscriptions


@dataclass
class SubUser:
    toggle: bool


@dataclass
class SubLeague:
    all: bool
    sub_league_ids: Optional[List[uuid]] = None
    unsub_league_ids: Optional[List[uuid]] = None


@dataclass
class SubDraft:
    all: bool
    sub_draft_ids: Optional[List[uuid]] = None
    unsub_draft_ids: Optional[List[uuid]] = None


# Insert/Updates

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
    league_id: Optional[uuid] = None


@dataclass
class StatMultiplier:
    name: str
    multiplier: float
    meta: dict = field(default_factory=dict)
    league_id: Optional[uuid] = None


@dataclass
class ExternalUser:
    external_user_id: uuid
    name: str
    meta: dict = field(default_factory=dict)


@dataclass
class FantasyTeam:
    fantasy_team_id: uuid
    external_user_id: uuid
    league_id: uuid
    name: str
    meta: dict = field(default_factory=dict)


@dataclass
class DraftQueue:
    fantasy_team_id: uuid
    player_ids: List[uuid]


@dataclass
class DraftChoice:
    draft_choice_id: uuid
    timespan: Tuple[str, str]


@dataclass
class Pick:
    """
    A pick in the squad for timespan T. May or may not be in the team, needs an ActivePick entry to be in team.
    """
    pick_id: uuid
    fantasy_team_id: uuid
    draft_choice_id: uuid
    player_id: uuid
    timespan: Tuple[str, str]


@dataclass
class ActivePick:
    """
    THis is a pick that is actually in the team, and can score points earned for that player_id during this timespan
    """
    active_pick_id: uuid
    pick_id: uuid
    timespan: Tuple[str, str]


#######################

# Received
########################

# ExternalUser is received as well as sent
"""
#[derive(Deserialize, Serialize, Debug)]
pub struct ApiLeague {
    pub league_id: Uuid,
    pub name: String,
    pub team_size: i32,
    pub squad_size: i32,
    pub competition_id: Uuid,
    pub meta: serde_json::Value,
    pub max_squad_players_same_team: i32,
    pub max_squad_players_same_position: i32,
    pub max_team_players_same_team: i32,
    pub max_team_players_same_position: i32,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub periods: Option<Vec<Period>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub stat_multipliers: Option<Vec<StatMultiplier>>,
    pub fantasy_teams: Option<Vec<FantasyTeam>>,
}


#[derive(Deserialize, Serialize, Debug)]
pub struct ApiDraft {
    pub league_id: Uuid,
    pub draft_id: Uuid,
    pub period_id: Uuid,
    pub meta: serde_json::Value,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub team_drafts: Option<Vec<ApiTeamDraft>>,
}


"""