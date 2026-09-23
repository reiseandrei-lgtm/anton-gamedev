# Slice selection & handoff package

> Adapted from gstack-game `prototype-slice-plan` (slice-types, scoring) and `implementation-handoff` (handoff-template) — MIT © 2026 fagemx. See ATTRIBUTION.md.

## Slice types

| Type | Proves | Fake | Typical build |
|---|---|---|---|
| Mechanic | Core verb is fun in isolation (30s, no progression) | Art, audio, UI, levels | 3–7 days |
| Onboarding | New player gets it in 60s | Everything after 2 min | 1–2 weeks |
| Progression | Growth across sessions ("stronger than when I started") | Late game, social | 2–3 weeks |
| Combat | Combat readable, satisfying, deep (2–3 enemy types + mini-boss) | Story, economy | 1–3 weeks |
| Economy | Resource flow creates decisions (often a spreadsheet sim) | All but earn/spend | 1–2 weeks |
| Narrative | Choice → consequence is felt; branch/state holds (one scene/Ink slice) | Art, VO, most systems | 3–10 days |
| Vertical | All systems combine (10–15 min near-final) | Content volume | 4–8 weeks |

Vertical slice only after mechanic prototypes validated the loops — jumping to it first is the #1 scope mistake.
Unsure → Mechanic prototype.

## Scoring — 5 × 0–2 = /10
Validation value (tests the #1 risk) · Feasibility (≤2 weeks = 2) · Signal clarity (binary, visible in 5 min of watching) · Dependency risk (0–1 fakes = 2) · Scope discipline (nothing removable).
8–10 build it · 6–7 fix weakest axis first · 4–5 reconsider · 0–3 not a prototype.

## Handoff template
```markdown
---
status: draft
updated: YYYY-MM-DD
slice_type:
hypothesis: "If …, the player will … within …"
failure_looks_like:
---
# Handoff: <slice>

## 1. Build target (one sentence)
## 2. Scope
### In (MUST / SHOULD / COULD)
### Out (and why)
### Placeholder OK (what it looks like)
## 3. Player experience requirements
| Player action | Expected response (V/A/haptic) | Timing | Feel target |
|---|---|---|---|
## 4. Systems
| System | Role in slice | Exists? | Notes |
|---|---|---|---|
## 5. Assets and audio
| Asset | Real / Placeholder | Spec |
|---|---|---|
Полный список — `design/art/asset-list.md` (priority `slice`); звук — `design/audio/event-map.md`.
## 6. Acceptance
### Engineering Done  (stable IDs: tests and build log reference them)
- [ ] ED1 builds, target framerate, all §3 interactions work
- [ ] ED2 …
### Design Done  ← the important part
- [ ] DD1 player can feel <X> (observable)
- [ ] DD2 player understands <Y> after <Z> encounters
- [ ] DD3 the "soul" is present: <one thing>
### Not done until
- [ ] someone other than the developer played it
## 7. Tempting shortcuts that kill the experience
| Risk | Shortcut | Why it kills it |
|---|---|---|
## 8. How to verify
| What | How | Pass |
|---|---|---|
```

## Common mistakes
All items same priority · criteria without ED/DD IDs · no experiential criteria · "standard" anything · assets without real/placeholder tag · no "soul" named.
