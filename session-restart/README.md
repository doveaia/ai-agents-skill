# session-restart

Teach an agent to bail out cleanly and ask the operator for a fresh
session when the current session is broken by a **tooling or
infrastructure failure** (model adapter crash, remote compaction 404,
deployment-not-found, repeated provider 5xx). Retrying inside a
wedged session burns budget and corrupts state — the right move is
to persist a handover and stop.

> Agent-facing instructions live in [`SKILL.md`](./SKILL.md). This
> file is the human-facing quick start.

## When this skill fires

Trigger only on signals that the **session itself** is broken, not
the work. Canonical triggers:

- `adapter_failed` at the end of a tool/turn.
- `remote compaction failed` / `Failed to run pre-sampling compact`.
- `The API deployment for this resource does not exist` (HTTP 404)
  from the model endpoint.
- Same error reappearing after `Retried run`.
- Repeated provider 5xx on the same URL.

Do NOT trigger for: ordinary bugs, single transient errors,
recoverable rate limits, test failures, or anything fixable in-turn.

## What the agent will do

1. Stop the failing operation — no further retries.
2. Stage / commit in-progress work (WIP commit if commit-ready).
3. Write a short `HANDOVER.md` with goal, stopping point, last green
   checkpoint, the literal error, and the next step.
4. Surface the error block verbatim to the operator.
5. Tell the operator: *"Open a new session and resume from
   `HANDOVER.md`."*
6. Stop. The new session is launched by the operator, **not** by the
   dying session.

Full protocol and failure-signature table: see [`SKILL.md`](./SKILL.md).

## Example trigger (Codex / Azure OpenAI)

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

`adapter_failed` + `Retried run` + same error after the retry is the
textbook case: the session is wedged, restart in a fresh one.

## Layout

```
session-restart/
├── README.md   # this file
└── SKILL.md    # agent-facing instructions (paperclip)
```
