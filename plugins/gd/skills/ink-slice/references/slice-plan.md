# Ink slice plan

> Adapted from narrative-skills `if-plan-ink-slice`, `if-design-progression`, `if-draft-ink`, `if-playtest-review` (MIT © 2026 Rafael García Moreno). See ATTRIBUTION.md.

## Slice types
location · dialogue · obstacle · navigation system · inventory/knowledge/skill system · phase transition · ending or major branch.

## Suggested Ink layout (adapt to the project)
```
ink/
  main.ink            # entry point + INCLUDE list
  systems/            # state helpers, navigation loops, shared tunnels
  locations/          # location knots and revisits
  dialogues/          # character conversations and topic loops
  scenes/             # linear scripted scenes (VN-style)
```

## <slice>.plan.md skeleton
```markdown
---
status: draft
updated: YYYY-MM-DD
slice_id: <snake_case>
type: location | dialogue | obstacle | system | phase | ending
---
# Ink slice: <slice_id>

## Source design
- branch: design/narrative/branches/<…>.md (beats …)
- characters: …

## Files
| File | Change |
|---|---|

## Entry / exit
- Entry: `-> knot.stitch` when <state>
- Exits: `-> …` (back to loop / next phase / END)

## State
| var | type | read/write | set where | meaning |
|---|---|---|---|---|

## Player choices (intent, not text)
| id | Intent | Condition | Sticky/once | Result |
|---|---|---|---|---|

## Revisit behaviour
First visit / repeat / after <state>

## Tags (Unity / FMOD / animation conventions)
`#speaker:<id>` `#emotion:<id>` `#sfx:<fmod_event>` `#music:<state>` …

## Locks & keys
| id | type | requires | grants | scope | critical | fallback |
|---|---|---|---|---|---|---|

## Acceptance criteria
- [ ] start → every exit reachable
- [ ] no choice leads to an unintended dead end
- [ ] all state vars declared in plan; none unused
- [ ] revisit handled

## Review results
| Severity | Finding | File / knot | Fix |
|---|---|---|---|
```

## Locks & keys checks
1. Extract implied blockers from branches, dialogue topics, map.
2. Each blocker → explicit requires/grants.
3. Critical progress achievable via ≥1 understandable route.
4. Alternate routes for critical knowledge when exploration is open.
5. Detect soft locks, circular dependencies, unlocks that don't change play.
6. Minimum state variables needed — no more.

## Playtest review dimensions (static)
start-to-completion route · location reachability · character availability · critical clue availability · gates (inventory/knowledge/skill/relationship) · circular dependencies · repeated choices & revisits · accidental one-way exits · unavailable/premature endings · vars used in Ink but absent from plan · vars in plan but unused in Ink.
Classify: blocking · major · minor · polish. Don't treat every missed optional line as blocking; don't ignore soft locks caused by dialogue order.
