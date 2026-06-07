# AegisSpike Taxonomy & GW1 PvP Terminology Reference

This document serves as the canonical reference for all terminology used by
the AegisSpike analysis engine. It covers Guild Wars 1 game mechanics, PvP
tactical concepts, and AegisSpike-specific analytical terms. The engine uses
this taxonomy to classify events, attribute credit, and generate human-readable
explanations in the dashboard.

---

## 1. Skill Effect Types

Guild Wars 1 skills produce effects that fall into distinct mechanical
categories. Understanding these categories is essential because each has
different rules for stacking, removal, and mutual exclusivity.

### 1.1 Hexes

Negative effects applied to enemies. A target can have multiple hexes active
simultaneously. Hexes are ordered in a **LIFO (Last In, First Out) stack** —
the most recently applied hex sits on top and is removed first by single-target
hex removal skills.

- **Application:** Cast by the attacker onto the target. Has a cast time and
  can be interrupted.
- **Removal:** Hex removal skills (Remove Hex, Cure Hex, Smite Hex) strip the
  top hex. Multi-hex removal (Divert Hexes, Expel Hexes) removes from the top
  downward. Holy Veil, when dropped, removes one hex.
- **Expiry:** Each hex has a defined duration. When the duration ends, the hex
  is removed from the stack regardless of position.
- **AegisSpike relevance:** The LIFO ordering is the foundation of cover-hex
  mechanics (Section 9.2). The engine tracks the full hex stack per player to
  determine whether hex removal hit a cover or the primary threat.

### 1.2 Enchantments

Positive effects applied to allies or self. Like hexes, enchantments stack in
**LIFO order** — the most recently applied enchantment is removed first by
enchantment removal skills.

- **Application:** Cast on self or ally. Has a cast time and can be interrupted.
- **Removal by enemies:** Enchantment removal skills (Rip Enchantment, Strip
  Enchantment, Rend Enchantments) strip from the top. Inspired Enchantment
  steals the top enchantment.
- **Cover enchantment:** A cheap enchantment applied after a critical one
  (e.g., Protective Spirit) to shield it from single-target removal.
- **AegisSpike relevance:** Defensive enchantments (Protective Spirit, Spirit
  Bond, Aegis) are the primary mechanism for spike mitigation. The engine
  tracks their application and removal to score defensive plays.

### 1.3 Conditions

Binary status effects. A target either has a condition or does not — the same
condition cannot stack in intensity. Reapplying a condition that is already
active refreshes its duration. Multiple *different* conditions can coexist on
one target simultaneously with no limit.

Unlike hexes and enchantments, conditions have **no defined stack order** for
removal purposes. Condition removal skills either remove a specific named
condition or remove one/all conditions without an ordering requirement.

| Condition | Effect | AegisSpike Classification |
|-----------|--------|--------------------------|
| **Deep Wound** | -20% max HP (capped at -100 HP). Reduces current HP proportionally. | Setup condition — triggers S1 (Vulnerable) |
| **Daze** | Spells take 2x cast time. Any hit interrupts spells. | Setup condition — triggers S1 (Vulnerable) |
| **Blind** | 90% miss chance on attacks (not spells). | Shutdown condition |
| **Crippled** | -50% movement speed. | Positional condition |
| **Weakness** | All attributes -1. Attack damage reduced to 66%. | Pressure condition |
| **Burning** | -7 health degeneration pips (-14 HP/sec). | Pressure/damage condition |
| **Poison** | -4 health degeneration pips (-8 HP/sec). | Pressure condition |
| **Bleeding** | -3 health degeneration pips (-6 HP/sec). | Pressure condition |
| **Disease** | -4 health degeneration pips (-8 HP/sec). Spreads to adjacent allies. | Pressure condition |
| **Cracked Armor** | -20 armor rating (minimum floor of 60 AR). | Setup condition |

Health degeneration from multiple conditions stacks additively, but total
degeneration is capped at **-10 pips** (-20 HP/sec).

### 1.4 Stances

Self-buffs that activate instantly (no cast time, no aftercast). **Only one
stance can be active at a time** — activating a new stance immediately replaces
the current one. Cannot be removed by hex or enchantment removal. Ended only by
specific anti-stance skills (Wild Blow, Wild Throw) or by duration expiry.

Examples: Frenzy (+33% attack speed, double damage taken), Rush (speed boost),
Flail (+33% attack speed, -33% movement speed).

### 1.5 Shouts and Chants

**Shouts** activate instantly with no cast time and no aftercast. Cannot be
interrupted. Affect the user and/or nearby allies. Multiple shouts of different
types can be active simultaneously.

