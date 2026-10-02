---
name: ci-report
description: Measures GitHub Actions minutes per repo and workflow (billed the way GitHub bills), estimates monthly cost on GitHub, Blacksmith and Ubicloud, and gives a go/no-go for a self-hosted runner at home. Use when the user asks about CI cost, Actions minutes, "is CI te duur", or whether to buy a runner box.
when_to_use: Trigger on questions about CI/Actions cost, speed or usage, and on the monthly measurement reminder.
allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/ci_usage.py *) Bash(gh api *) Bash(gh repo list *)
---

# CI report: measure first, then decide

## Steps

1. Run `python3 ${CLAUDE_SKILL_DIR}/scripts/ci_usage.py --days 30` (add `--repos owner/a,owner/b` to narrow). It only reads.
2. Find the plan's free minutes: Free 2000, Pro 3000 per month. If unknown, ask once or check `gh api user --jq .plan.name`.
3. Read the table and answer three questions:
   - **Where do the minutes go?** Usually the `claude` workflow (Claude building on the runner), not tests. Name the top 3 workflows.
   - **Waste?** Look for: jobs that wait (sleep, polling), CI on doc-only changes, runs not cancelled when a new push arrives, missing dependency caches (long median on small repos), scheduled jobs that run Claude when nothing changed. Propose the concrete fix per item.
   - **Speed?** Median minutes for `ci` and `claude`. Over ~5 min for CI on a small repo is a speed problem, whatever the cost.
4. **Box decision** (self-hosted runner at home). Recommend it only if at least one holds:
   - paid minutes (above the free quota) cost more than ~EUR 15 per month on the cheapest hosted option for 2 months in a row, or
   - median CI time is the bottleneck and caching did not fix it, or
   - the user wants long or frequent Claude runs that would exceed the free quota.
   Otherwise: stay on cloud, and switch to Ubicloud or Blacksmith only once the free quota runs out.
5. If a box is recommended, give the budget with **current prices verified at primary sources at that moment** (shop pages, energy tariff), never from memory:
   - hardware: a small always-on Linux machine (mini PC, 16 GB RAM, SSD); not the BBG work laptop
   - power: idle watts x 24 x 30 x price per kWh
   - break-even months = hardware cost / (monthly hosted cost avoided - monthly power)
   Also state the risks: GitHub postponed (not cancelled) a $0.002/min self-hosted platform fee; the box must stay on; never attach it to public repos.
6. Report in 10 lines max: minutes and cost per month, top consumers, waste fixes, box yes/no with the reason.

## Rules

- Prices in the script are dated; if older than 3 months, re-check the GitHub, Blacksmith and Ubicloud pricing pages and update `PRICE` in the script via a PR to this plugin.
- Do not change workflows in this skill; propose fixes as issues or as a PR the user approves.
