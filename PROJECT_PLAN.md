# AegisSpike Project Plan

## GW1 GvG Spike Performance Analysis & Attribution Engine

---

## Overview

AegisSpike parses Guild Wars 1 combat text logs and produces a multi-dimensional analysis of spike performance in Guild versus Guild (GvG) PvP matches. Rather than relying on shallow aggregate DPS/HPS metrics, it attributes tactical credit across the full spike lifecycle: setup, execution, disruption, mitigation, and macro-attrition.

This plan breaks the scoping document into implementable phases with concrete deliverables.

---

## Phase 0 — Foundations & Log Format Research

**Goal:** Establish the project skeleton, understand the raw input data, and define internal data structures.

### Tasks

| # | Task | Description |
|---|------|-------------|
| 0.1 | **GW1 combat log format analysis** | Collect sample combat log files (`.txt` / `.log`) from GvG matches. Document the line format, timestamp resolution, event types (damage, skill activation, death, condition applied/removed, hex applied/removed, weapon swap, interrupt, knockdown, heal, enchantment). |
| 0.2 | **Project scaffolding** | Initialize Python project with `pyproject.toml`. Set up directory layout: `aegisspike/parser/`, `aegisspike/engine/`, `aegisspike/models/`, `aegisspike/api/`, `frontend/`. Add linting (ruff), formatting (black), and type-checking (mypy). |
| 0.3 | **Core data models (Pydantic v2)** | Define the canonical event tuple: `(t, Player, Target, EventType, Skill, Value, WeaponSet)`. Define enums for `EventType`, `WeaponSet ∈ {Defensive, 40/40 Staff, High-Energy, Martial}`, `PlayerState`, `Archetype`. |
| 0.4 | **GW1 skill database seed** | Build a reference table of GvG-relevant skills with metadata: cast time, recharge, energy cost, skill type (hex, enchantment, attack, shout, signet, spirit), and known interactions (e.g. Shadow Shroud = primary threat hex, Smite Hex / Cure Hex = hex removal). |
| 0.5 | **Test harness** | Create pytest scaffold with synthetic log fixtures representing known spike scenarios (clean kill, mitigated save, overkill, cover-hex interaction, interrupt during cast). |

### Deliverables
- Documented log format specification
- Running project with `pytest` green on stub tests
- Pydantic models importable from `aegisspike.models`

---

## Phase 1 — Log Parser

**Goal:** Turn raw combat log text into a stream of typed, timestamped `CombatEvent` objects.

### Tasks

| # | Task | Description |
|---|------|-------------|
| 1.1 | **Line tokenizer** | Regex-based parser that extracts timestamp (ms resolution), source player, target player, skill name, event type, and numeric value from each log line. |
| 1.2 | **Weapon set inference** | Track weapon-swap events per player. Tag every subsequent combat event with the player's current `WeaponSet` until the next swap. |
| 1.3 | **Player roster builder** | From the first N lines, identify all 16 players (8v8) and assign team membership and archetype (Warrior, Ranger, Mesmer, Elementalist, Monk, Ritualist, Necromancer, Paragon, Dervish, Assassin) based on skill usage patterns. |
| 1.4 | **Hex/condition stack tracker** | Maintain a per-player ordered stack of active hexes and conditions with application time and expected duration. Track removal events (cleanse, expiry). |
| 1.5 | **Stream output** | Emit a `list[CombatEvent]` sorted by timestamp, with full dimensional tagging. |

### Deliverables
- `aegisspike.parser.parse_log(file) -> list[CombatEvent]`
- Unit tests against synthetic and real log files

---

## Phase 2 — Spike Detection Engine

**Goal:** Implement the sliding-window spike detector and outcome classifier (Sections 2.1, 2.5 of the spec).

### Tasks

