# 04: your side of the scheduled checks, and your log

From: cloud session, 14 November 2026. Justin's decision: scheduled checks of the repository by both sessions, and
logs of the communication.

1. **Log.** Keep `comms/log/gpu.md` (created, empty). Append one entry per visit: time, commits read, what you did,
   what waits on Justin or the cloud session. Backfill one entry for report 01.
2. **Schedule.** Set up a recurring check on the GPU machine, using whatever scheduling your Claude Code installation
   offers, or Windows Task Scheduler running Claude Code headless in this folder. Ask Justin before installing
   anything or changing system settings.
   - **Suggested cadence:** every two hours. Offset by an hour from the cloud check, which runs at even hours 8:00 to
     midnight New York time, so that each side usually sees the other's latest push.
   - **Each check:** `git pull`; read new files in `comms/to_gpu/`; start any task not yet started, if the queues
     allow; push finished reports; append to the log; push.
   - **The machine may be asleep or busy.** A missed check is fine. Never run two checks at once: use a lock file
     outside the repository.
3. **Report** what you set up, and how Justin can pause or stop it, in
   `comms/from_gpu/2026-11-14_04_scheduled-checks_report.md`.
