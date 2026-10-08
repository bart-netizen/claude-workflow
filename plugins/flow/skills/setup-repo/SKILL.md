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
   - `review.yml`: a short caller of the reusable workflow `bart-netizen/claude-workflow/.github/workflows/review.yml@v1`: after green CI an independent Claude (Opus) runs the `review` skill; one comment per PR with a verdict, updated on each push. Never approves or merges. Set `workflows:` to the exact `name:` of the repo's CI workflow. The repo's Actions settings must allow reusable workflows from other repositories.
   - `deploy.yml`: on push to `main`, deploys to Cloud Run (build runs in Cloud Build) and smoke-tests the health URL.
   - `check-prod.yml`: daily gate of seconds; Claude analyses logs only after a deploy (24h) and every Monday (7d).
   - `ci.yml`: tests on pull requests only, with dependency cache and cancel-in-progress; fill in the language block and the Project facts lint/test commands. Skip if equivalent CI exists, but add cancel-in-progress and paths-ignore to it.
   - All jobs use `runs-on: ubuntu-latest`; switching to a home runner later is a one-line change per job.
   Skip any workflow the repo already has an equivalent of; adapt instead of duplicating.
6. **GitHub Actions auth to GCP**: Workload Identity Federation, never service account keys. Check with `gcloud iam workload-identity-pools list --location=global --project=<project>`. If missing: pool `github`, OIDC provider with `--attribute-condition "assertion.repository=='<owner>/<repo>'"`, service account `github-deployer` bound via `roles/iam.workloadIdentityUser` to the repo principalSet. Least privilege by deploy style:
   - repo already has `cloudbuild.yaml` (build SA deploys): `cloudbuild.builds.editor`, `serviceusage.serviceUsageConsumer`, `iam.serviceAccountUser` on the build SA only, `storage.objectAdmin` + `storage.legacyBucketReader` on the source-staging bucket only. Deploy with `gcloud builds submit --config cloudbuild.yaml` so the manual and automatic route stay identical.
   - otherwise (`gcloud run deploy --source`): `run.admin`, `iam.serviceAccountUser` on the runtime SA, `cloudbuild.builds.editor`, `artifactregistry.writer`, `serviceusage.serviceUsageConsumer`.
   - always, for check-prod: `logging.viewer`, `run.viewer` (+ `cloudscheduler.viewer` if jobs exist).
   Show the commands and run them only after the user says yes.
7. **Repo variables and secrets**: list exactly what the user must set (`gh variable set` / `gh secret set` commands ready to paste):
   - variables: `GCP_PROJECT`, `GCP_REGION`, `CLOUD_RUN_SERVICE`, `GCP_WIF_PROVIDER`, `GCP_DEPLOY_SA`, `HEALTH_URL`
   - secret: `CLAUDE_CODE_OAUTH_TOKEN` (from `claude setup-token`), or `ANTHROPIC_API_KEY`
   - labels: create `claude` and `prod-check` with `gh label create`.
   - repo setting: allow GitHub Actions to create pull requests (`gh api -X PUT repos/<repo>/actions/permissions/workflow -f default_workflow_permissions=read -F can_approve_pull_request_reviews=true`), otherwise the auto-PR step in claude.yml fails.
   - token: tell the user to run `claude setup-token`, then `pbpaste | tr -d ' \n\r' | gh secret set CLAUDE_CODE_OAUTH_TOKEN -R <repo>` (a pasted token often breaks on line wraps: 401 "OAuth access token is invalid").
8. Open a PR with all of it, body listing what the user still has to do (step 6/7 items). Do not merge.

## Rules

- Check required status checks first (`gh api repos/<repo>/branches/main/protection --jq .required_status_checks`). Never put a paths filter on a workflow whose job is a required check.
- Test the label route once after merge with a small real docs issue: label `claude` must end in an open PR with CI running, without a click. Debug failures with `gh run rerun <id> --debug` (shows the full Claude output).

- Never put project ids, URLs of private services, tokens or customer names in the flow plugin repo; they belong in the project repo only.
- Do not change application code during setup.
