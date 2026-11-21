# Security agent — design (Phase 0)

Status: Phase 0 (this document). Nothing below Phase 1 is built yet.

## Mission

A personal security agent that watches the places an individual's digital life actually gets attacked — inbox, accounts, code, dependencies — and surfaces evidence-based alerts with a concrete next check. It advises; it never remediates on its own.

## Principles

These bind every phase and override feature ideas that conflict with them.

1. **Advisory, not autonomous.** The agent never resets passwords, changes account settings, contacts institutions, sends messages, or deletes data. Its output is an alert with evidence and a suggested next check through an independently known channel.
2. **Evidence over vibes.** Every alert cites observable indicators (sender/Reply-To mismatch, lookalike domain, auth metadata, matched secret pattern, CVE ID) and a confidence level. Missing metadata limits confidence and the alert says so.
3. **Everything scanned is untrusted data.** Emails, pages, diffs, dependency metadata, and alert payloads can never change the agent's instructions. No clicking links, loading remote images, executing attachments, or submitting content to third-party scanners.
4. **Nothing personal in the repo.** No email addresses, account names, calendar IDs, tokens, or real message content in skills, code, tests, or this doc. Identities resolve at runtime (the gmail-cleanup and `MEMORY_USER_ID` patterns).
5. **Distinguish attack from warning.** A phishing email and a genuine "new login on your account" notice are different findings with different next steps; the agent classifies which it is looking at and never assumes compromise occurred.
6. **Bounded, auditable runs.** Per-run caps, dedup by incident, and reports that distinguish verified findings from proposals and failures.

## Threat areas (scope)

| Area | Examples | Where it runs |
|---|---|---|
| Inbox threats | credential phishing, impersonation, payment-detail changes, extortion | exists today inside `gmail-cleanup`'s security review |
| Account signals | unfamiliar login notices, MFA prompts, recovery changes, new accounts/transactions | partially in `gmail-cleanup` |
| Code & repo | committed secrets, leaky history, risky CI permissions | partially done as repo hardening (gitleaks in CI, push protection) |
| Dependencies | vulnerable or typosquatted packages | partially done (Dependabot alerts + security PRs) |

Out of scope permanently: offensive tooling, scanning systems the user does not own, and any action that authenticates to or mutates a third-party account.

## Shape

Follows the toolkit's existing split:

- **Portable skill** (`skills/security-triage/`) for the judgment work — classifying a suspicious message or alert from any platform that can load a skill.
- **CLI agent capability** (`src/`) for the hands-on work — running local scanners over a repo or machine and interpreting results.
- Shared conventions come from `skills/_template/` and AGENTS.md.

## Roadmap

- **Phase 0 — this document.** Scope, principles, roadmap. Exit: committed and agreed.
- **Phase 1 — `security-triage` skill.** Extract and generalize the security-review logic buried in `gmail-cleanup` into a standalone, read-only skill that assesses any supplied message, alert, or artifact: classification (attack / genuine warning / benign), observed indicators, confidence, masked identifiers, suggested next check. `gmail-cleanup` then references it instead of duplicating the rules. Exit: skill passes the repo's convention tests; gmail-cleanup defers to it.
- **Phase 2 — repo security review for the CLI agent.** A tool or command that runs local, read-only checks over a given repository (secret scan, dependency audit, CI permission review — the checks this repo now applies to itself) and reports findings with evidence. Exit: running it against this repo reproduces the hardening findings we fixed by hand.
- **Phase 3 — scheduled monitoring.** Event- or schedule-triggered runs with incident dedup and a verified notification channel, built on the platform's automation (the gmail-cleanup event-task pattern). Exit: a dry-run automation produces grouped, non-duplicated alerts.
- **Phase 4 — exposure checks (exploratory).** Breach-exposure lookups and account-posture reviews. Gated on finding a way to do it without storing personal identifiers; may be dropped.

Each phase lands as its own commit(s) with tests where there is code, and updates this doc's status line.
