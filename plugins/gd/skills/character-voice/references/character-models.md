# Character & voice models

> Adapted from narrative-skills `create-character-bible`, `define-style-bible`, `if-design-dialogue` (MIT © 2026 Rafael García Moreno) and Claude-Code-Game-Studios `narrative-director` agent principles (MIT © 2026 Donchitos). See ATTRIBUTION.md.

## Character card (characters/<name>.md)
```markdown
---
status: draft
updated: YYYY-MM-DD
id: <snake_case>
---
# <Name>
## Function
- Story: <role in central conflict>
- Gameplay: <what the player does with/against them: quest giver, companion, card, rival…>
## Want / Need
- External want: …
- Internal need: …
- Wound / fear / contradiction: …
## Arc
Start state → pressure → possible end states (per branch)
## Knowledge
| Knows | Hides | Misunderstands | Refuses to discuss |
|---|---|---|---|
## Voice markers (descriptions, not sample lines)
- Sentence length / rhythm:
- Vocabulary / register:
- Avoids:
- Under stress:
- Verbal tell:
## Availability
Where / when they appear; what changes availability
## Dialogue topics
| topic_id | Gate (knowledge / item / trust / location) | One-time reveal? | State change |
|---|---|---|---|
## Relationships (pointer to _relationships.md)
## Open questions
```

## Relationship matrix (_relationships.md)
| A ↔ B | Current status | Tension | What shifts it | State var |
|---|---|---|---|---|

## Voice pillars (voice-pillars.md)
3–5 rules. Each: rule · do (described) · don't (described) · why (pillar/tone).
Cover: register & era, sentence rhythm, humor, how fear/tenderness sound, forbidden clichés, localization notes (RU/EN: idioms that don't survive translation, formal/informal address).

## Dialogue design for free-order conversations
- Conversations must work in any order: acknowledge early/late/repeated encounters.
- Critical clue → reliable route; optional clue → a purpose.
- Repeatable small-talk loop acknowledges prior visits without bloating state.
- Mark topics that disappear, change, or appear after state changes.
- Never assume a fixed conversation order.

## Lean cast rule
Every major character needs a dramatic function AND a gameplay function. Two characters with the same function → merge candidate.
