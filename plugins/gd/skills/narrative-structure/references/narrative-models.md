# Narrative models

> Adapted from Claude-Code-Game-Studios agents `narrative-director`, `world-builder` (MIT © 2026 Donchitos), narrative-skills `if-design-structure`, `continuity-check` (MIT © 2026 Rafael García Moreno), gstack-game `game-review/motivation` ludonarrative table (MIT © 2026 fagemx). See ATTRIBUTION.md.

## Branching structures

| Structure | Shape | Cost | Good for |
|---|---|---|---|
| Branch & bottleneck | Diverge, reconverge at key beats; state carries flavor | Medium | Chapter-based narrative RPG, VN |
| Hub & spoke | Hub with optional spokes in any order | Low–medium | Cozy/day loops, investigation |
| Parallel paths | 2–3 routes through same beats with different framing | Medium | Faction/character routes |
| State-driven / storylets | Small content units gated by state qualities | High design, scales well | Card-based narrative, systemic RPG |
| Time-cave | Every choice branches, no reconvergence | Explodes | Short pieces only |
| Open quest | Goals with multiple solutions via systems | High | Immersive sim moments |

Rule of thumb: >3 levels of branching without reconvergence = combinatorial explosion → add bottleneck or convert to state.

## Consequence tree (per choice)
| Field | Content |
|---|---|
| id | `choice_<scene>_<n>` |
| Context | What the player knows / doesn't know at this moment |
| Options | Each option's intent (not text) |
| Immediate consequence | Visible within the scene |
| Delayed consequence | Where and when it pays off (scene id) |
| State change | `var = value` |
| Reconverges at | beat id or "never" |
| Player-visible? | How the player notices the consequence |

Checks: every choice has at least one noticed consequence (or is documented as intentional flavor) · every delayed payoff has a setup · no flag is set but never read · no flag is read but never set.

## Critical path
- Can be completed via ≥1 understandable route without fixed order.
- Critical knowledge/items have a reliable source and an alternative route when exploration is open.
- Fail-soft policy for missed content and revisits is defined.

## World element (world.md sections)
Core concept (one line) · Rules (possible / impossible) · History (events that shaped now) · Factions & tensions · Places · Connections · Player relevance (how the player touches it) · Contradictions check · Open questions.

## Ludonarrative tests
Theme ↔ Mechanics · Tone ↔ Feel · Character ↔ Abilities · World ↔ Systems. For each: pass / fail / intentional (with note).
Positive design: find one mechanic that *says* the theme (e.g., a cozy day loop that the night horror slowly corrupts: safe routines become the source of dread).

## Continuity check
Compare facts across docs: names, dates/timeline, who-knows-what, object locations, relationship states, world rules. Classify: contradiction · drift · ambiguity (do not resolve ambiguity by invention — flag it).

## branches/<branch>.md skeleton
```markdown
---
status: draft
updated: YYYY-MM-DD
structure: branch-and-bottleneck | hub | parallel | storylets | open
---
# Branch: <name>
## Purpose (what this branch does for the player / pillar)
## Entry conditions (state)
## Beats
| id | Beat [what happens / what the player learns / emotion] | Choice? |
|---|---|---|
## Consequence trees
## State (reads / writes)
| var | type | set in | read in |
|---|---|---|---|
## Exits / reconvergence
## Ludonarrative notes
## Open questions
```
