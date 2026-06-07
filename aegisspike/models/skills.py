from pydantic import BaseModel, Field

from aegisspike.models.enums import SkillType


class SkillData(BaseModel):
    name: str
    skill_type: SkillType
    cast_time_ms: int = Field(default=1000, description="Activation time in ms")
    recharge_ms: int = Field(default=0, description="Recharge/cooldown in ms")
    energy_cost: int = Field(default=5)
    is_elite: bool = Field(default=False)
    is_hex_removal: bool = Field(default=False, description="Can remove hexes (Smite Hex, etc.)")
    is_condition_removal: bool = Field(default=False)
    is_primary_threat_hex: bool = Field(default=False, description="High-value hex")
    is_defensive_save: bool = Field(default=False, description="Prot Spirit, Spirit Bond, etc.")
    causes_deep_wound: bool = Field(default=False)
    causes_daze: bool = Field(default=False)
    causes_knockdown: bool = Field(default=False)
    expected_duration_ms: int = Field(default=0, description="Duration of hex/enchant/condition")
