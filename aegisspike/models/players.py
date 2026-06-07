from pydantic import BaseModel, Field

from aegisspike.models.enums import Archetype, PlayerState, Team, WeaponSet


class Player(BaseModel):
    name: str
    team: Team
    archetype: Archetype = Field(default=Archetype.UNKNOWN)
    current_state: PlayerState = Field(default=PlayerState.S0_NEUTRAL)
    current_weapon_set: WeaponSet = Field(default=WeaponSet.UNKNOWN)
    max_hp: int = Field(default=480, description="Estimated max HP for the build")
    max_energy: int = Field(default=30, description="Estimated max energy for the build")
    skills: list[str] = Field(default_factory=list, description="Known skills from log activity")


class PlayerRoster(BaseModel):
    players: list[Player] = Field(default_factory=list)

    def get_player(self, name: str) -> Player | None:
        for p in self.players:
            if p.name == name:
                return p
        return None

    def get_team(self, team: Team) -> list[Player]:
        return [p for p in self.players if p.team == team]

    @property
    def team_a(self) -> list[Player]:
        return self.get_team(Team.TEAM_A)

    @property
    def team_b(self) -> list[Player]:
        return self.get_team(Team.TEAM_B)
