# Channel between the two Claude sessions

Two sessions work on this repository:
- **cloud**: the claude.ai session (design, page code, notes). No GPU.
- **gpu**: the Claude Code session on Justin's GPU machine (measurements, validations, heavy runs).

Justin decides; both sessions record his decisions as decisions and their own ideas as proposals (see THEORY_NOTES.md).

## How to talk
- Instructions for the GPU session go in `comms/to_gpu/`, one file per task, named `YYYY-MM-DD_NN_short-name.md`.
- Reports go in `comms/from_gpu/`, named after the task they answer (`..._report.md`). Put figures beside them as PNGs.
- Never edit the other side's files; reply with a new file.
- Start each session with `git pull`; commit and push when a task or report is done. Commit messages say what changed and why.
- Older instructions (before this repository) are in `queue/`.

## Ground rules
- `build/justins_game_of_life.html` is generated; change `tools/` and rebuild (see the main README).
- A result from an older page is marked superseded once the page changes in a way that affects it.
- Readouts are measures, not causes.

## Logs and scheduled checks
- Each side keeps an append-only log: `comms/log/cloud.md` and `comms/log/gpu.md`. Write only your own; one entry
  per visit, even when nothing changed ("no change" in one line is enough).
- The cloud side runs a scheduled check every two hours, 8:00 to midnight New York time. It pulls, reads new reports,
  logs, answers what it can within decisions already made, and notifies Justin of anything new.
- The GPU side runs its own scheduled check (task 04). It pulls, starts tasks it has not started, and pushes finished
  reports.
- Neither scheduled check makes a decision that is Justin's. A choice that needs him goes in the log under
  "Waits on Justin", and the cloud check tells him.
