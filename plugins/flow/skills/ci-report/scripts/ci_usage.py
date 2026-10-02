#!/usr/bin/env python3
"""Measure GitHub Actions minutes per repo and workflow, the way GitHub bills them.

Usage: ci_usage.py [--days 30] [--repos owner/a,owner/b]   (default: all your repos)
Needs: gh (authenticated). Only reads; never changes anything.

Billing rules applied (GitHub docs): each job is rounded UP to a whole minute;
public repos on standard runners are free; self-hosted runners are free.
"""
import argparse, json, math, subprocess, sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone

PRICE = {"github": 0.006, "blacksmith": 0.004, "ubicloud": 0.002}  # USD/min, 2 vCPU Linux, checked 2026-10-02


def gh(path):
    out = subprocess.run(["gh", "api", "--paginate", "--slurp", path],
                         capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit(f"gh api {path} failed: {out.stderr.strip()}")
    return json.loads(out.stdout)


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--repos", default="")
    a = ap.parse_args()
    since = (datetime.now(timezone.utc) - timedelta(days=a.days)).date().isoformat()

    if a.repos:
        repos = [(r, None) for r in a.repos.split(",")]
    else:
        listed = subprocess.run(["gh", "repo", "list", "--limit", "200", "--json",
                                 "nameWithOwner,isPrivate"], capture_output=True, text=True)
        if listed.returncode != 0:
            sys.exit(listed.stderr)
        repos = [(r["nameWithOwner"], r["isPrivate"]) for r in json.loads(listed.stdout)]

    rows, total_billed = [], 0
    for repo, private in repos:
        if private is None:
            private = gh(f"repos/{repo}")[0]["private"]
        pages = gh(f"repos/{repo}/actions/runs?per_page=100&created=>={since}")
        runs = [r for p in pages for r in p.get("workflow_runs", [])]
        agg = defaultdict(lambda: {"runs": 0, "jobs": 0, "min": 0, "selfhosted": 0, "secs": []})
        for run in runs:
            w = agg[run["name"]]
            w["runs"] += 1
            jpages = gh(f"repos/{repo}/actions/runs/{run['id']}/jobs?per_page=100")
            for job in (j for p in jpages for j in p.get("jobs", [])):
                if not job.get("started_at") or not job.get("completed_at"):
                    continue
                secs = max(0, (ts(job["completed_at"]) - ts(job["started_at"])).total_seconds())
                if secs == 0:
                    continue  # skipped jobs are not billed
                w["jobs"] += 1
                w["secs"].append(secs)
                if "self-hosted" in (job.get("labels") or []):
                    w["selfhosted"] += math.ceil(secs / 60)
                else:
                    w["min"] += math.ceil(secs / 60)
        for name, w in sorted(agg.items(), key=lambda kv: -kv[1]["min"]):
            billed = w["min"] if private else 0
            total_billed += billed
            secs = sorted(w["secs"]) or [0]
            rows.append([repo, "private" if private else "public", name, w["runs"], w["jobs"],
                         w["min"], billed, w["selfhosted"], round(secs[len(secs) // 2] / 60, 1)])

    hdr = ["repo", "vis", "workflow", "runs", "jobs", "hosted_min", "billable_min", "selfhosted_min", "median_job_min"]
    print(f"# GitHub Actions usage, last {a.days} days (since {since})\n")
    print("| " + " | ".join(hdr) + " |")
    print("|" + "---|" * len(hdr))
    for r in rows:
        print("| " + " | ".join(str(x) for x in r) + " |")
    month = total_billed * 30 / a.days
    print(f"\nBillable minutes (private, GitHub-hosted): {total_billed}  -> ~{month:.0f} per 30 days")
    print("Included free per month: Free 2000, Pro 3000 (check your plan).")
    for k, p in PRICE.items():
        print(f"If ALL billable minutes were paid on {k}: ${month * p:.2f} per month")


if __name__ == "__main__":
    main()