| # | Task | Description |
|---|------|-------------|
| 2.1 | **5,000ms sliding event buffer** | Per-player rolling window. Accumulate `D_T(t)` (cumulative raw damage) over `[t - 5s, t]`. |
| 2.2 | **Spike activation trigger** | Fire a `SpikeEvent` when `D_T(t) >= 500 HP` within the window. Record `t_start`. |
| 2.3 | **Outcome classification** | **Kill:** target transitions to Dead within `[t_start, t_start + 10s]`. **Mitigated:** target survives beyond `t_start + 10s` and damage drops below threshold. |
| 2.4 | **DTMC state machine** | Implement the 5-state model: `S0 (Neutral) → S1 (Vulnerable) → S2 (Spike Active) → S3 (Mitigated) | S4 (Dead)`. Track transitions per player. Build the transition probability matrix `P` over match history. |
| 2.5 | **Lethality Delta calculator** | Compute `ΔP_death = P(S4 | S2 ∩ Disruption X) - P(S4 | S2 ∩ No Disruption)` for each disruption type to quantify their tactical value. |

### Deliverables
- `aegisspike.engine.spike_detector.detect_spikes(events) -> list[SpikeEvent]`
- Each `SpikeEvent` contains: target, t_start, outcome, participants, state transitions

---

## Phase 3 — Attribution & Scoring Models

**Goal:** Implement the credit-assignment mathematics (Sections 2.2, 2.3, 2.4 of the spec).

### Tasks

| # | Task | Description |
|---|------|-------------|
| 3.1 | **Piecewise Quadratic Decay W(t)** | `W(t) = 1.0` if `0 ≤ t ≤ 5`; `W(t) = (1 - (t-5)/5)^2` if `5 < t ≤ 10`; `W(t) = 0` if `t > 10`. Apply to all actions within a spike window relative to `t_death`. |
| 3.2 | **State-persistence decay (t_eff)** | For hexes/conditions: `t_eff = max(0, t_spike_start - t_end_influence)`. If hex persists into spike window, `t_eff = 0` → full credit. Solves the "T-7s hex dilemma". |
| 3.3 | **Effective Damage (eDMG)** | When target HP < sum of simultaneous attacks, distribute remaining HP proportionally: `eDMG_i = H_rem × (d_i / Σd_j)`. Prevents overkill inflation. |
| 3.4 | **Total Performance Score (TPS)** | Aggregate per-player: `TPS = Σ(eDMG_i × W(t_i)) + interrupt_points + VDP + exhaustion_credits + strategic_baiting_credits`. |

### Deliverables
- `aegisspike.engine.attribution.score_spike(spike, events) -> list[PlayerContribution]`
- Unit tests validating decay curves, eDMG edge cases, hex persistence credit

---

## Phase 4 — GvG Heuristic Analytics

**Goal:** Implement the GvG-specific tactical metrics (Sections 3.1–3.4, 5.1–5.3 of the spec).

### Tasks

| # | Task | Description |
|---|------|-------------|
| 4.1 | **Dynamic interrupt credits** | `Interrupt Points = Base Score × ΔP_death × C_mult`. Clutch factor: `C_mult = 1.0` (HP ≥ 75%), `1.5` (25–75%), `2.5` (≤ 25%). |
| 4.2 | **Cover-hex attribution (VDP)** | Monitor hex stack during spikes. When enemy Monk's hex removal clears cover hex instead of primary threat, award Virtual Damage Prevented to the cover hex caster. |
| 4.3 | **Locked-state vulnerability** | Flag `S_locked` when support class begins a cast with `T_cast ≥ 1.5s`. If ally dies during lock, log Spatially Blocked Defensive Window and calculate opportunity cost. |
| 4.4 | **Locked-state exploitation** | When an `S_locked` cast is interrupted, apply 2.5x Locked-State Multiplier to interrupt score. Credit interrupter with denying the full spell payoff. |
| 4.5 | **Weapon-set lethality delta** | Compute `ΔP_40/40 = P(S4 | S2 ∩ Caller_weapon=40/40) - P(S4 | S2 ∩ Caller_weapon=Defensive)` to quantify tell/fake/timing quality. |
| 4.6 | **Energy Burn Metric (EBM)** | Track energy spent by defenders vs attackers in each spike+stabilization window. Compute Resource Burn Coefficient `Φ = E_def / E_att`. Award Energy Tax Points when `Φ ≥ 2.0`. |
| 4.7 | **Countermeasure Baiting Index** | Track defensive cooldown usage forced by spikes. When follow-up spike occurs within the "Vulnerable Utility Window", apply multiplier. |
| 4.8 | **Over-Heal Overhead (OHO)** | `OHO = Total Group-Healing / Target-Specific Damage Prevented`. Award Collateral Strategic Impact bonus when `OHO > 1.5`. |

