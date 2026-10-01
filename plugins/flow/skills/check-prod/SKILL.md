---
name: check-prod
description: Reviews a deployed Cloud Run service - error logs, request latency, failing requests, recent revisions - compares with the previous period and opens GitHub issues for real problems. Use when the user asks "draait het nog", "check productie", "any errors", after a deploy, or when a scheduled run asks for a production check.
when_to_use: Trigger for production health questions about a repo whose CLAUDE.md has a "## Project facts" section with GCP project, region and service. Also the prompt of the weekly scheduled check and the post-deploy check.
allowed-tools: Bash(gcloud logging read *) Bash(gcloud run services describe *) Bash(gcloud run revisions list *) Bash(gh issue list *) Bash(gh issue create *) Bash(gh issue comment *) Bash(curl -s *)
---

# Check-prod: is it actually working?

Read `## Project facts` in CLAUDE.md for: GCP project, region, Cloud Run service name(s), health URL, and any "expected noise" notes.

Window: last 24h after a deploy, last 7 days for the weekly run. Use the window the prompt gives; default 7 days.

## Steps

1. **Revisions**: `gcloud run revisions list --service=<svc> --region=<region> --project=<project> --limit=5`. Note which revision is serving and when it was deployed.
2. **Health**: `curl -s -o /dev/null -w "%{http_code} %{time_total}" <health URL>`.
3. **Errors**: 
   `gcloud logging read 'resource.type="cloud_run_revision" AND resource.labels.service_name="<svc>" AND severity>=ERROR' --project=<project> --freshness=<window> --limit=200 --format=json`
   Group by message signature (strip ids, timestamps, numbers). Count per group, first and last seen, which revision.
4. **Requests**: same filter with `httpRequest.status>=500`, and sample latency from `httpRequest.latency` where present. Flag p95 that looks clearly worse than the previous window.
5. **Scheduled jobs / webhooks**: if Project facts lists jobs or webhooks, confirm each ran in the window (log line or request). Silence is a finding.
6. **Decide** per finding:
   - New error group, or a group that started with the latest revision -> **issue**.
   - Known/expected noise listed in Project facts -> ignore.
   - Existing open issue for the same signature -> comment with new counts instead of a new issue (`gh issue list --label prod-check`).
7. **Issues**: title `prod: <short signature>`, label `prod-check`, body with count, window, revision, 1-3 sample log lines (redact tokens, emails, personal data), suspected cause, and acceptance criteria for the fix (so it is buildable via the normal flow).
8. **Report**: 5 lines max. Healthy / degraded / broken, what you opened or commented, and nothing else. If everything is fine, say so in one line.

## Rules

- Read-only on GCP. Never redeploy, roll back or change config; recommend it in the issue instead.
- Never paste secrets or personal data from logs into issues.
- If gcloud is not authenticated or the project facts are missing, say exactly what is missing and stop.
