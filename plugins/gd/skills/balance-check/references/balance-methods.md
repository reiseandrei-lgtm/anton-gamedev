# Balance methods

> Adapted from gstack-game `balance-review` references (difficulty-curve, economy-model, progression, character-balance, monetization, scoring, gotchas) — MIT © 2026 fagemx — and Claude-Code-Game-Studios `balance-check` (MIT © 2026 Donchitos). See ATTRIBUTION.md.

## Difficulty curve
Healthy = sawtooth in the Flow channel (tension → release → higher baseline).

| Condition | Verdict |
|---|---|
| Step > 2× previous | SPIKE |
| Multiple spikes in 3 consecutive steps | DEATH ZONE (escalate) |
| No increase for 5+ steps | PLATEAU |
| First spike before all core mechanics are taught | PREMATURE (escalate) |
| Spike coincides with a monetization prompt | FRUSTRATION MONETIZATION (escalate) |

Metric: time-to-complete, failure rate, attempts, stat threshold — ask which applies.
Recovery: after 3 failures what changes? Cost of failure 1–5 min ok, 30+ min red. Is failure informative? Can failure yield something?

## Economy
Per currency: faucet/hour and sink/hour for a typical active player.
Ratio >1.2 inflationary · 0.9–1.1 healthy · <0.8 deflationary.
Projection table Day 1/7/14/30/90: earned, spent, stockpile. Flag the day stockpile > 2× the most expensive item.
Currencies: 1–2 clear · 3 only with distinct purposes · 4+ red flag.
Gini target (multiplayer economies): co-op/PvE <0.3 · PvP 0.3–0.5 · >0.6 flag.

## Progression
Milestones (adjust per genre; mobile compress 5–10×): first action <30s · "I understand" 2–5min · first meaningful choice 5–15min · first "wow" 30–60min · first identity/build choice 1–3h. Flag >2× or <0.5× target.
**Grind ratio** = meaningful actions / all actions per hour: >0.5 engaging · 0.3–0.5 ok · 0.2–0.3 grindy · <0.2 treadmill. Flag <0.3 for >2h.
Content runway: unique hours before repetition (<5h premium / <2h F2P = red).
Probabilistic rewards need documented bad-luck protection (pity). Pity/expected ratio healthy 1.5–3×.

## Character / card / role balance
Pick one framework and stay consistent: cost curve (power per cost unit), rock-paper-scissors counters, role budget (each role owns a niche).
Card games: mana/cost curve per rarity, card-advantage value, tempo; flag cards strictly better than another at same cost.
Co-op roles: each role necessary in ≥1 common situation; no role optional in >50% of situations.
Win-rate/usage spread (with data): <10% healthy · >15% flag.

## Compound effects
Multiplicative stacking: +10% ×3 = +33%, not +30%. Always compute stacked maximum and check caps.

## Monetization (F2P only)
Free player viability · paywall after hook · pay-to-win perception (cosmetic > convenience > advantage > required) · diminishing returns on spend. Separate soft vs real-money currency analysis. Compute real cost at expected and pity thresholds.

## Scoring (each /10, weighted)
Difficulty 25% · Economy 25% · Progression 20% · Monetization 20% · Character 10%. N/A → redistribute.
- Difficulty: flow adherence 3 · spikes 2 · recovery 3 · variety 2
- Economy: sink/faucet 3 · inflation control 2 · currency clarity 2 · distribution 3
- Progression: milestones 3 · grind ratio 2 · runway 2 · reward schedule 3
- Monetization: free viability 3 · paywall timing 2 · P2W 3 · tier fairness 2
- Character: framework 3 · spread 3 · counters 2 · power-creep plan 2

## Gotchas
Round numbers are aspirations, not measurements · snapshot ≠ projection (always Day 1/7/30) · real-money currency has different ethical stakes · balanced ≠ fair · check stacking · verify "cosmetic only" claims · "standard rates" are not automatically fair.

## Output table skeleton
| Parameter | Current | Proposed | Source (GDD §) | Rationale |
|---|---|---|---|---|
