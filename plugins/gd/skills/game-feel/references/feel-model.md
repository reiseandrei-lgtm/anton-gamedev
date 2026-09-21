# Feel & playability model

> Adapted from gstack-game `feel-pass` (feedback-chains, feel-vocabulary, scoring, gotchas), `build-playability-review` (scoring) and `player-experience` — MIT © 2026 fagemx. See ATTRIBUTION.md.

## 4-beat feedback chain
ANTICIPATION (wind-up, 2–10f) → ACTION (1–5f, shortest) → IMPACT (3–8f, where feel lives) → RESOLUTION (5–15f, return to neutral).
Impact channels: visual (flash, particles, numbers) · audio · haptic · camera (shake, zoom, hitstop) · target reaction.

"Soul" examples: melee — hitstop · ranged — hit marker · jump — apex hang + landing squash/sound · pickup — fly-to-player tween · damage taken — visible i-frames.
Non-combat (cozy, cards, VN): card play — lift/snap + sound + board reaction; dialogue choice — immediate acknowledgement (sound, portrait reaction) before text; crafting/placing — snap + settle + ambient response.

## Dead time
0–5f normal · 5–15f ok between actions · 15–30f suspicious · 30f+ (0.5s) **flag** · 60f+ (1s) **escalate**. Authored dramatic pauses are not dead time; anticipation and hold states are not dead time.

## Vocabulary (use only these)
- Responsiveness: **snappy** <50ms · **responsive** 50–80ms · **sluggish** 80–150ms · **mushy** variable · **disconnected** >150ms.
- Impact: **crunchy** (many channels synced) · **weighty** · **light** · **hollow** (channels missing) · **numb** (none).
- Rhythm: **flowing** · **staccato** · **relentless** · **lurching** · **monotonous**.
- Clarity: **readable** · **telegraphed** · **obscured** · **cryptic**.
- Energy: **charged** · **released** · **flat** · **overloaded**.

## Feel score — 7 × 0–2 = /14
Responsiveness (<50ms=2, 50–100=1, >100=0) · Clarity · Impact (full chain, multi-channel) · Rhythm (tension/release) · Payoff (reward ∝ effort) · Dead time (inverse) · Overload/noise (inverse).
Verdict: 12–14 ALIVE · 9–11 BREATHING · 6–8 FLAT · 3–5 MUDDY · 0–2 DEAD.

## Playability score — 6 × 0–2 = /12
Loop closure · Session viability (5+ min with variation) · Onboarding (goal+controls in 60s) · Failure recovery (clear cause, <5s retry) · Retention signal ("one more try") · Peak moment (someone would retell it).
Verdict: 10–12 PLAY-READY · 7–9 ALMOST · 4–6 NOT YET · 0–3 TECH DEMO.

## Gotchas
1. Judging visuals before timing. A white box with 0 lag beats a pretty swing with 5f lag.
2. "Feels good" without a channel.
3. Polish ≠ feel. Polish is surface; feel is latency, cancel windows, curves.
4. Audio is ~40–50% of feel. A landing without sound feels floaty.
5. Evaluating one action instead of the 50th repetition in-loop.
6. Test: strip all VFX — is the action still readable? If not, effects are doing the mechanics' job.

## Report templates

```
Feel: <mechanic> — target: <feeling>
  Responsiveness _/2 — <ms>
  Clarity        _/2
  Impact         _/2 — channels: V/A/H/Cam
  Rhythm         _/2
  Payoff         _/2
  Dead time      _/2 — <longest gap>
  Overload       _/2
  TOTAL _/14 — <verdict>
Top 3 blockers: 1) <channel + timing + fix> 2) … 3) …
```

```
Playability: <build>
  Loop closure _/2 · Session _/2 · Onboarding _/2 · Failure recovery _/2 · Retention _/2 · Peak _/2
  TOTAL _/12 — <verdict>
Top blocker: …
Session timeline: 0:00 … / 0:30 … / X:XX player stops — why
```

## Persona walkthrough
Persona: experience level, genre familiarity, session context (phone on commute, evening PC, co-op with friend).
Timeline bullets: what they see → what they try → what they understand/misunderstand → friction → emotion. End with the churn moment and its cause. Analysis only, no prose narration.
