# claude-workflow

A Claude Code plugin that turns the hand-offs in a solo dev loop into skills, so the human only does the two things that need a human: say **what** to build, and decide to **merge**.

```
idea ──spec──▶ issue ──label "claude"──▶ build ──ship──▶ PR ──merge──▶ deploy ──check-prod──▶ issues
 you                     you                 Claude          you       Actions     Actions / weekly
```

## Skills (plugin `flow`)

| Skill | Fires when | Does |
| --- | --- | --- |
| `spec` | You describe a feature, change or bug | Writes a GitHub issue with goal, non-goals, testable acceptance criteria and its own assumptions |
| `ship` | Code for an issue is done / before any PR | Tests per criterion, lint, docs, DECISIONS.md, PR mapping criteria to evidence. Never merges |
| `check-prod` | "Is it working?", after each deploy, weekly | Reads Cloud Run logs and revisions, opens or updates `prod-check` issues |
| `setup-repo` | "Put this repo on the flow" | Project facts in CLAUDE.md, plugin settings, GitHub Actions for build, deploy and checks |

All skills are model-invoked: you do not type commands, Claude picks them from what you say. Typing `/flow:spec` etc. still works if you want to force one.

## Install (once per machine)

```bash
claude plugin marketplace add bart-netizen/claude-workflow
claude plugin install flow@bart-workflow
```

Then in Claude Code: `/plugin` → Marketplaces → `bart-workflow` → **Enable auto-update**. Pushing to this repo now reaches every machine.

## Put a project on the flow (once per repo)

Open Claude Code in the repo and say: *"zet deze repo op de flow"*. The `setup-repo` skill opens a PR and lists the few things you still set yourself (GCP Workload Identity, repo variables, the `CLAUDE_CODE_OAUTH_TOKEN` secret).

Project-specific facts (GCP project, service, commands) live in each project's `CLAUDE.md`, never in this repo.

## Design rules

- Procedures live in skills, facts in `CLAUDE.md`, decisions in `DECISIONS.md`.
- Acceptance criteria are the contract between spec, build and review.
- Production is read-only for Claude; deploys happen only through merge.
- When you explain something to Claude for the third time, it becomes a skill here.
