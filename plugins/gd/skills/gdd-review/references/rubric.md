# GDD review rubric

> Adapted from gstack-game `game-review` references (core-loop, progression, economy, motivation, risk, design-consistency, scoring) — MIT © 2026 fagemx. See ATTRIBUTION.md.

## Mode weights

| Section | Mobile | PC/Console | Multiplayer | Narrative |
|---|---|---|---|---|
| 1 Core Loop | 25% | 30% | 25% | 15% |
| 2 Progression & Retention | 25% | 20% | 15% | 15% |
| 3 Economy | 25% | 10% | 20% | 5% |
| 4 Motivation | 10% | 15% | 15% | 30% |
| 5 Risk | 5% | 10% | 10% | 10% |
| 6 Cross-Consistency | 10% | 15% | 15% | 25% |

Section N/A (e.g., no economy) → redistribute its weight equally.

## 1. Core Loop — /10
MDA check: design must flow backward from Aesthetics (8: Sensation, Fantasy, Narrative, Challenge, Fellowship, Discovery, Expression, Submission) → Dynamics → Mechanics. **Mechanics-first with no target feelings: −3.**
Loop tiers: micro 10–30s · meso 5–15min · macro session · meta days. All four should be explicit.

| Criterion | Pts | Rule |
|---|---|---|
| Clarity | 0–2 | One sentence "verb → feedback → reward → repeat" |
| Session fit | 0–2 | Loop completes inside target session length |
| Depth | 0–2 | Mastery = doing it better, not more |
| Fail state | 0–2 | Failure teaches and creates decisions |
| Uniqueness | 0–2 | "It's the game where you…" test |

Questions: Is the micro-loop fun with zero rewards? What does the player do on the 100th repetition that they didn't on the 1st? What happens in the 5 seconds after failure?
ESCALATE: no core loop defined — features without moment-to-moment play.

## 2. Progression & Retention (Flow) — /10

| Tier | Time | SDT need |
|---|---|---|
| FTUE | first 60s | Competence — "I can do this" |
| D1 | 0–24h | Autonomy — "I want to try MY strategy" |
| D7 | 1–7d | Competence — "I'm getting better" |
| D30 | 7–30d | Relatedness — "This is MY world/team" |

Flow: sawtooth (tension → release → higher baseline). Flat = boredom; vertical spike = frustration; not described = assumes difficulty "just works".

| Criterion | Pts | Rule |
|---|---|---|
| FTUE | 0–2 | Time to first meaningful action documented and < benchmark (30s mobile, 2min PC) |
| Retention hooks | 0–3 | D1, D7, D30 hooks named, 1 each ("they'll want to come back" = 0) |
| Difficulty curve | 0–2 | Sawtooth with milestone releases described |
| Churn points | 0–3 | Top 3 quit points with mitigation, 1 each |

Premium narrative games: replace D1/D7/D30 with "session-to-session pull" and "chapter cliffhanger" hooks.

## 3. Economy — /10 (N/A if none)
Every currency needs a sink/faucet map. **No map: −3.** Know which reinforcement schedule is used (fixed/variable ratio/interval); variable ratio on core progression = ASK (wellbeing).

| Criterion | Pts | Rule |
|---|---|---|
| Currency clarity | 0–2 | ≤3 currencies with intuitive exchange |
| Sink/faucet | 0–3 | Full map with equilibrium analysis |
| Monetization ethics | 0–3 | No pay-to-win in competitive, no IAP before aha-moment (N/A premium → redistribute) |
| Spending tiers | 0–2 | Value for minnow/dolphin/whale (F2P only) |

Red flags (−1 each): >3 currencies without purpose; no sinks; hard currency pay-only; no pity for probabilistic rewards; reward schedule undocumented.

## 4. Motivation (MDA · SDT · Ludonarrative) — /10

SDT per system: Autonomy (meaningful choice) · Competence (skill growth) · Relatedness (connection). **A system serving zero SDT needs doesn't motivate → ASK.**
Player types: Bartle (Achiever, Explorer, Socializer, Competitor) or Quantic Foundry (Action, Social, Mastery, Achievement, Immersion, Creativity). GDD must know whom it serves and whom it doesn't.

Ludonarrative consonance:

| Test | Pass | Fail |
|---|---|---|
| Theme ↔ Mechanics | "Choices matter" + real branching | "Choices matter" but all paths converge |
| Tone ↔ Feel | Dark story + weighty mechanics | Dark story + bouncy forgiving mechanics (unless intended) |
| Character ↔ Abilities | Weak character, vulnerable gameplay | "Weak" character one-shots everything |
| World ↔ Systems | Scarce world, scarce economy | Post-apocalypse with fully stocked shops |

Intentional dissonance is valid if documented.

| Criterion | Pts | Rule |
|---|---|---|
| SDT coverage | 0–3 | 1 per need served by a core system |
| Player targeting | 0–3 | Targets named · systems serve them · non-targets acknowledged |
| Ludonarrative | 0–2 | Consonant or justified dissonance |
| Emotional arc | 0–2 | Session arc mapped (tension/release/climax) |

Questions: Name a moment the player feels powerful and one they feel vulnerable — how many minutes apart? The story says X — which mechanic also says X?

## 5. Risk — /10
Matrix probability × impact (Minor/Significant/Critical). Categories: pillar violation · scope (Lake vs Ocean: content list with "etc." = Ocean) · technical feasibility (netcode, procgen, save sync) · differentiation · retention cliff.

| Criterion | Pts | Rule |
|---|---|---|
| Identification | 0–3 | All 5 categories rated |
| Mitigation | 0–3 | Every high+ risk has a concrete plan ("we'll playtest" = vague) |
| Pillar coherence | 0–2 | No feature contradicts pillars, or justified |
| Scope realism | 0–2 | Lake with concrete content list |

ESCALATE: Ocean scope with no cut plan and no MVP; critical risk with zero mitigation.

## 6. Cross-Consistency — /10
- **Voice**: does every system deliver what the pillars promise? 0 violations CONSISTENT · 1–2 MINOR DRIFT (ASK) · 3+ MAJOR DRIFT (ESCALATE, #1 finding).
- **Boundaries**: zero state, overflow, level mismatch, failure cascade (network drop, save corrupt), player defiance. Does the response match the pillars? (Cozy fails gently; punishing-but-fair fails transparently.)
- **Storytelling channels**: visual hierarchy · audio as information · animation as character · UI as world-building. 4 Rich / 2–3 Adequate / 0–1 Sparse.
- **Internal**: same term/number described differently in different sections.

Score: Voice 0–4, Boundaries 0–3, Channels 0–2, Internal 0–1.