**Chants** (Paragon-specific) have a cast time and provide effects to allies in
earshot. Ended effects can trigger bonus effects ("finale" skills).

### 1.6 Weapon Spells

Ritualist-specific buffs applied to an ally. **Only one weapon spell can be
active on a character at a time** — applying a new one replaces the old.
Critically, weapon spells **cannot be removed by enemies** — they can only be
replaced by another weapon spell or expire naturally. This makes them the most
resilient form of defensive buff.

Examples: Weapon of Warding (damage reduction), Wielder's Boon (healing on
attack), Weapon of Shadow (shadow stepping).

### 1.7 Spirits

Summoned creatures placed at a fixed location that provide passive area effects.
Spirits have their own health pool and can be targeted and killed.

- **Binding Rituals** (Ritualist): Create spirits affecting allies/enemies
  within their range. Examples: Shelter (absorbs damage for nearby allies),
  Union (takes damage instead of allies), Recovery (health regeneration).
- **Nature Rituals** (Ranger): Create spirits with **global effects** affecting
  all creatures on the map (both teams). Examples: Fertile Season, Frozen Soil
  (disables resurrections).

Spirits typically have long cast times (3+ seconds), making the caster
vulnerable during placement. The AegisSpike engine tracks this as a
Locked Vulnerability State.

### 1.8 Other Skill Types

| Type | Exclusivity | Key Properties |
|------|-------------|----------------|
| **Signet** | No limit | Zero energy cost. Typically longer cast/recharge. Not a spell (immune to spell-targeting counters, vulnerable to signet-targeting counters). |
| **Glyph** | One at a time | Modifies the next spell(s) cast. Elementalist/Monk. |
| **Preparation** | One at a time | Enhances attacks for a duration. Ranger-specific. |
| **Ward** | Multiple allowed | Area effect at caster's location. Duration-limited. |
| **Well** | Multiple allowed | Area effect centered on a corpse. Necromancer-specific. |
| **Trap** | Multiple allowed | Placed at caster's location, triggered by enemy proximity. Ranger-specific. |
| **Form** | One at a time | Transforms the character. Typically elite. Dervish avatars. |
| **Echo** | Varies | Paragon-specific. Duration-limited effect on a single ally. |

---

## 2. Combat Mechanics

### 2.1 Damage Formula

All non-armor-ignoring damage is calculated as:

```
Damage = Base_Damage × 2^((60 - Effective_AR) / 40)
```

- **60 AR** is the baseline — at 60 armor, you take exactly the listed damage.
- Every **+40 AR** above 60 halves damage taken.
- Every **-40 AR** below 60 doubles damage taken.
- **Armor penetration** reduces the target's AR before the formula:
  `Effective_AR = Base_AR × (1 - Penetration%) + AR_modifiers`

### 2.2 Armor-Ignoring Damage

Several damage sources bypass the armor formula entirely:

- **Bonus damage from attack skills** (the "+XX damage" component on warrior,
  ranger, and assassin skills). The base weapon damage uses armor; the bonus
  is armor-ignoring.
- Most **Mesmer and Necromancer** damage skills (Domination, Illusion, Curses,
  Blood Magic).
- **Life stealing** (Blood Magic) — ignores armor and is not classified as
  "damage" at all (bypasses Protective Spirit, damage reduction, etc.).
- **Holy damage** and **shadow damage** — typically armor-ignoring.

### 2.3 Damage Types

| Category | Types | Resisted By |
|----------|-------|-------------|
| **Physical** | Slashing (sword/axe), Blunt (hammer), Piercing (bow/spear/dagger) | Armor, shields, physical damage reduction skills |
| **Elemental** | Fire, Cold, Earth, Lightning | Armor, elemental resistance skills, Ranger +30 vs elemental |
| **Non-standard** | Chaos, Dark, Holy, Shadow | Chaos uses normal armor; Dark/Holy/Shadow typically armor-ignoring |

### 2.4 Critical Hits

A critical hit **ignores 20 points of the target's armor** and deals the
**maximum value** in the weapon's damage range (no randomness).

- Base critical chance scales with weapon mastery attribute (~1.44% per rank,
  ~15% at rank 12).
- Assassin's Critical Strikes attribute adds +1% per rank and grants energy
  on critical hits.
- **Flanking:** Hitting a moving foe from behind with melee always results in
  a critical hit.

### 2.5 Health Pools

All professions share the same base health: **480 HP at level 20**.

Professions differ in **armor rating**, not base health:

