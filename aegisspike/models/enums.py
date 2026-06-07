from enum import StrEnum


class EventType(StrEnum):
    DAMAGE = "damage"
    HEAL = "heal"
    SKILL_ACTIVATION = "skill_activation"
    SKILL_CANCEL = "skill_cancel"
    CONDITION_APPLIED = "condition_applied"
    CONDITION_REMOVED = "condition_removed"
    HEX_APPLIED = "hex_applied"
    HEX_REMOVED = "hex_removed"
    ENCHANTMENT_APPLIED = "enchantment_applied"
    ENCHANTMENT_REMOVED = "enchantment_removed"
    INTERRUPT = "interrupt"
    KNOCKDOWN = "knockdown"
    DEATH = "death"
    RESURRECTION = "resurrection"
    WEAPON_SWAP = "weapon_swap"
    ENERGY_CHANGE = "energy_change"


class WeaponSet(StrEnum):
    DEFENSIVE = "defensive"
    STAFF_40_40 = "40/40_staff"
    HIGH_ENERGY = "high_energy"
    MARTIAL = "martial"
    UNKNOWN = "unknown"


class Archetype(StrEnum):
    WARRIOR = "warrior"
    RANGER = "ranger"
    MESMER = "mesmer"
    ELEMENTALIST = "elementalist"
    MONK = "monk"
    RITUALIST = "ritualist"
    NECROMANCER = "necromancer"
    PARAGON = "paragon"
    DERVISH = "dervish"
    ASSASSIN = "assassin"
    UNKNOWN = "unknown"


class PlayerState(StrEnum):
    S0_NEUTRAL = "neutral"
    S1_VULNERABLE = "vulnerable"
    S2_SPIKE_ACTIVE = "spike_active"
    S3_MITIGATED = "mitigated"
    S4_DEAD = "dead"


class SkillType(StrEnum):
    ATTACK = "attack"
    SPELL = "spell"
    HEX = "hex"
    ENCHANTMENT = "enchantment"
    SHOUT = "shout"
    CHANT = "chant"
    SIGNET = "signet"
    SPIRIT = "spirit"
    STANCE = "stance"
    TRAP = "trap"
    WARD = "ward"
    WEAPON_SPELL = "weapon_spell"
    GLYPH = "glyph"
    PREPARATION = "preparation"
    ECHO = "echo"
    FORM = "form"
    PET_ATTACK = "pet_attack"


class SpikeOutcome(StrEnum):
    KILL = "kill"
    MITIGATED = "mitigated"
    IN_PROGRESS = "in_progress"


class Team(StrEnum):
    TEAM_A = "team_a"
    TEAM_B = "team_b"
