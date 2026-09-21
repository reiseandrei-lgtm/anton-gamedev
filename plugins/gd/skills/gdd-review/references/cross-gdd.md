# Cross-GDD checklist (mode: cross)

> Adapted from Claude-Code-Game-Studios `review-all-gdds` and `consistency-check` (MIT © 2026 Donchitos). See ATTRIBUTION.md.

Load order: `systems-map.md` → Summary of every `gdd/*.md` → full text only for GDDs involved in a suspected conflict.

## A. Consistency
1. **Dependency bidirectionality** — A depends on B ⇒ B lists A as dependent.
2. **Rule contradictions** — floors/ceilings bypassed elsewhere; two GDDs define the same resource's accumulation differently; state transitions (death, reset) handled differently; timing (same frame vs next); stacking rules.
3. **Stale references** — GDD A references a mechanic GDD B later changed or removed.
4. **Ownership** — one tuning knob / data value owned by two GDDs.
5. **Formula compatibility** — output range of A fits input range expected by B.
6. **Acceptance criteria conflicts** — "cannot die from one hit" vs "boss deals 150% max HP".
7. **Entity drift** — same character/item/enemy with different stats or names across docs.

## B. Design holism
1. **Progression loop competition** — two systems both award the primary resource and call themselves "core".
2. **Attention budget** — count ACTIVE systems (player decides regularly) at the same moment. >3–4 simultaneous = overload.
3. **Dominant strategy** — resource monopoly, risk-free power, option superior in all dimensions, obvious optimal path.
4. **Economic loop** — combined faucets vs combined sinks across all GDDs.
5. **Difficulty consistency** — what scales, how (linear/exp/stepped), when; do systems scale in step?
6. **Pillar alignment** — each system → pillar; systems pulling pillars apart.
7. **Fantasy coherence** — do all systems serve the same player fantasy?

## C. Scenario walkthrough
Pick 2–4 multi-system moments (e.g., combat + economy drop; level-up mid-fight; dialogue choice unlocking a mechanic; any 3+ system chain). Walk step by step: what each system does, in what order, with what data.
Flag: **BLOCKER** (undefined behavior, broken transition, contradiction) · **WARNING** (compounding spikes, uncapped feedback loops, reward conflicts) · **INFO** (ordering ambiguity).

## Verdict
PASS — no blockers · CONCERNS — warnings only · FAIL — any blocker. List GDDs flagged for revision with the exact section.