| Profession | Base AR | Special | Typical GvG HP |
|------------|---------|---------|----------------|
| Warrior | 80 | +20 vs physical | 535–600 |
| Paragon | 80 | — | 535–600 |
| Ranger | 70 | +30 vs elemental | 535–570 |
| Assassin | 70 | — | 535–570 |
| Dervish | 70 | +25 HP from armor | 560–595 |
| Monk | 60 | — | 495–535 |
| Mesmer | 60 | — | 495–535 |
| Elementalist | 60 | — | 495–535 |
| Necromancer | 60 | — | 495–535 |
| Ritualist | 60 | — | 495–535 |

**Typical GvG caster HP (Survivor armor):**
480 (base) + 50 (Superior Vigor) + 40 (full Survivor insignia) + 40 (4× Vitae
runes) − 75 (1 Superior attribute rune) = **535 HP**

**Typical GvG caster HP (Radiant armor):**
480 + 50 − 75 + 40 (4× Vitae) = **495 HP** (but +8 energy)

### 2.6 Energy Pools

| Profession | Base Energy | Regen Pips | Special |
|------------|-------------|------------|---------|
| Warrior | 20 | 2 | Uses adrenaline primarily |
| Paragon | 25 | 2 | Leadership returns energy per ally affected by shouts/chants |
| Ranger | 25 | 3 | Expertise reduces skill costs |
| All casters | 30 | 4 | — |

Each energy pip = **1 energy per 3 seconds**. So 4 pips = 1.33 energy/sec.

Elementalist Energy Storage adds +3 max energy per rank (rank 12 = +36,
total ~66 base energy).

### 2.7 Health Regeneration and Degeneration

Health regeneration/degeneration is measured in **pips**. Each pip =
**2 HP/sec**. The net regen/degen is capped at **±10 pips** (±20 HP/sec).

Natural regen in combat depends on current health percentage and effects.
Multiple degen conditions stack additively (Burning -7 + Poison -4 + Bleeding -3
= -14 pips, capped to -10).

---

## 3. Equipment & Weapon Sets

### 3.1 Weapon Swapping

Characters have up to **4 weapon slots** (F1–F4). Swapping is instant and can
be done during most actions (but not while knocked down). **Weapon swaps are
visible to enemies** — opponents can see your equipped weapon model change,
which leaks tactical information.

### 3.2 Weapon Set Types

| Set | Components | Purpose |
|-----|-----------|---------|
| **40/40 Set** | Wand + Focus, both with 20% HCT (Halves Casting Time) and 20% HSR (Halves Skill Recharge) for a specific attribute | Offensive casting. Effective probability is **36%** per roll (not 40%) due to independent probability: 20% + 20% × 80% = 36%. |
| **Defensive (Shield) Set** | One-handed weapon + Shield (+8 AR, +30 HP, +10 AR vs specific damage type) | Swapped to when taking damage. PvP players carry multiple shields for different damage types. |
| **High-Energy Set** | Staff or Wand+Focus with +energy mods (+15 energy, -1 regen) | Swapped to momentarily before casting expensive skills, then swapped back to avoid the regen penalty. |
| **Martial Set** | Axe/Sword/Hammer | Primary damage dealing for frontline. Damage mods (Vampiric, Zealous, Sundering). |
| **Enchanting Set** | Weapon with "of Enchanting" mod (+20% enchantment duration) | Swapped to before casting key enchantments, then swapped back. |

### 3.3 Weapon Swap as Tell

In competitive GvG, an experienced opponent can read weapon swaps:

- Warrior swaps to **40/40 caster set** → likely about to use a skill that
  benefits from HCT/HSR, or faking a spike.
- Monk swaps to **shield set** → expects incoming damage, bracing for spike.
- Caster on **40/40** → actively casting. On **shield** → defensive posture.

AegisSpike tracks weapon set as a **dimension** on every combat event to
quantify these tells and correlate them with spike outcomes.

---

## 4. Cast Time & Aftercast Mechanics

### 4.1 Cast Times

| Notation | Duration | Interrupt Difficulty |
|----------|----------|---------------------|
| ¼ cast (0.25s) | Effectively instant | Nearly impossible to interrupt reactively |
| ½ cast (0.50s) | Very fast | Very difficult to interrupt |
| ¾ cast (0.75s) | Fast | Difficult but possible |
| 1s cast | Standard | Standard interrupt window |
| 2s cast | Long | Easy to interrupt, high-risk cast |
| 3s+ cast | Very long | Extremely vulnerable (spirits, resurrections) |

### 4.2 Aftercast Delay

A **0.75-second** delay occurs after successfully completing any skill that has
an activation time. During aftercast:

