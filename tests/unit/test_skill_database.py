from aegisspike.models.skill_database import SKILL_DB, lookup


class TestSkillDatabase:
    def test_lookup_by_name(self):
        skill = lookup("Eviscerate")
        assert skill is not None
        assert skill.name == "Eviscerate"
        assert skill.causes_deep_wound is True

    def test_lookup_case_insensitive(self):
        assert lookup("eviscerate") is not None
        assert lookup("EVISCERATE") is not None
        assert lookup("  Eviscerate  ") is not None

    def test_lookup_nonexistent(self):
        assert lookup("Totally Made Up Skill") is None

    def test_shadow_shroud_is_primary_threat(self):
        skill = lookup("Shadow Shroud")
        assert skill is not None
        assert skill.is_primary_threat_hex is True

    def test_smite_hex_is_hex_removal(self):
        skill = lookup("Smite Hex")
        assert skill is not None
        assert skill.is_hex_removal is True

    def test_cure_hex_is_hex_removal(self):
        skill = lookup("Cure Hex")
        assert skill is not None
        assert skill.is_hex_removal is True

    def test_protective_spirit_is_defensive_save(self):
        skill = lookup("Protective Spirit")
        assert skill is not None
        assert skill.is_defensive_save is True

    def test_spirit_bond_is_defensive_save(self):
        skill = lookup("Spirit Bond")
        assert skill is not None
        assert skill.is_defensive_save is True

    def test_shelter_is_spirit_with_long_cast(self):
        skill = lookup("Shelter")
        assert skill is not None
        assert skill.cast_time_ms == 3000
        assert skill.skill_type.value == "spirit"

    def test_purge_signet_removes_both(self):
        skill = lookup("Purge Signet")
        assert skill is not None
        assert skill.is_hex_removal is True
        assert skill.is_condition_removal is True
        assert skill.cast_time_ms == 2000

    def test_warriors_cause_deep_wound(self):
        for name in ["Eviscerate", "Dismember"]:
            skill = lookup(name)
            assert skill is not None
            assert skill.causes_deep_wound is True, f"{name} should cause deep wound"

    def test_knockdown_skills(self):
        for name in ["Bull's Strike", "Gust", "Gale", "Horns of the Ox"]:
            skill = lookup(name)
            assert skill is not None
            assert skill.causes_knockdown is True, f"{name} should cause knockdown"

    def test_database_has_minimum_skills(self):
        assert len(SKILL_DB) >= 40

    def test_all_skills_have_valid_types(self):
        for name, skill in SKILL_DB.items():
            assert skill.skill_type is not None, f"{name} missing skill_type"
            assert skill.cast_time_ms >= 0, f"{name} has negative cast time"
            assert skill.recharge_ms >= 0, f"{name} has negative recharge"
