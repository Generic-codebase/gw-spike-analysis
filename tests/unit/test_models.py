from aegisspike.models import (
    Archetype,
    CombatEvent,
    DeathEvent,
    EventType,
    Player,
    PlayerRoster,
    PlayerState,
    SkillData,
    SkillType,
    SpikeEvent,
    WeaponSet,
)
from aegisspike.models.enums import SpikeOutcome, Team
from aegisspike.models.events import HexConditionState


class TestCombatEvent:
    def test_create_damage_event(self):
        evt = CombatEvent(
            timestamp_ms=5200,
            source="Axe Go Brrr",
            target="Monk Target",
            event_type=EventType.DAMAGE,
            skill="Eviscerate",
            value=132.0,
            weapon_set=WeaponSet.MARTIAL,
        )
        assert evt.timestamp_ms == 5200
        assert evt.timestamp_s == 5.2
        assert evt.source == "Axe Go Brrr"
        assert evt.event_type == EventType.DAMAGE
        assert evt.value == 132.0

    def test_defaults(self):
        evt = CombatEvent(
            timestamp_ms=0,
            source="A",
            target="B",
            event_type=EventType.DEATH,
        )
        assert evt.skill == ""
        assert evt.value == 0.0
        assert evt.weapon_set == WeaponSet.UNKNOWN

    def test_serialization_roundtrip(self):
        evt = CombatEvent(
            timestamp_ms=1000,
            source="A",
            target="B",
            event_type=EventType.HEAL,
            skill="Word of Healing",
            value=185.0,
        )
        data = evt.model_dump()
        restored = CombatEvent.model_validate(data)
        assert restored == evt


class TestHexConditionState:
    def test_active_hex(self):
        state = HexConditionState(
            skill="Shadow Shroud",
            source="Necro",
            target="Monk",
            applied_ms=1000,
            expected_duration_ms=10000,
        )
        assert state.is_active is True
        assert state.end_influence_ms == 11000

    def test_removed_hex(self):
        state = HexConditionState(
            skill="Shadow Shroud",
            source="Necro",
            target="Monk",
            applied_ms=1000,
            expected_duration_ms=10000,
            removed_ms=5000,
        )
        assert state.is_active is False
        assert state.end_influence_ms == 5000

    def test_effective_decay_distance_hex_persists_through_spike(self):
        state = HexConditionState(
            skill="Shadow Shroud",
            source="Necro",
            target="Monk",
            applied_ms=1000,
            expected_duration_ms=10000,
        )
        t_spike_start = 5000
        t_eff = max(0, t_spike_start - state.end_influence_ms)
        assert t_eff == 0  # hex still active at spike, full credit

    def test_effective_decay_distance_hex_expired_before_spike(self):
        state = HexConditionState(
            skill="Shadow Shroud",
            source="Necro",
            target="Monk",
            applied_ms=1000,
            expected_duration_ms=3000,
            removed_ms=4000,
        )
        t_spike_start = 8000
        t_eff = max(0, t_spike_start - state.end_influence_ms)
        assert t_eff == 4000  # 4s gap, significant decay


class TestSpikeEvent:
    def test_kill_spike(self):
        spike = SpikeEvent(
            spike_id=1,
            target="Monk Target",
            t_start_ms=5000,
            t_end_ms=6100,
            outcome=SpikeOutcome.KILL,
            peak_damage=559.0,
            participants=["Axe Go Brrr", "Fire Caller", "Arrow Rain"],
        )
        assert spike.duration_ms == 1100
        assert spike.outcome == SpikeOutcome.KILL

    def test_in_progress_spike_has_no_duration(self):
        spike = SpikeEvent(
            spike_id=2,
            target="Prot Monk",
            t_start_ms=12000,
        )
        assert spike.duration_ms is None
        assert spike.outcome == SpikeOutcome.IN_PROGRESS


class TestDeathEvent:
    def test_create(self):
        death = DeathEvent(
            timestamp_ms=6100,
            target="Monk Target",
            killer="Axe Go Brrr",
        )
        assert death.target == "Monk Target"


class TestPlayer:
    def test_defaults(self):
        p = Player(name="Axe Go Brrr", team=Team.TEAM_A)
        assert p.archetype == Archetype.UNKNOWN
        assert p.current_state == PlayerState.S0_NEUTRAL
        assert p.current_weapon_set == WeaponSet.UNKNOWN

    def test_with_archetype(self):
        p = Player(
            name="Healing Monk",
            team=Team.TEAM_A,
            archetype=Archetype.MONK,
            max_hp=480,
            max_energy=45,
        )
        assert p.archetype == Archetype.MONK


class TestPlayerRoster:
    def test_get_player(self):
        roster = PlayerRoster(players=[
            Player(name="Axe Go Brrr", team=Team.TEAM_A, archetype=Archetype.WARRIOR),
            Player(name="Healing Monk", team=Team.TEAM_A, archetype=Archetype.MONK),
            Player(name="Enemy War", team=Team.TEAM_B, archetype=Archetype.WARRIOR),
        ])
        assert roster.get_player("Axe Go Brrr") is not None
        assert roster.get_player("Axe Go Brrr").archetype == Archetype.WARRIOR  # type: ignore[union-attr]
        assert roster.get_player("Nonexistent") is None

    def test_team_filtering(self):
        roster = PlayerRoster(players=[
            Player(name="P1", team=Team.TEAM_A),
            Player(name="P2", team=Team.TEAM_A),
            Player(name="P3", team=Team.TEAM_B),
        ])
        assert len(roster.team_a) == 2
        assert len(roster.team_b) == 1


class TestSkillData:
    def test_defensive_save(self):
        skill = SkillData(
            name="Protective Spirit",
            skill_type=SkillType.ENCHANTMENT,
            cast_time_ms=250,
            recharge_ms=5000,
            energy_cost=10,
            is_defensive_save=True,
        )
        assert skill.is_defensive_save is True
        assert skill.is_hex_removal is False

    def test_primary_threat_hex(self):
        skill = SkillData(
            name="Shadow Shroud",
            skill_type=SkillType.HEX,
            cast_time_ms=1000,
            recharge_ms=5000,
            energy_cost=10,
            is_primary_threat_hex=True,
            expected_duration_ms=10000,
        )
        assert skill.is_primary_threat_hex is True


class TestEnums:
    def test_event_type_values(self):
        assert EventType.DAMAGE.value == "damage"
        assert EventType.INTERRUPT.value == "interrupt"

    def test_weapon_set_values(self):
        assert WeaponSet.STAFF_40_40.value == "40/40_staff"
        assert WeaponSet.DEFENSIVE.value == "defensive"

    def test_player_state_dtmc(self):
        assert PlayerState.S0_NEUTRAL.value == "neutral"
        assert PlayerState.S4_DEAD.value == "dead"

    def test_archetype_coverage(self):
        archetypes = [a.value for a in Archetype]
        assert "warrior" in archetypes
        assert "mesmer" in archetypes
        assert "monk" in archetypes
        assert "ritualist" in archetypes
        assert "paragon" in archetypes
