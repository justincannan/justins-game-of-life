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
