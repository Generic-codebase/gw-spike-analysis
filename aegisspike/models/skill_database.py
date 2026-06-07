"""Seed database of GvG-relevant skills with metadata for the attribution engine.

This is not exhaustive — it covers the skills explicitly referenced in the
AegisSpike spec plus the most common GvG staples. The parser uses this to
resolve cast times, recharges, and tactical flags (primary-threat hex,
defensive save, etc.) without requiring the user to supply a skill list.
"""

from aegisspike.models.enums import SkillType
from aegisspike.models.skills import SkillData

SKILL_DB: dict[str, SkillData] = {}


def _add(s: SkillData) -> None:
    SKILL_DB[s.name.lower()] = s


def lookup(name: str) -> SkillData | None:
    return SKILL_DB.get(name.strip().lower())


# ---------------------------------------------------------------------------
# Warrior — frontline spike damage
# ---------------------------------------------------------------------------
_add(SkillData(
    name="Eviscerate",
    skill_type=SkillType.ATTACK,
    cast_time_ms=0,
    recharge_ms=8000,
    energy_cost=5,
    is_elite=True,
    causes_deep_wound=True,
))
_add(SkillData(
    name="Executioner's Strike",
    skill_type=SkillType.ATTACK,
    cast_time_ms=0,
    recharge_ms=5000,
    energy_cost=5,
))
_add(SkillData(
    name="Bull's Strike",
    skill_type=SkillType.ATTACK,
    cast_time_ms=0,
    recharge_ms=10000,
    energy_cost=5,
    causes_knockdown=True,
))
_add(SkillData(
    name="Dismember",
    skill_type=SkillType.ATTACK,
    cast_time_ms=0,
    recharge_ms=8000,
    energy_cost=5,
    causes_deep_wound=True,
))
_add(SkillData(
    name="Frenzy",
    skill_type=SkillType.STANCE,
    cast_time_ms=0,
    recharge_ms=4000,
    energy_cost=0,
))
_add(SkillData(
    name="Rush",
    skill_type=SkillType.STANCE,
    cast_time_ms=0,
    recharge_ms=8000,
    energy_cost=5,
))

# ---------------------------------------------------------------------------
# Paragon — spike support and shouts
# ---------------------------------------------------------------------------
_add(SkillData(
    name="\"Go for the Eyes!\"",
    skill_type=SkillType.SHOUT,
    cast_time_ms=0,
    recharge_ms=4000,
    energy_cost=5,
))
_add(SkillData(
    name="Cruel Spear",
    skill_type=SkillType.ATTACK,
    cast_time_ms=0,
    recharge_ms=10000,
    energy_cost=5,
    causes_deep_wound=True,
))

# ---------------------------------------------------------------------------
# Mesmer — disruption, hexes, shutdown
# ---------------------------------------------------------------------------
_add(SkillData(
    name="Diversion",
    skill_type=SkillType.HEX,
    cast_time_ms=2000,
    recharge_ms=10000,
    energy_cost=10,
    expected_duration_ms=6000,
))
_add(SkillData(
    name="Shame",
    skill_type=SkillType.HEX,
    cast_time_ms=1000,
    recharge_ms=10000,
    energy_cost=10,
    expected_duration_ms=8000,
))
_add(SkillData(
    name="Power Drain",
    skill_type=SkillType.SPELL,
    cast_time_ms=250,
    recharge_ms=15000,
    energy_cost=5,
))
_add(SkillData(
    name="Power Leak",
    skill_type=SkillType.SPELL,
    cast_time_ms=250,
    recharge_ms=20000,
    energy_cost=10,
))
_add(SkillData(
    name="Cry of Frustration",
    skill_type=SkillType.SPELL,
    cast_time_ms=0,
    recharge_ms=15000,
    energy_cost=5,
))

# ---------------------------------------------------------------------------
# Necromancer — hexes, cover hexes, pressure
# ---------------------------------------------------------------------------
_add(SkillData(
    name="Shadow Shroud",
    skill_type=SkillType.HEX,
    cast_time_ms=1000,
    recharge_ms=5000,
    energy_cost=10,
    is_primary_threat_hex=True,
    expected_duration_ms=10000,
))
_add(SkillData(
    name="Faintheartedness",
    skill_type=SkillType.HEX,
    cast_time_ms=1000,
    recharge_ms=8000,
    energy_cost=10,
    expected_duration_ms=10000,
))
_add(SkillData(
    name="Parasitic Bond",
    skill_type=SkillType.HEX,
    cast_time_ms=1000,
    recharge_ms=2000,
    energy_cost=5,
    expected_duration_ms=20000,
))
_add(SkillData(
    name="Suffering",
    skill_type=SkillType.HEX,
    cast_time_ms=2000,
    recharge_ms=10000,
    energy_cost=15,
    expected_duration_ms=12000,
))