### Deliverables
- Modular heuristic calculators under `aegisspike.engine.heuristics/`
- Integration tests using multi-spike match scenarios

---

## Phase 5 — Macro-Pressure & Attrition Sequences

**Goal:** Implement the attrition chain, spike cadence, and cumulative pressure models (Section 4 of the spec).

### Tasks

| # | Task | Description |
|---|------|-------------|
| 5.1 | **Markovian attrition chain** | Track consecutive spikes on the same target within a 120s window. Model kill probability as: `P(S4 | S2^(n)) = P(S4 | S2^(1)) + (1 - P(S4 | S2^(1))) × (1 - e^(-λ(n-1)))`. Award Exhaustion Credit `χ` to failed-spike callers. |
| 5.2 | **Spike cadence (κ)** | `κ = t_spike_n - t_spike_{n-1}`. If `κ ≤ 10s` (Desynchronized Window), apply 1.5x Strategic Synergy Multiplier. If `κ > 12s`, reset to baseline. |
| 5.3 | **Cumulative Pressure Index (CPI)** | Rolling 60s integral of weighted damage + hex degeneration + condition severity. Flag High Background Pressure when `CPI > 350 HP/s` sustained over 60s. |

### Deliverables
- `aegisspike.engine.attrition` module
- Validated against synthetic multi-spike sequences

---

## Phase 6 — Match Aggregation & MVP

**Goal:** Roll up per-spike scores into match-level player rankings, team comparisons, and MVP selection.

### Tasks

| # | Task | Description |
|---|------|-------------|
| 6.1 | **Player leaderboard** | Aggregate TPS across all spikes for each player. Break down by category: eDMG contribution, interrupt value, VDP, exhaustion credits, strategic baiting. |
| 6.2 | **Team spider chart dimensions** | Compute 5-axis team profile: Spike Execution, Defensive Saves, Disruption, Pressure/Attrition, Coordination. Normalize to 0–100. |
| 6.3 | **MVP algorithm** | Select highest TPS player. Include archetype-specific context (e.g. "Interrupts: 14, Lifelines Denied: 4" for Mesmers). |
| 6.4 | **Match metadata** | Duration, total spikes detected, successful vs mitigated counts, Markov transition summary. |

### Deliverables
- `aegisspike.engine.aggregator.analyze_match(events) -> MatchAnalysis`
- Full response JSON matching the API schema from Section 7.2

---

## Phase 7 — Backend API (FastAPI)

**Goal:** Expose the analysis engine through a stateless HTTP API (Section 6–7 of the spec).

### Tasks

| # | Task | Description |
|---|------|-------------|
| 7.1 | **FastAPI application** | Single route: `POST /api/v1/analyze-log`. Accepts `multipart/form-data` with combat log file (`.txt` or `.log`). |
| 7.2 | **Pydantic response schema** | Define `MatchAnalysisResponse` matching the JSON contract in Section 7.2: `match_metadata`, `mvp`, `player_leaderboard`, `charts`, `markov_chains`. |
| 7.3 | **Error handling** | Validate file type, size limits, malformed log detection. Return structured error responses. |
| 7.4 | **OpenAPI docs** | Auto-generated Swagger UI via FastAPI for API consumers. |

### Deliverables
- Running FastAPI server with `/api/v1/analyze-log` endpoint
- Swagger docs at `/docs`

---

## Phase 8 — Frontend Dashboard

**Goal:** Build the client portal for log upload and interactive visualization (Section 6 of the spec).

### Tasks

