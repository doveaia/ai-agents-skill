---
name: session-restart
description: >
  When the current agent session is broken by a tooling or infrastructure
  failure (remote compaction 404, adapter_failed, deployment-not-found,
  context that can no longer be compacted, repeated turn-level errors that
  do not depend on the agent's actions), stop the work, persist a clean
  handover (git commit + short state note), and instruct the operator to
  start a NEW session instead of retrying inside the broken one. Do NOT
  use for: bugs in the agent's own code, single transient errors that
  succeed on retry, recoverable rate limits, or anything fixable inside
  the current turn.
---

# Session restart (tooling-failure recovery)

This skill teaches the agent how to react when the *session itself* is
broken — i.e. the failure is in the model adapter, compaction service,
or model-provider deployment, not in the work being done. Retrying
inside a broken session wastes budget and corrupts state. The correct
move is to **bail out cleanly and tell the operator to open a fresh
session.**

## Failure signatures that qualify

Match on the *signature*, not the literal string — wording drifts.
These are the high-confidence triggers:

| Signal | Where it shows up | What it means |
| --- | --- | --- |
| `remote compaction failed` / `Failed to run pre-sampling compact` | codex_core / Codex stderr | The session's context can no longer be compressed by the remote compactor. It will fail again on the next turn. |
| `adapter_failed` | exit message, end of tool output | The model adapter itself errored, not your request. |
| `The API deployment for this resource does not exist` (404) | Azure OpenAI / OpenAI-compatible endpoint URL | The deployment your session is pinned to is missing or unreachable. The session cannot recover by retrying. |
| `unexpected status 5xx` repeated 3+ times on the same provider URL | any model adapter | Provider-side outage, not a request problem. |
| `context_length_exceeded` immediately after a failed compaction | model response | Compaction is broken AND context is full — the session is wedged. |
| `Retried run` followed by the same error | wrapper output | Automatic retry already happened and failed identically. Do not retry again. |

Example (verbatim from a real Codex run — use this as the canonical
case the skill is built around):

```
Error running remote compact task: unexpected status 404 Not Found:
The API deployment for this resource does not exist. ...
url: https://<account>.openai.azure.com/openai/v1/responses/compact
(adapter_failed)
Exit code 1
Retried run
... ERROR codex_core::compact_remote: remote compaction failed ...
... ERROR codex_core::session::turn: Failed to run pre-sampling compact
```

The combination of `adapter_failed` + `Retried run` + same error after
the retry is the textbook trigger.

## Signals that do NOT qualify (keep working)

- Single 429 / rate-limit error → back off and retry, do not restart.
- A tool you called returned an error you can fix (bad flag, wrong
  path, missing dep) → fix and continue.
- A unit test failed → debug, do not restart.
- A network blip on one HTTP call that succeeds on retry → continue.
- You ran out of disk / quota → ask the operator; restart will not
  help.

If you are unsure, ask the operator before bailing.

## Handover protocol (do this in order)

The session is about to end. Spend the remaining capacity making the
next session resumable.

1. **Stop the failing operation.** Do not loop on retries. Do not
   spawn subagents to "work around" the broken adapter.
2. **Persist in-progress work to disk.**
   - If files are modified: stage them (`git add <paths>`) — do *not*
     commit work that isn't intended to ship.
   - If the work is commit-ready: commit with a clear WIP message,
     e.g. `wip: <task> — session aborted, see HANDOVER.md`.
   - If files are not in a git repo: write the current state to a
     plain file the operator named (or `./session-handover.md` in cwd
     as a fallback).
3. **Write a one-screen handover note** (`HANDOVER.md` or named by the
   operator) containing:
   - **Goal** — the original task in one sentence.
   - **Where I stopped** — file paths and the exact state.
   - **What was working** — last green checkpoint (test, build, etc.).
   - **What broke the session** — paste the literal error block.
   - **Next step** — the single concrete action the next session
     should take first.
   Keep it under 40 lines. No history retelling.
4. **Surface the trigger to the operator** verbatim — paste the error
   block so they can see it was tooling, not your work.
5. **Tell the operator to start a new session.** Use this exact
   phrasing so it is unambiguous:

   > The session is wedged by a tooling failure (`adapter_failed` /
   > `remote compaction failed`). I have saved a handover at
   > `<path>`. Please open a new session and resume from that file.

6. **Do not start the new session yourself.** Restarting from inside
   the broken session re-inherits its corrupted state. The operator
   (or the harness) must launch a fresh process.

## How the new session should resume

When picked up in a fresh session, the resuming agent should:

1. Read the handover file (`HANDOVER.md` or named path) **first**.
2. Run `git status` and `git log -1` to confirm the on-disk state
   matches the handover.
3. Re-run the last known-good check (tests, build, lint) before
   continuing the work — proves the environment recovered.
4. Only then continue from "Next step" in the handover.

## What NOT to do

1. **Do not retry the broken operation more than once.** The wrapper
   may already have retried — check for `Retried run` in stderr.
2. **Do not amend or force-push** to hide the broken-session commits.
3. **Do not swap models / endpoints on your own** to dodge the
   deployment-404. Provider configuration is operator-owned; surface
   the error and let them decide.
4. **Do not delete the handover file** at the end of the new session
   without the operator's say-so — it is the audit trail.
5. **Do not invoke this skill for ordinary bugs.** If the failure is
   in the work, not the tooling, debug normally.

## Reporting back

The final message in the dying session must contain:

1. The trigger (paste the literal error block).
2. The handover file path.
3. A one-line summary of what was preserved (commit SHA, files staged,
   etc.).
4. The exact restart instruction (see step 5 of the handover
   protocol).

That is the entire output. No retry attempts, no speculation about
the cause beyond "tooling failure", no apologies.
