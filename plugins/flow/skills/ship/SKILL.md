---
name: ship
description: Finishes a change so it can be merged and auto-deployed - tests for every acceptance criterion, lint, docs, DECISIONS.md, a clean PR that maps criteria to evidence. Use when implementation of an issue is done or the user says "klaar", "afmaken", "maak een PR", "ship it". This is the last 20 percent; do it fully.
when_to_use: Trigger after code changes for an issue are complete, and always before opening or updating a pull request. Deployment itself is NOT done here; merging to main triggers the deploy workflow.
---

# Ship: the last 20 percent

The user is good at the first 80 percent and does not want to do the last 20. You do it, completely, every time.

## Checklist (all of it, in order)

1. **Acceptance criteria**: open the linked issue. For every criterion, point to a test that proves it. Missing test = write it. A criterion that cannot be tested automatically gets a manual check step in the PR.
2. **Run everything** the repo defines (see `## Project facts` in CLAUDE.md: test, lint, typecheck, build). Fix failures. Do not skip or weaken tests to get green.
3. **Container sanity**: if there is a Dockerfile, run `docker build` (or the project's build command) so the deploy will not fail on build.
4. **Config and secrets**: new env vars go in Secret Manager or the deploy workflow, never in code. List any new ones in the PR under "Ops".
5. **Docs**: update README / CLAUDE.md Project facts if commands, env vars or architecture changed. Append architectural choices to `DECISIONS.md` (date, decision, why, alternatives).
6. **Diff hygiene**: remove debug code, commented-out blocks, stray files. Keep the diff about this issue only.
7. **PR**: open or update it with `gh pr create` / `gh pr edit`, body:

```
Closes #<issue>

## What changed
2-4 bullets, user-facing first.

## Acceptance criteria -> evidence
- [x] <criterion> -> <test name or check>

## Ops
New env vars, migrations, feature flags, rollback note ("revert this PR" or the specific step).

## Not done / follow-ups
Anything deliberately left out, as new issue links.
```

8. Stop. Do not merge. Merging is the user's one decision; it triggers deploy and the post-deploy check automatically.

## Rules

- Red CI is never "done". If CI fails on the PR, read the logs (`gh run view --log-failed`), fix, push again.
- Database migrations must be backward compatible with the currently running revision (expand first, contract in a later PR).
- If the change is risky (auth, payments, data deletion, external writes), put it behind a feature flag and say so in Ops.
