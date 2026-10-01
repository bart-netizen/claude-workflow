---
name: spec
description: Turns a rough idea, feature wish or bug report into a GitHub issue with goal, non-goals and testable acceptance criteria, ready for Claude to build. Use whenever the user describes something new to build, change or fix ("ik wil dat...", "kun je ... toevoegen", "new feature", "bug:"), before any code is written.
when_to_use: Trigger on feature ideas, change requests and bug reports in any repo that has a "## Project facts" section in CLAUDE.md. Do not trigger for questions, explanations or one-line fixes the user wants done immediately.
---

# Spec: idea to buildable issue

The user's job ends at "what and why". Your job is to make it buildable without another round of explaining.

## Steps

1. Read `CLAUDE.md` (Project facts, conventions) and `DECISIONS.md` if present. Skim the code the idea touches.
2. Ask at most 2 questions, only when a wrong guess would mean rework (scope, data model, user-facing behaviour). Otherwise decide and write the assumption into the issue.
3. Write the issue with exactly these sections:

```
## Goal
One or two sentences: what changes for the user and why.

## Non-goals
What this explicitly does not do.

## Acceptance criteria
- [ ] Each line is observable and testable: input, action, expected result.
- [ ] Include at least one failure / edge case.
- [ ] Include "existing tests pass" and "deployed service responds healthy".

## Notes for the builder
Files likely touched, data/schema impact, feature flag yes/no, risks.

## Assumptions
Decisions you made without asking. The user can veto these on the issue.
```

4. Size check: if it is more than ~1 day of work or touches more than one service, split it into numbered issues and link them.
5. Create the issue with `gh issue create`. Add label `claude` only if the user said to start building right away; otherwise leave it unlabelled so the user can add the label as their "go".
6. Reply with the issue link and the assumptions list. Nothing else.

## Rules

- Acceptance criteria are the contract for review. If you cannot write a testable line, the idea is not clear yet: say what is missing.
- Never invent business rules (prices, tax logic, thresholds). Mark them `TODO(user)` in Assumptions.
- If a decision is architectural (new service, new datastore, auth change), also append it to `DECISIONS.md` in the PR that implements it.
