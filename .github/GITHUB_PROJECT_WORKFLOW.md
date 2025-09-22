# Sample GitHub Project workflow (high-level)
## Goal: a lightweight, structured Agile flow you can run solo using GitHub Projects + Issues.

## Board layout (columns & purpose)

* Backlog — all ideas / future stories (unprioritized).
* To Do / Ready — prioritized for the next sprint; issues here have acceptance criteria and are ready to start.
* In Progress — you’re actively working on these (one feature per branch).
* In Review / QA — PR open, awaiting review/CI or manual QA.
* Done — merged, accepted, release-ready.
* Blocked (optional) — things stopped by external dependency.

## Labels (minimal, high-value)

* enhancement (feature)
* bug
* chore (ops / upgrades)
* priority:high / priority:medium / priority:low
* wip (work-in-progress)
* blocked

## Issue = user story pattern (use as Issue template)

Title: Feature — [short summary]
Body:
As a <user type>
I want <capability>
So that <benefit / why>

## Acceptance criteria

* AC1: <clear pass/fail statement>
* AC2: ...

## Definition of Done

* Code compiled / tests pass
* Unit tests added (if relevant)
* PR opened and linked to issue
* Docs/README updated if behavior changed

## Sample issues (ready to copy)

1. Title: Feature — Email/password login
   Body: As a user, I want to log in with email and password so that I can access my account.
   Acceptance criteria:
   - AC1: User can submit email + password and receive a success or error.
   - AC2: Passwords validated and errors shown for invalid credentials.
   - AC3: Successful login sets a session token and redirects to dashboard.
   Estimate: Small (1–2 days)

2. Title: Feature — Password reset flow
   Body: As a user, I want to reset a password via email so I can regain access.
   Acceptance criteria: ... 
   Estimate: Small–Medium

3. Title: Bug — Signup form validation missing client-side email check
   Body: Steps to reproduce, expected vs actual. 
   Estimate: Small

## Automation rules (use GitHub Projects automation)

* When an Issue is closed, move card → Done.
* When a PR is opened that references an Issue, move card → In Review / QA.
* When a PR is merged, automatically close Issue and move card → Done.
(These are available in GitHub Projects automation; set them once.)

## Sprint cadence (solo-friendly)

* Sprint length: 1 week (or 2 weeks if you prefer more focus).
* Planning (start): move 2–4 top-priority issues from Backlog → To Do.
* Work: pick one issue at a time, create branch feat/<short-name> or bugfix/<short-name>.
* End of sprint: close/merge what’s done; quick retrospective notes in a RETRO.md or project wiki:
  - What went well
  - What blocked me
  - Action: one change for next sprint

## Branching & PR habits (simple)

* Feature branch per issue, named 'feat/issue-123-login' or 'fix/issue-45-validation'.
* PR description: link issue (Closes #123) + short summary + testing steps.
* Use GitHub Actions for basic CI: run tests, lint, and if all pass, allow merge.

## Definition of Done checklist (copy into PR template) 

* Code builds locally and on CI
* Unit tests covering new logic added / existing tests pass
* README or CHANGELOG updated if behavior changed
* Issue linked and closes on merge