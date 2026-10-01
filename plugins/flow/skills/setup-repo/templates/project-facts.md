## Project facts

<!-- Read by the flow skills (spec, ship, check-prod). Keep it factual and current. -->

- Purpose: <one line, who uses it and for what>
- Stack: <language/framework>, <datastore>
- Commands: test `<cmd>` · lint `<cmd>` · typecheck `<cmd>` · build `<cmd>` · run locally `<cmd>`
- GCP project: <project-id>
- Region: <region>
- Cloud Run service(s): <service-name>
- Health URL: <https://.../health>
- Scheduled jobs / webhooks that must fire: <e.g. Cloud Scheduler "daily-sync" 06:00, Wahoo webhook>; or "none"
- Secrets live in: Secret Manager (<names>)
- Expected log noise (ignore in check-prod): <e.g. 404 on /favicon.ico>; or "none"
- Feature flags: <how they work here>; or "none"
- Way of working: new work starts as an issue written with the spec skill; implementation always ends with the ship skill (PR, never merge); production questions use check-prod.
- Out of bounds: <things Claude must never touch without asking, e.g. production data deletes, billing>
