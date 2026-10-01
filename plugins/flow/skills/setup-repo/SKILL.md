---
name: setup-repo
description: One-time setup that puts a repository on the flow - Project facts in CLAUDE.md, DECISIONS.md, the flow plugin registered in .claude/settings.json, and GitHub Actions for building issues, CI, auto-deploy to Cloud Run and production checks. Use when the user says "zet deze repo op de flow", "setup flow", or starts a new project.
when_to_use: Trigger only on an explicit request to set up or migrate a repo to this workflow, or when creating a new project repo. Safe to re-run; it only adds what is missing.
---

# Setup-repo: put a repo on the flow

Goal: after this, the user's loop is "describe idea -> add label `claude` -> review PR -> merge". Everything else runs by itself.

## Steps

1. **Inventory** (read only): language, test/lint/build commands, Dockerfile, existing `.github/workflows/`, existing CLAUDE.md. Find the GCP project, region and Cloud Run service from existing workflows, `gcloud run services list`, or ask once.
2. **CLAUDE.md**: add a `## Project facts` section from `${CLAUDE_SKILL_DIR}/templates/project-facts.md` (fill every field; unknown = `TODO(user)`). Keep the rest of CLAUDE.md as is. Keep CLAUDE.md short: facts and conventions only, procedures belong in skills.
3. **DECISIONS.md**: create if missing, with the header from `${CLAUDE_SKILL_DIR}/templates/DECISIONS.md` and one first entry describing the current architecture.
4. **Plugin for local sessions**: run
   `claude plugin marketplace add bart-netizen/claude-workflow --scope project`
   `claude plugin install flow@bart-workflow --scope project`
   and commit the resulting `.claude/settings.json`.
5. **Workflows**: copy from `${CLAUDE_SKILL_DIR}/templates/` into `.github/workflows/`, filling the placeholders:
   - `claude.yml`: builds issues labelled `claude` and answers `@claude` on issues and PRs.
   - `deploy.yml`: on push to `main`, deploys to Cloud Run, then runs a 1-hour check-prod.
   - `check-prod.yml`: weekly production check that opens issues.
   - If no CI exists for tests, add `ci.yml` running the Project facts test/lint commands on pull requests.
   Skip any workflow the repo already has an equivalent of; adapt instead of duplicating.
6. **GitHub Actions auth to GCP**: prefer Workload Identity Federation (no keys). Check with `gcloud iam workload-identity-pools list --location=global --project=<project>`. If missing, print the exact gcloud commands to create pool, provider (restricted to this repo) and a deploy service account with roles `run.admin`, `iam.serviceAccountUser`, `cloudbuild.builds.editor`, `artifactregistry.writer`, `logging.viewer`, and let the user run them. Never create service account keys.
7. **Repo variables and secrets**: list exactly what the user must set (`gh variable set` / `gh secret set` commands ready to paste):
   - variables: `GCP_PROJECT`, `GCP_REGION`, `CLOUD_RUN_SERVICE`, `GCP_WIF_PROVIDER`, `GCP_DEPLOY_SA`
   - secret: `CLAUDE_CODE_OAUTH_TOKEN` (from `claude setup-token`), or `ANTHROPIC_API_KEY`
   - labels: create `claude` and `prod-check` with `gh label create`.
8. Open a PR with all of it, body listing what the user still has to do (step 6/7 items). Do not merge.

## Rules

- Never put project ids, URLs of private services, tokens or customer names in the flow plugin repo; they belong in the project repo only.
- Do not change application code during setup.
