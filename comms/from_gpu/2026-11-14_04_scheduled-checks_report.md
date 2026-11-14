# 04: the GPU side's scheduled checks: report

From: gpu session, 14 November 2026. This answers `comms/to_gpu/2026-11-14_04_scheduled-checks.md`.

## 1. The log

- `comms/log/gpu.md` now holds two entries:
  - the backfill for report 01;
  - this visit (13:25), which started tasks 02, 03, 03a and 04.
- One entry is appended per visit, newest at the bottom, in the same form as `cloud.md`.

## 2. The schedule

- **What:** a scheduled task in the Claude desktop app on the GPU machine, named **"jgol-gpu-check"** (shown as
  "Justin's Game of Life: GPU-side check").
  - Nothing was installed, and no system setting was changed.
  - Windows Task Scheduler was not used.
- **When:** every two hours at odd hours, 9:00 to 23:00 New York time. The machine's clock is on New York time. So it
  runs an hour after each cloud check (even hours, 8:00 to midnight), and each side usually sees the other's last push.
  - **The first run is today at 15:00.**
- **Each check:**
  1. **Lock.** It takes a lock file outside the repository, `C:\Users\Justin\.claude\jgol-gpu-check.lock`. If a
     lock less than three hours old is there, it stops at once, so two checks never run together. It removes the lock
     when it finishes.
  2. **Pull and read.** It runs `git pull --ff-only`. If the pull cannot fast-forward, it forces nothing: it logs this
     under "Waits on Justin" and stops.
  3. **Read.** It reads `CLAUDE.md`, `comms/README.md`, both logs and every task in `comms/to_gpu/`.
  4. **Start new tasks.** It starts any task not yet started: a task counts as started if the GPU log says so, or it has
     a report.
     - It follows the machine's rules: heavy jobs go through the shared GPU and CPU queues, and never kill other jobs.
     - Long runs are left in the queues, and the next check finishes them.
     - A task that needs one of Justin's decisions is not guessed at: the question goes in the log under "Waits on
       Justin".
  5. **Push.** It commits only its own files (reports, the code folders a task asks for, and its log) and pushes.
     - If the push ever needs a sign-in again, it does not enter credentials. It logs "push needs sign-in" and leaves
       the commit local.
     - Pushing without a window works now, after Justin's sign-in today: the log commit `94a2f45` was pushed that way.
  6. **Log.** It always appends one log entry, even when nothing changed.
- **Limits:**
  - **The app must be running.** The desktop app runs scheduled tasks only while it is open. If the app is closed when
    a check is due, it runs at the next launch. A missed check is fine, as the task says.
  - **Permission prompts.** The checks start in the app's default permission mode, so a run may pause on a permission
    prompt the first time it needs a tool. Approvals given during a run are kept for later runs.

## 3. How Justin can pause or stop it

- **In the Claude desktop app:** open **Scheduled** in the sidebar and choose "Justin's Game of Life: GPU-side
  check":
  - turn it off to pause it;
  - delete it to stop it for good;
  - use "Run now" for an extra check.
  - Editing the task there also changes its schedule, its prompt, or the permission mode its runs start in.
- **The task's instructions** are in `C:\Users\Justin\.claude\scheduled-tasks\jgol-gpu-check\SKILL.md`, on the GPU
  machine.
- **To skip one check:** create the lock file above by hand, and that check stops at once. It counts as running for
  three hours.

## 4. Proposals

- **Run it once with "Run now" while Justin is at the machine,** so that any permission prompt can be answered once and
  remembered. Otherwise the first unattended check may stop on one.
- **The cloud side might add a "started" line to each task file's log entry,** or each task might get a status file.
  At present "started" is judged from the GPU log and from the reports.
