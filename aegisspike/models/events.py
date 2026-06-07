from pydantic import BaseModel, Field

from aegisspike.models.enums import EventType, SpikeOutcome, WeaponSet


class CombatEvent(BaseModel):
    timestamp_ms: int = Field(description="Milliseconds since match start")
    source: str = Field(description="Player who initiated the action")
    target: str = Field(description="Player affected by the action")
    event_type: EventType
    skill: str = Field(default="", description="Skill name, empty for auto-attacks")
    value: float = Field(default=0.0, description="Numeric value (damage, healing, energy)")
    weapon_set: WeaponSet = Field(default=WeaponSet.UNKNOWN)

    @property
    def timestamp_s(self) -> float:
        return self.timestamp_ms / 1000.0


class DeathEvent(BaseModel):
    timestamp_ms: int
    target: str
    killer: str = Field(default="", description="Last-hit player if identifiable")


class HexConditionState(BaseModel):
    skill: str
    source: str
    target: str
    applied_ms: int
    expected_duration_ms: int = Field(default=0)
    removed_ms: int | None = Field(default=None)

    @property
    def end_influence_ms(self) -> int:
        if self.removed_ms is not None:
            return self.removed_ms
        return self.applied_ms + self.expected_duration_ms

    @property
    def is_active(self) -> bool:
        return self.removed_ms is None


class SpikeEvent(BaseModel):
    spike_id: int = Field(default=0)
    target: str
    t_start_ms: int
    t_end_ms: int | None = Field(default=None)
    outcome: SpikeOutcome = Field(default=SpikeOutcome.IN_PROGRESS)
    peak_damage: float = Field(default=0.0, description="Max cumulative damage in window")
    participants: list[str] = Field(default_factory=list)
    events: list[CombatEvent] = Field(default_factory=list)

    @property
    def duration_ms(self) -> int | None:
        if self.t_end_ms is None:
            return None
        return self.t_end_ms - self.t_start_ms