# ---------------------------------------------------------------------------
# Elementalist — spike damage, disruption
# ---------------------------------------------------------------------------
_add(SkillData(
    name="Mind Burn",
    skill_type=SkillType.SPELL,
    cast_time_ms=2000,
    recharge_ms=15000,
    energy_cost=15,
))
_add(SkillData(
    name="Mind Blast",
    skill_type=SkillType.SPELL,
    cast_time_ms=1000,
    recharge_ms=2000,
    energy_cost=5,
    is_elite=True,
))
_add(SkillData(
    name="Gust",
    skill_type=SkillType.SPELL,
    cast_time_ms=1000,
    recharge_ms=15000,
    energy_cost=10,
    causes_knockdown=True,
))
_add(SkillData(
    name="Gale",
    skill_type=SkillType.SPELL,
    cast_time_ms=1000,
    recharge_ms=20000,
    energy_cost=10,
    causes_knockdown=True,
))
_add(SkillData(
    name="Blurred Vision",
    skill_type=SkillType.HEX,
    cast_time_ms=1000,
    recharge_ms=5000,
    energy_cost=10,
    expected_duration_ms=12000,
))
_add(SkillData(
    name="Meteor Shower",
    skill_type=SkillType.SPELL,
    cast_time_ms=5000,
    recharge_ms=60000,
    energy_cost=25,
    causes_knockdown=True,
))
_add(SkillData(
    name="Ward Against Foes",
    skill_type=SkillType.WARD,
    cast_time_ms=1000,
    recharge_ms=20000,
    energy_cost=10,
    expected_duration_ms=10000,
))

# ---------------------------------------------------------------------------
# Ranger — interrupts, disruption
# ---------------------------------------------------------------------------
_add(SkillData(
    name="Savage Shot",
    skill_type=SkillType.ATTACK,
    cast_time_ms=500,
    recharge_ms=5000,
    energy_cost=10,
))
_add(SkillData(
    name="Distracting Shot",
    skill_type=SkillType.ATTACK,
    cast_time_ms=500,
    recharge_ms=10000,
    energy_cost=5,
))
_add(SkillData(
    name="Magebane Shot",
    skill_type=SkillType.ATTACK,
    cast_time_ms=500,
    recharge_ms=10000,
    energy_cost=10,
    is_elite=True,
))
_add(SkillData(
    name="Splinter Weapon",
    skill_type=SkillType.WEAPON_SPELL,
    cast_time_ms=1000,
    recharge_ms=5000,
    energy_cost=10,
    expected_duration_ms=8000,
))

