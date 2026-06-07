# GW1 Combat Log Format Specification

## Source

The primary data source for AegisSpike is the **GWToolbox++ Combat Log** module,
which hooks into the Guild Wars 1 client via GWCA and writes structured combat
events to disk.

This document defines the expected input format. The parser must handle minor
variations (extra whitespace, missing fields, alternate timestamp formats)
gracefully.

---

## Line Format

Each line in the combat log represents a single event:

```
<timestamp>|<source>|<target>|<event_type>|<skill>|<value>
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | Integer | Milliseconds since match start (0 = first event) |
| `source` | String | Character name of the acting player |
| `target` | String | Character name of the affected player (may equal source) |
| `event_type` | Enum | One of the event type codes below |
| `skill` | String | Skill name, or empty for auto-attacks / system events |
| `value` | Float | Numeric payload (damage dealt, HP healed, energy cost, duration in ms) |

### Event Type Codes

| Code | Meaning | `value` interpretation |
|------|---------|----------------------|
| `DMG` | Direct damage dealt | Damage amount (pre-mitigation raw) |
| `HEA` | Healing received | HP healed |
| `SKA` | Skill activation started | Energy cost |
| `SKC` | Skill activation cancelled | 0 |
| `CNA` | Condition applied | Expected duration (ms) |
| `CNR` | Condition removed | 0 |
| `HXA` | Hex applied | Expected duration (ms) |
| `HXR` | Hex removed | 0 |
| `ENA` | Enchantment applied | Expected duration (ms) |
| `ENR` | Enchantment removed | 0 |
| `INT` | Interrupt landed | 0 |
| `KND` | Knockdown applied | Duration (ms) |
| `DEA` | Player death | 0 |
| `RES` | Player resurrected | HP after resurrection |
| `WSW` | Weapon swap | 0 |
| `NRG` | Energy change | Energy delta (negative = spent) |

---

## Example Log Lines

```
0|System|System|SKA||0
125|Axe Go Brrr|Monk Target|DMG|Eviscerate|132
125|Axe Go Brrr|Monk Target|CNA|Deep Wound|15000
250|Fire Caller|Monk Target|DMG|Mind Burn|98
300|Vortex X|Healing Monk|INT|Power Drain|0
375|Shadow Necro|Monk Target|HXA|Shadow Shroud|10000
400|Shadow Necro|Monk Target|HXA|Parasitic Bond|20000
500|Arrow Rain|Monk Target|DMG|Savage Shot|45
625|Axe Go Brrr|Axe Go Brrr|WSW||0
750|Healing Monk|Monk Target|HEA|Word of Healing|185
800|Healing Monk|Healing Monk|NRG|Word of Healing|-5
1250|Monk Target|Monk Target|DEA||0
```

---

## Weapon Swap Detection

Weapon swaps (`WSW`) appear as source == target events with no skill name.
The parser tracks the current weapon set per player based on subsequent
skill usage patterns:

- If next skill activation is a martial attack -> `MARTIAL`
- If next skill activation is a caster spell and prior set was martial -> infer `40/40_STAFF` or `DEFENSIVE` based on skill type
- Explicit weapon-set tagging requires GWToolbox++ Custom Plugin (Phase 0.1 extension)

Initial implementation: default to `UNKNOWN` and update via heuristic
inference from skill sequences.

---

## Team Detection

The log does not explicitly tag teams. Team membership is inferred by:

1. **Damage polarity:** Players who damage each other are on opposing teams.
2. **Heal polarity:** Players who heal each other are on the same team.
3. **First contact heuristic:** Build a graph from the first 100 events;
   partition into two sets via connected-component analysis on heal edges.

---

## Known Limitations

1. **Timestamp resolution:** GW1 runs on ~250ms server ticks. Sub-tick
   ordering of simultaneous events is not guaranteed.
2. **Energy tracking:** Not all energy changes are logged by default
   Toolbox configs. EBM calculations may need to estimate from known
   skill costs.
3. **Weapon set data:** Toolbox does not natively export weapon set names.
   Must be inferred (see above) or captured with a custom GWCA plugin.
4. **Pet damage:** Pet attacks may appear with the pet's name as source
   rather than the ranger's name. Requires pet-owner mapping.
5. **AoE events:** Area skills (Meteor Shower, Splinter Weapon procs)
   generate one line per target hit. No explicit "AoE" flag.
