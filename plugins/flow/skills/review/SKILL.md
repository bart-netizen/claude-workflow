---
name: review
description: Independent review of a pull request before the human merges. First checks the issue itself against the business purpose, project facts and spec format, then checks the diff against the acceptance criteria and the flow rules. Posts one review comment with a verdict. Never approves, merges, pushes or edits code.
when_to_use: Run by the review workflow once CI is green on a PR, or when the user asks "review PR #N" / "kijk deze PR na". Not for writing or fixing code.
---

# Review: a second pair of eyes before the merge

The builder already checked its own work with `ship`. You are not the builder. Assume nothing it claims is true until you have seen it.

## Gather

1. `gh pr view <N> --json title,body,files,headRefName` and `gh pr diff <N>`.
2. The linked issue (`Closes #<n>`): `gh issue view <n> --comments` (the builder's evidence often sits in a comment).
3. `CLAUDE.md` (purpose, `## Project facts`, out of bounds, domain facts, conventions) and `DECISIONS.md`.
4. Open the tests and code the PR points to as evidence. Read them; do not trust names.

## 1. Was the issue right? (business and spec)

- Does the goal serve the purpose in CLAUDE.md? Would the user notice the change, and is it the change they need?
- Conflicts with out of bounds, DECISIONS.md or domain facts?
- Spec format: Goal, Non-goals, testable Acceptance criteria (with a failure or edge case, "existing tests pass", "deployed service responds healthy"), Notes for the builder, Assumptions.
- Business rules (prices, thresholds, legal or privacy rules) that someone invented without `TODO(user)`?
- Criteria the user would obviously expect but that are missing.

## 2. Does the PR deliver the issue?

- Every criterion has evidence that really proves it: the test asserts the behaviour, not just runs. Name any criterion without real evidence.
- Scope: the diff is about this issue only, and the non-goals are respected.
- Out of bounds and privacy from CLAUDE.md: no personal data, secrets or certificates in code, logs, fixtures or the PR. External calls sit behind client modules; tests run offline.
- Ship checklist: DECISIONS.md for architectural choices, README / Project facts updated, Ops section, no debug code, no skipped or weakened tests.
- Correctness and deploy risk: bugs, missed edge cases, error handling, Dockerfile, new env vars, backward-compatible migrations, a feature flag for risky changes.

## Post

One comment, in Dutch, with `gh pr review <N> --comment --body-file <file>`, at most ~40 lines:

```
**Verdict: ✅ Klaar om te mergen** | **⚠️ Mergen kan, met kanttekeningen** | **❌ Niet mergen**

**Issue vs doel en specs**
1-3 lines; say "klopt" if it does.

**Criteria → bewijs**
- [x] / [ ] <criterion> → <test or file:line>, with "niet bewezen: ..." where the evidence falls short

**Bevindingen**
- Blokkerend: <file:line> what is wrong and why it matters
- Niet blokkerend: ...

**Voor Bart**
Questions only the user can answer (business rules, assumptions to veto). Leave out if none.
```

If there are blocking findings the builder can fix, end with one copyable line that starts with `@claude` and tells the builder exactly what to change. The user posts it; a comment from the workflow itself does not trigger anything, so this never loops.

## Rules

- Never approve, merge, push, label, close or edit files. Comment only; the merge is the user's decision.
- Be concrete: file:line, input, expected vs actual. No style nits beyond the conventions in CLAUDE.md.
- A wrong issue is a finding too: if the issue itself misses the business goal, say so under "Issue vs doel en specs" and give the verdict ❌ even when the code matches the issue.
- If everything is fine, keep it short. Do not repeat the PR body.