# ---------------------------------------------------------------------------
# Monk — defensive saves, hex removal, healing
# ---------------------------------------------------------------------------
_add(SkillData(
    name="Protective Spirit",
    skill_type=SkillType.ENCHANTMENT,
    cast_time_ms=250,
    recharge_ms=5000,
    energy_cost=10,
    is_defensive_save=True,
    expected_duration_ms=5000,
))
_add(SkillData(
    name="Spirit Bond",
    skill_type=SkillType.ENCHANTMENT,
    cast_time_ms=250,
    recharge_ms=5000,
    energy_cost=10,
    is_defensive_save=True,
    expected_duration_ms=8000,
))
_add(SkillData(
    name="Aegis",
    skill_type=SkillType.ENCHANTMENT,
    cast_time_ms=2000,
    recharge_ms=30000,
    energy_cost=15,
    is_elite=False,
    is_defensive_save=True,
    expected_duration_ms=5000,
))
_add(SkillData(
    name="Guardian",
    skill_type=SkillType.ENCHANTMENT,
    cast_time_ms=250,
    recharge_ms=5000,
    energy_cost=5,
    is_defensive_save=True,
    expected_duration_ms=5000,
))
_add(SkillData(
    name="Shield of Absorption",
    skill_type=SkillType.ENCHANTMENT,
    cast_time_ms=250,
    recharge_ms=8000,
    energy_cost=5,
    is_defensive_save=True,
    expected_duration_ms=5000,
))
_add(SkillData(
    name="Reversal of Fortune",
    skill_type=SkillType.SPELL,
    cast_time_ms=250,
    recharge_ms=2000,
    energy_cost=5,
    is_defensive_save=True,
))
_add(SkillData(
    name="Word of Healing",
    skill_type=SkillType.SPELL,
    cast_time_ms=750,
    recharge_ms=3000,
    energy_cost=5,
    is_elite=True,
    is_defensive_save=True,
))
_add(SkillData(
    name="Infuse Health",
    skill_type=SkillType.SPELL,
    cast_time_ms=250,
    recharge_ms=4000,
    energy_cost=10,
    is_defensive_save=True,
))
_add(SkillData(
    name="Smite Hex",
    skill_type=SkillType.SPELL,
    cast_time_ms=1000,
    recharge_ms=8000,
    energy_cost=10,
    is_hex_removal=True,
))
_add(SkillData(
    name="Cure Hex",
    skill_type=SkillType.SPELL,
    cast_time_ms=1000,
    recharge_ms=4000,
    energy_cost=5,
    is_hex_removal=True,
))
_add(SkillData(
    name="Divert Hexes",
    skill_type=SkillType.ENCHANTMENT,
    cast_time_ms=1000,
    recharge_ms=15000,
    energy_cost=10,
    is_elite=True,
    is_hex_removal=True,
))
_add(SkillData(
    name="Purge Signet",
    skill_type=SkillType.SIGNET,
    cast_time_ms=2000,
    recharge_ms=20000,
    energy_cost=0,
    is_hex_removal=True,
    is_condition_removal=True,
))
_add(SkillData(
    name="Restore Condition",
    skill_type=SkillType.SPELL,
    cast_time_ms=750,
    recharge_ms=3000,
    energy_cost=5,
    is_condition_removal=True,
))
_add(SkillData(
    name="Divine Healing",
    skill_type=SkillType.SPELL,
    cast_time_ms=1000,
    recharge_ms=5000,
    energy_cost=5,
))
_add(SkillData(
    name="Heal Area",
    skill_type=SkillType.SPELL,
    cast_time_ms=1000,
    recharge_ms=5000,
    energy_cost=10,
))

# ---------------------------------------------------------------------------
# Ritualist — weapon spells, spirits, defensive support
# ---------------------------------------------------------------------------
_add(SkillData(
    name="Weapon of Warding",
    skill_type=SkillType.WEAPON_SPELL,
    cast_time_ms=750,
    recharge_ms=3000,
    energy_cost=5,
    is_defensive_save=True,
    expected_duration_ms=8000,
))
_add(SkillData(
    name="Protective Was Kaolai",
    skill_type=SkillType.SPELL,
    cast_time_ms=750,
    recharge_ms=5000,
    energy_cost=10,
    is_defensive_save=True,
))
_add(SkillData(
    name="Wielder's Boon",
    skill_type=SkillType.SPELL,
    cast_time_ms=250,
    recharge_ms=3000,
    energy_cost=5,
    is_defensive_save=True,
))
_add(SkillData(
    name="Recovery",
    skill_type=SkillType.SPIRIT,
    cast_time_ms=3000,
    recharge_ms=30000,
    energy_cost=15,
    expected_duration_ms=30000,
))
_add(SkillData(
    name="Shelter",
    skill_type=SkillType.SPIRIT,
    cast_time_ms=3000,
    recharge_ms=30000,
    energy_cost=15,
    is_defensive_save=True,
    expected_duration_ms=30000,
))
_add(SkillData(
    name="Life",
    skill_type=SkillType.SPIRIT,
    cast_time_ms=3000,
    recharge_ms=30000,
    energy_cost=15,
    expected_duration_ms=30000,
))

# ---------------------------------------------------------------------------
# Assassin — spike chains
# ---------------------------------------------------------------------------
_add(SkillData(
    name="Horns of the Ox",
    skill_type=SkillType.ATTACK,
    cast_time_ms=0,
    recharge_ms=12000,
    energy_cost=5,
    causes_knockdown=True,
))
_add(SkillData(
    name="Falling Spider",
    skill_type=SkillType.ATTACK,
    cast_time_ms=0,
    recharge_ms=8000,
    energy_cost=5,
))
_add(SkillData(
    name="Twisting Fangs",
    skill_type=SkillType.ATTACK,
    cast_time_ms=0,
    recharge_ms=15000,
    energy_cost=10,
    causes_deep_wound=True,
))

# ---------------------------------------------------------------------------
# Ward Against Harm — referenced in spec for baiting
# ---------------------------------------------------------------------------
_add(SkillData(
    name="Ward Against Harm",
    skill_type=SkillType.WARD,
    cast_time_ms=1000,
    recharge_ms=20000,
    energy_cost=15,
    is_elite=True,
    is_defensive_save=True,
    expected_duration_ms=10000,
))
