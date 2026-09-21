# Estimation & scope verdicts

> Verdict thresholds adapted from Claude-Code-Game-Studios `scope-check` and `estimate` (MIT © 2026 Donchitos); Lake/Ocean from gstack-game `game-review/risk` (MIT © 2026 fagemx). Sizes calibrated for solo / 2–4 person indie. See ATTRIBUTION.md.

## Size → person-days (one generalist, Unity)

| Size | Days | Typical examples |
|---|---|---|
| S | 0.5–2 | Tuning pass, one UI screen, one simple enemy/card, one short scripted scene |
| M | 3–7 | New mechanic on existing systems, one location blockout+dress, one dialogue branch set with state |
| L | 8–20 | New system (inventory, relationship, save), one chapter/zone, co-op sync of one mechanic |
| XL | 20+ | Netcode, procgen, custom tools, full chapter at final quality → **split before estimating** |

## Multipliers
- Unproven tech (netcode, procgen, custom shader pipeline, first time with a tool): ×1.5–2
- Content needs art + animation + audio + implementation: add each discipline separately
- Narrative content: design ≠ writing ≠ implementation (Ink/VO) — estimate each
- Polish to final quality: +30–50% on top of functional
- Buffer: +20% on total for unplanned work

## Confidence
High — done similar before · Medium — similar, new twist · Low — never done → prototype a spike first, estimate after.

## Scope creep verdicts (vs baseline)

| Net change | Verdict |
|---|---|
| ≤10% | PASS — on track |
| 10–25% | CONCERNS — targeted cuts |
| 25–50% | FAIL — cut or formally extend |
| >50% | FAIL — stop and re-plan |

## Capacity verdicts (no baseline)
Estimate×1.2 ≤ capacity → PASS · ≤1.3× capacity → CONCERNS · >1.3× → FAIL.

## Lake vs Ocean
Lake: bounded, countable ("10 levels × 3 enemy types"). Ocean: unbounded ("procedural infinite world with emergent stories"). Most failed indies are Oceans that believed they were Lakes.

## scope.md skeleton
```markdown
---
status: draft
updated: YYYY-MM-DD
baseline: <date or none>
---
# Scope
## Capacity
People × h/week × weeks = … person-days (−20% buffer → …)
## Inventory
| Item | Type | Size | Days | Confidence | Pillar | Class (Must/Should/Cut) |
|---|---|---|---|---|---|---|
## Total vs capacity → Verdict
## Cut order (least pillar damage first)
1. … — what breaks: …
## Risks
```