| # | Task | Description |
|---|------|-------------|
| 8.1 | **Drag-and-drop upload** | File drop zone accepting `.txt` / `.log` files. Sends `multipart/form-data` POST to backend. Shows upload progress. |
| 8.2 | **Match overview panel** | Display match metadata: duration, spike counts (successful/mitigated), kill timeline. |
| 8.3 | **Player leaderboard table** | Sortable table with TPS, archetype, contribution breakdown. Highlight MVP row. |
| 8.4 | **Damage attribution charts** | Chart.js pie/bar charts: Dimension A (player damage distribution), Dimension B (skill damage distribution). |
| 8.5 | **Team spider/radar chart** | Overlay radar chart comparing Team A vs Team B across 5 axes. |
| 8.6 | **Spike timeline view** | Horizontal timeline of all spike events. Click to expand individual spike detail: participants, eDMG, decay weights, outcome. |
| 8.7 | **Markov transition display** | Visualization of state transition probabilities. Sankey or flow diagram of S0→S1→S2→S3/S4 paths. |

### Deliverables
- Single-page application (Tailwind CSS + vanilla JS or React + Chart.js)
- Responsive layout, functional with the backend API

---

## Phase 9 — Optimization & Production Hardening

**Goal:** Handle large logs, add caching, and prepare for deployment (Section 8 of the spec).

### Tasks

| # | Task | Description |
|---|------|-------------|
| 9.1 | **Redis caching** | Cache processed JSON payloads by log file hash. Return cached results on re-upload. |
| 9.2 | **Streaming parser** | Process log files line-by-line to handle 20MB+ files without loading entirely into memory. |
| 9.3 | **Web Worker delegation** | If client-side parsing is pursued, offload parsing to a Web Worker to keep UI responsive. |
| 9.4 | **WASM compilation (stretch)** | Compile core parsing algorithms to WebAssembly (Rust) for near-native browser performance. |
| 9.5 | **Deployment config** | Dockerize backend. Add CORS configuration. Production ASGI server (uvicorn/gunicorn). |

### Deliverables
- Sub-5s analysis time for typical 30-min match logs
- Docker Compose stack for one-command deployment

---

## Dependency Graph

```
Phase 0 (Foundations)
  │
  ▼
Phase 1 (Parser)
  │
  ▼
Phase 2 (Spike Detection) ──────────────────────┐
  │                                               │
  ▼                                               ▼
Phase 3 (Attribution)              Phase 5 (Macro-Pressure/Attrition)
  │                                               │
  ▼                                               │
Phase 4 (GvG Heuristics) ◄───────────────────────┘
  │
  ▼
Phase 6 (Aggregation & MVP)
  │
  ├──────────────────┐
  ▼                  ▼
Phase 7 (API)    Phase 8 (Frontend)
  │                  │
  └──────┬───────────┘
         ▼
Phase 9 (Optimization)
```

---

## Key Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Language | Python | Matches the analytical core, FastAPI ecosystem, rapid iteration |
| API Framework | FastAPI | Async, auto-docs, native Pydantic integration |
| Data Validation | Pydantic v2 | Spec requirement, fast serialization |
| Frontend | Tailwind + Chart.js | Lightweight, no build toolchain required for MVP |
| State Model | DTMC (5-state) | Captures tactical flow without over-fitting |
| Decay Model | Piecewise quadratic | Balances credit between setup and execution roles |

---

## Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| GW1 combat log format is inconsistent or undocumented | Blocks Phase 1 | Collect diverse sample logs early; build flexible regex patterns with fallback heuristics |
| Overkill eDMG edge cases with simultaneous attacks at identical timestamps | Incorrect attribution | Comprehensive unit tests with known-answer scenarios |
| Hex stack ordering ambiguity in logs | Cover-hex VDP miscalculation | Cross-reference with GW1 wiki hex mechanics; allow manual correction |
| Large log files (20MB+) cause timeout | Poor UX | Streaming parser + Redis caching (Phase 9) |
| Weapon set inference from logs may be unreliable | Noisy weapon dimension | Fallback to "Unknown" set; allow user annotation |

---

## Success Criteria

1. **Spike detection accuracy:** ≥95% of manually-identified spikes in test logs are detected, with correct kill/mitigate classification
2. **Attribution fairness:** Setup players (Mesmers landing Shadow Shroud at T-7s) receive meaningful credit, not just Warriors landing the final hit
3. **eDMG correctness:** No overkill inflation — total eDMG across all players in a spike equals the target's HP at spike start (for kills)
4. **Sub-5s analysis** for a typical 30-minute match log
5. **Functional dashboard** where a user can drag-drop a log and see the full analysis within 10 seconds