- The player cannot move, attack, or activate another skill.
- The delay **cannot be reduced** by any attribute or effect (including
  Mesmer's Fast Casting, which reduces activation time but not aftercast).
- Aftercast does **not** occur if the skill is interrupted, cancelled, or fails
  to activate.

**Skills with no aftercast:** Shouts, stances, flash enchantments, pet attacks.

### 4.3 Interrupts

A skill can only be interrupted **during its activation time** (while the cast
bar is filling). Once activation completes, the skill cannot be interrupted —
the aftercast window is not interruptible.

When a skill is interrupted:
- The skill does not complete. No effect occurs.
- No energy is refunded (energy is spent at activation start).
- No aftercast delay from the interrupted skill.
- The skill may go on a shortened recharge or full recharge depending on the
  interrupt source (Distracting Shot disables the skill for an extra period).

**Daze interaction:** Dazed targets have spell cast times doubled and all
spells become "easily interruptible" (any attack hit interrupts, not just
interrupt skills). This creates massive vulnerability windows.

### 4.4 Cancel Casting (C-Casting)

A player can cancel their own skill activation by pressing Escape or moving
before the cast completes. When cancelled:

- No effect occurs. No energy is spent.
- No aftercast delay.
- The skill goes on a very short recharge (typically instant or a few seconds).

**Tactical uses:**
- **Baiting interrupts:** Begin casting a skill, cancel it to waste the
  enemy's interrupt, then cast the real skill.
- **Baiting Diversion:** Begin a non-critical cast to trigger Diversion's
  recharge penalty on a throwaway skill instead of your elite.
- **Faking spikes:** A team can cancel-cast to fake a spike, forcing the
  enemy monks to waste defensive cooldowns on nothing.

---

## 5. GvG Match Structure

### 5.1 Format

- **8 versus 8** players, each team with their own guild hall map.
- One team attacks (plays on the other team's map), one defends.
- Objective: Kill the enemy **Guild Lord** NPC, or have more living players
  and NPCs when the match ends.

### 5.2 Key NPCs

| NPC | Stats | Role |
|-----|-------|------|
| **Guild Lord** | 1,680 HP, 70 AR, +5 health regen, Warrior/Ranger | Primary objective. Protected by a damage cap at match start (max 25 HP/sec initially, scaling to 300 HP/sec over 12 minutes). |
| **Bodyguard** | — | Heals the Guild Lord. Uses Oath of Healing. |
| **Knights** (2) | — | Warrior NPCs with physical damage and Healing Signet. |
| **Archers** (8) | — | Ranger NPCs stationed around the guild hall perimeter. |

### 5.3 Flag Stand & Morale

The **flag stand** is the central map objective. Each team has a flag runner who
carries the team flag from base to the stand.

- Holding the flag stand (your flag planted, enemy flag not) for **2 minutes**
  grants a **Morale Boost**.
- **Morale Boost:** +10% max health and energy. Recharges ALL skills including
  Resurrection Signets. Reduces Death Penalty. The Guild Lord permanently gains
  +300 max HP per morale boost.

### 5.4 Death Penalty (DP)

Each death incurs **-15% maximum health and energy**, stacking up to **-60%**.
Reduced by gaining experience (75 XP = -1% DP) or by Morale Boosts.

At high DP, even full-health players become extremely fragile. A monk at -60%
DP has roughly 200 HP instead of 535 — practically one-shot territory.

### 5.5 Victory or Death (VoD)

Triggered at the **28-minute mark**. All NPCs gain +10% damage and march toward
the center in waves:

1. First wave (4 archers) at 28:00
2. Second wave (4 archers) at 28:15
3. Third wave (2 knights + bodyguard) at 28:30
4. Guild Lord marches out at 30:00

NPC damage increases by +5% per minute after VoD. The match enters a chaotic
endgame where NPC survival becomes critical.

---

## 6. Team Roles & Composition

### 6.1 Frontline (Typically 2 Players)

**Professions:** Warrior, Dervish, sometimes Assassin.

**Role:** Primary damage dealers, spike executors, target callers. Melee
professions are the most energy-efficient damage source because auto-attacks
deal high DPS for zero energy cost, supplemented by burst skills.

**In a spike:** Apply Deep Wound (Eviscerate, Dismember), call the target
(Ctrl+Click in team chat), and execute burst damage skills on the countdown.

**Key skills:** Eviscerate, Executioner's Strike, Bull's Strike (knockdown),
Frenzy, Rush, Shock.

### 6.2 Midline (Typically 2–3 Players)

**Professions:** Mesmer, Elementalist, Necromancer, Ranger, Paragon.

**Role:** The most versatile line. Positioned between frontline and backline.
Dual purpose — support allies and disrupt enemies.

| Midline Role | Primary Job | Key Skills |
|-------------|-------------|------------|
| **Mesmer (Domination)** | Interrupt enemy monks, energy denial, shutdown hexes | Power Drain, Power Leak, Diversion, Shame |
| **Mesmer (Illusion)** | Pressure damage, snares | Clumsiness, Wandering Eye |
| **Elementalist** | Spike damage, knockdowns, wards | Mind Burn, Gust, Gale, Ward Against Foes |
| **Necromancer** | Hex pressure, healing reduction, cover hexes | Shadow Shroud, Lingering Curse, Parasitic Bond |
| **Ranger** | Interrupts, Apply Poison, split pressure | Savage Shot, Distracting Shot, Broad Head Arrow (Daze) |
| **Paragon** | Shout support, spike damage (spear) | "Go for the Eyes!", Cruel Spear, defensive shouts |

### 6.3 Backline (Typically 2–3 Players)

**Professions:** Monk, Ritualist.

**Role:** Keeping the team alive. The highest-priority targets for the enemy
(kill the monks, win the game) and the most protected by allies.

| Backline Role | Attribute Line | Key Skills |
|--------------|----------------|------------|
| **Healing Monk (WoH)** | Healing Prayers | Word of Healing, Patient Spirit, Infuse Health, Dwayna's Kiss |
| **Protection Monk** | Protection Prayers | Spirit Bond, Protective Spirit, Shield of Absorption, Aegis, Guardian |
| **Hybrid Monk** | Both | Mix of healing and protection |
| **Ritualist** | Restoration/Communing | Weapon of Warding, Protective Was Kaolai, Wielder's Boon, spirits (Shelter, Life) |

### 6.4 Flag Runner (1 Player)

Self-sufficient character who runs the flag from base to the flag stand
repeatedly. Must handle 1v1 fights against the enemy runner.

**Common professions:** Ranger, Elementalist, Dervish, Paragon.

**Requirements:** Speed boost, self-healing, some offensive capability.

### 6.5 Spike Caller

Usually one of the frontline warriors. Designates the spike target using
Ctrl+Click (target call in team chat) and coordinates the countdown via
voice comms ("3... 2... 1... spike").

With two frontliners, they typically alternate: while one rebuilds adrenaline
after a spike, the other calls the next.

---

## 7. Offensive Tactics

### 7.1 Spike

A coordinated burst of damage from multiple team members focused on a single
target, intended to kill before monks can react. The defining offensive action
in GvG.

**Anatomy of a spike:**

1. **Setup** (T-7s to T-3s): Apply hexes (Shadow Shroud for healing reduction,
   cover hexes), strip key enchantments, apply Deep Wound.
2. **Call** (T-3s): Spike caller Ctrl+Clicks the target. Begins countdown.
3. **Execution** (T-0): All damage skills land within a ~1-second window.
   Warriors use Eviscerate + Executioner's Strike. Midline adds burst damage.
   Mesmers interrupt enemy monks attempting to save the target.
4. **Resolution** (T+0 to T+5s): Target dies (kill) or survives (mitigated).

**AegisSpike classification:**
- **Clean spike:** Target goes from full HP to dead in under 2 seconds.
- **Forced spike:** Target dies but required extended pressure beyond the
  initial burst.
- **Mitigated spike:** Target survives. Backline successfully saved them.
- **Attrition spike:** Target survives but the defending team exhausted
  significant resources (energy, cooldowns) to save them.

### 7.2 Train

Sustained melee pressure where frontline characters chase and attack the same
target continuously. Unlike a spike (burst), training is sustained damage over
time. The goal is to drain the enemy monks' energy and cooldowns through
constant healing demand.

Training is often combined with periodic spike attempts — train a target to
exhaust monk resources, then spike when defensive cooldowns are down.

### 7.3 Pressure

A strategic approach focused on dealing more total damage than the enemy can
heal over time, rather than burst kills. Pressure builds use conditions
(Burning, Poison, Bleeding), hexes, and sustained damage to overwhelm the
enemy backline's ability to keep up.

**AegisSpike metric:** Cumulative Pressure Index (CPI) — a rolling 60-second
integral of weighted damage, hex degeneration, and condition severity.

### 7.4 Split

Dividing your team to attack multiple objectives simultaneously. Typically
2–3 players split off to attack enemy base NPCs (archers, knights, bodyguard,
or Guild Lord) while the remaining players fight at the flag stand.

**Strategic purpose:** Forces the enemy to choose between losing the flag
stand fight (if they send players to defend base) or losing NPCs/Guild Lord
(if they don't). The split team must be self-sufficient.

### 7.5 Collapse

Regrouping split players to a single location. Called when:
- The split is failing and players need to regroup.
- The enemy splits and your team collapses to outnumber them at one location.
- A critical fight requires full team presence.

### 7.6 Target Calling and Faking

**Target call:** Ctrl+Click on enemy broadcasts to team chat. Voice comms
provide the countdown.

**Faking:** Using cancel-casting, weapon swaps, or positioning to feint a spike
on one target, bait out defensive cooldowns (Aegis, Guardian, Protective Spirit),
then immediately spike a different target while those defensive skills are on
recharge.

---

## 8. Defensive Tactics

### 8.1 Pre-Protting

Preemptively applying protective enchantments (Protective Spirit, Spirit Bond,
Shield of Absorption) to a target *before* the spike arrives, rather than
reactively after damage begins. Requires reading the enemy's spike target
correctly — wasted if applied to the wrong target.

### 8.2 Pre-Veiling

Maintaining **Holy Veil** on allies before hexes land. Holy Veil is a
maintained enchantment that:
- Doubles the cast time of any hex targeting the veiled ally (making hexes
  easier to interrupt).
- When the monk manually drops Holy Veil, it removes one hex from the target.

**Tactical use:** Pre-veil a likely spike target. When a dangerous hex lands,
immediately drop Holy Veil to remove it before the enemy can apply a cover hex.

### 8.3 Peeling

Helping a targeted ally escape by applying crowd control, snares, or damage to
the enemies attacking them. Examples:
- Monk casts Guardian or Aegis on the spike target.
- Elementalist uses Gust to knock down the attacking warrior.
- Mesmer uses Diversion on the warrior to disable their spike skill.

**AegisSpike term:** Forced Utility Countermeasure — a defensive skill used
reactively on an attacker during a spike. Tracked for the Countermeasure
Baiting Index.

### 8.4 Kiting

Using movement to stay out of melee range while avoiding damage. Essential for
squishy backline characters being pursued by warriors.

**Pre-kiting:** Anticipating an enemy's approach and beginning to move away
*before* they reach you. Proactive positioning rather than reactive kiting.
High-level monks pre-kite based on warrior body language (weapon swaps,
positioning, Bull's Strike range).

### 8.5 Infuse Health

The most powerful emergency heal in the game. The Monk loses **half their
current HP**; the target ally is healed for 100–136% of the amount lost.

- **0.25-second cast time** — effectively instant, nearly impossible to
  interrupt.
- The health loss is not damage and cannot be prevented by any means.
- Typically followed by a self-heal. The infusing monk becomes temporarily
  vulnerable.
- **AegisSpike relevance:** Infuse Health is the highest-value defensive play.
  A successful infuse that saves a spike target scores maximum defensive
  credit.

### 8.6 Protective Spirit + Spirit Bond Combo

The cornerstone of Protection Prayers defense:

- **Protective Spirit:** Caps damage from any single hit to 10% of the
  target's max health (~50 HP per hit).
- **Spirit Bond:** Whenever the target takes damage exceeding 60 HP from a
  single hit (checked *before* Prot Spirit reduces it), heals for 40–88 HP.

Together: large hits are capped to ~50 damage while simultaneously triggering
an 80+ HP heal. The target effectively *gains* health from being attacked.
This combo is the primary reason spikes require setup (Deep Wound, hex
pressure, enchantment stripping) to succeed — raw damage alone cannot
overcome Prot Spirit + Spirit Bond on an uncompromised target.

### 8.7 Body Blocking

Physically positioning your character to obstruct enemy movement. Used to:
- Prevent warriors from reaching your backline.
- Trap an enemy corpse to prevent resurrection.
- Block narrow map passages during splits.

### 8.8 Balling vs Spreading

- **Balling (up):** Clustering the team together. Enables efficient AoE
  healing (Heal Party, Divine Healing) but creates vulnerability to AoE
  damage (Meteor Shower, Splinter Weapon).
- **Spreading:** Dispersing the team to avoid AoE damage and hex application.
  Reduces AoE healing efficiency.

Good teams dynamically ball and spread based on the threat — spread when
the enemy has AoE pressure, ball when they need efficient healing.

---

## 9. Advanced Mechanical Concepts

### 9.1 Deep Wound in Spikes

Deep Wound (-20% max HP) is not just a stat reduction — it fundamentally
changes the math of a spike:

- A 535 HP monk with Deep Wound has ~428 effective max HP.
- This ~107 HP reduction means ~20% less total damage is needed for a kill.
- Deep Wound also reduces the effectiveness of healing received.
- **AegisSpike classification:** Applying Deep Wound transitions the target
  to S1 (Vulnerable).

### 9.2 Cover Hex Mechanics

Because hex removal is LIFO (removes the most recent hex first), attackers
protect valuable hexes by applying a cheap "cover hex" on top:

1. Necromancer applies **Shadow Shroud** (primary threat — reduces healing).
2. Necromancer immediately applies **Parasitic Bond** (cover hex — cheap,
   long duration, low impact).
3. Enemy Monk uses **Cure Hex** → removes Parasitic Bond (the cover).
4. Shadow Shroud remains active, continuing to reduce healing during the spike.

**AegisSpike metric:** When hex removal hits the cover instead of the primary
threat, the cover hex caster earns **Virtual Damage Prevented (VDP)** — the
estimated healing that would have landed if the primary hex had been removed.

### 9.3 Locked-State Vulnerability

When a player begins a skill with a long cast time (≥1.5s), they enter a
**Locked Vulnerability State**. During this animation:

- They cannot move, cast other skills, or swap weapons.
- They are extremely vulnerable to interrupts and spikes.

**Key examples:**
- Monk using Purge Signet (2.0s activation).
- Ritualist placing a spirit (3.0s activation).
- Elementalist casting Meteor Shower (5.0s activation).

**AegisSpike metrics:**
- **Spatially Blocked Defensive Window:** If an ally dies while a backline
  player is locked in a long cast, the engine logs what defensive skills were
  available but could not be used.
- **Locked-State Exploitation:** Successfully interrupting a player in a
  locked state scores 2.5× the normal interrupt value.

### 9.4 Cooldown Desynchronization

Key defensive skills (Protective Spirit, Spirit Bond, Aegis) have recharges
of 5–30 seconds. If a spike team can execute a second spike *faster* than
the enemy's defensive cooldowns, the backline cannot rotate their safety
skills.

**AegisSpike metric:** Spike Cadence (κ) — the time between consecutive
spikes. If κ ≤ 10s, the enemy's defensive cooldowns are desynchronized,
and the second spike receives a 1.5× Strategic Synergy Multiplier.

### 9.5 Quarterknocking

An advanced warrior technique using fast attack speed (+33% from IAS stance)
combined with Stonefist Insignia (+1 second knockdown duration) to chain
knockdowns with hammers. The target is kept on the ground continuously,
unable to act.

### 9.6 Weapon Swap as Tell

Experienced players read enemy weapon swaps for information:

- **Warrior swaps from shield to martial weapon:** Preparing to spike. If the
  team knows a spike is coming, they can pre-prot.
- **Warrior stays on 40/40 during spike call:** Potential fake or poor play.
  AegisSpike quantifies this via the weapon-set lethality delta.
- **Monk swaps to shield set:** Expects incoming damage on themselves.

### 9.7 Energy Tax and Attrition

Even failed spikes serve a strategic purpose by forcing the enemy to spend
disproportionate resources to survive:

- **Resource Burn Coefficient (Φ):** The ratio of defender energy spent to
  attacker energy spent during a spike window. Φ ≥ 2.0 means the defenders
  spent double the energy — a winning attrition trade.
- **Exhaustion Credit (χ):** Awarded to spike callers when a failed spike
  still forced significant defensive resource expenditure, recognizing that
  the spike was strategically productive even without a kill.

---

## 10. AegisSpike-Specific Analytical Terms

These terms are defined by the AegisSpike engine and do not exist in standard
GW1 terminology.

### 10.1 DTMC States

| State | Name | Definition |
|-------|------|------------|
| S0 | Neutral | Target is healthy. Standard background pressure. |
| S1 | Vulnerable | Target has setup conditions (Deep Wound, Daze, Knockdown, or active Shadow Shroud). |
| S2 | Spike Active | Target receives ≥500 HP of raw damage within a rolling 5-second window. |
| S3 | Mitigated/Saved | Target survives the active spike window. Backline restores their HP. |
| S4 | Dead | Target is eliminated (absorbing state). |

### 10.2 Scoring Metrics

| Metric | Abbreviation | Definition |
|--------|-------------|------------|
| Effective Damage | eDMG | Actual damage credit after overkill correction. Distributes remaining HP proportionally among simultaneous attackers. |
| Piecewise Quadratic Decay | W(t) | Time-decay weight for credit attribution. 100% within 5s of kill, quadratic decay to 0% at 10s. |
| Effective Decay Distance | t_eff | For persistent effects: `max(0, t_spike_start - t_end_influence)`. If a hex persists into the spike window, t_eff = 0 (full credit). |
| Total Performance Score | TPS | Aggregate per-player score: eDMG × W(t) + interrupt points + VDP + exhaustion credits + strategic baiting credits. |
| Lethality Delta | ΔP_death | The change in kill probability when a specific condition or disruption is present vs absent. Measures the tactical value of any setup action. |
| Virtual Damage Prevented | VDP | Credit awarded to a cover hex caster when enemy hex removal hits the cover instead of the primary threat. |
| Clutch Factor | C_mult | Interrupt value multiplier based on target HP: 1.0× (HP ≥75%), 1.5× (25–75%), 2.5× (HP ≤25%). |
| Spike Cadence | κ | Time between consecutive spikes: κ = t_spike_n − t_spike_{n-1}. |
| Cumulative Pressure Index | CPI | Rolling 60-second integral of weighted damage + hex degeneration + condition severity. |
| Resource Burn Coefficient | Φ | Ratio of defender energy spent to attacker energy spent: Φ = E_def / E_att. |
| Exhaustion Credit | χ | Credit for failed spikes that forced significant defensive resource expenditure. |
| Over-Heal Overhead | OHO | Ratio of total group healing to target-specific damage prevented during a spike. OHO > 1.5 indicates collateral strategic impact. |
| Countermeasure Baiting Index | CBI | Tracks defensive cooldowns forced by spikes and the vulnerability windows created. |
| Energy Burn Metric | EBM | Total energy spent by defenders during a spike+stabilization window. |
| Spatially Blocked Defensive Window | — | Logged when a backline player is in a locked cast animation while an ally dies, identifying defensive skills that were available but unusable. |

### 10.3 Match-Level Metrics

| Metric | Definition |
|--------|------------|
| **MVP** | Highest TPS player across the match. Includes archetype-specific context. |
| **Team Spider Chart** | 5-axis radar comparing teams: Spike Execution, Defensive Saves, Disruption, Pressure/Attrition, Coordination. Normalized 0–100. |
| **Markovian Attrition Chain** | Tracks consecutive spikes on the same target within 120s. Models increasing kill probability due to backline resource exhaustion. |
| **High Background Pressure** | Flagged when CPI exceeds 350 HP/s sustained over 60 seconds. Depresses expected defensive output. |

---

## 11. Common GvG Slang & Abbreviations

| Term | Meaning |
|------|---------|
| **Prot** | Protection Monk, or the act of applying protective enchantments |
| **Infuse** | Using Infuse Health (the skill), or the Monk who carries it |
| **WoH** | Word of Healing — the dominant Healing Prayers elite |
| **SoA** | Shield of Absorption |
| **PS** | Protective Spirit |
| **SB** | Spirit Bond |
| **RC** | Restore Condition |
| **RoF** | Reversal of Fortune |
| **BHA** | Broad Head Arrow — Ranger elite that inflicts Daze on interrupt |
| **D-Shot** | Distracting Shot |
| **S-Shot** | Savage Shot |
| **Evis** | Eviscerate |
| **Exec** | Executioner's Strike |
| **Bull's** | Bull's Strike |
| **Para** | Paragon |
| **Rit** | Ritualist |
| **Mes** | Mesmer |
| **Ele** | Elementalist |
| **Necro** | Necromancer |
| **Sin** | Assassin |
| **Derv** | Dervish |
| **IAS** | Increased Attack Speed (e.g., Frenzy gives +33% IAS) |
| **IMS** | Increased Movement Speed |
| **KD** | Knockdown |
| **DW** | Deep Wound |
| **Rupt** | Interrupt |
| **Stripped** | Had an enchantment removed by the enemy |
| **Covered** | A hex or enchantment with a cover effect on top |
| **Overextended** | Pushed too far forward, out of backline support range |
| **Res** / **Rez** | Resurrect / Resurrection |
| **Res Sig** | Resurrection Signet |
| **Morale** / **MB** | Morale Boost |
| **VoD** | Victory or Death |
| **DP** | Death Penalty |
| **GvG** | Guild versus Guild |
| **HA** | Heroes' Ascent (different PvP format) |
| **TA** | Team Arenas |
| **Obs** | Observer mode (watching matches) |
| **Meta** | The dominant team builds/strategies at a given time |
| **Build** | A specific team composition with assigned skills |
| **Bar** | A single player's skill bar (the 8 skills they bring) |
| **Template** | Encoded skill bar that can be shared and loaded |
