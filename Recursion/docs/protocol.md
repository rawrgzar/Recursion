# Agent and task protocol

## Task files

Each problem has a `TASK.md` with YAML front matter and Markdown instructions. Start from `problems/_template/TASK.md`.

Required metadata: `id`, `title`, `status`, `parent`, and `acceptance`. Use `parent: null` for top-level work. Status values are `ready`, `claimed`, `blocked`, and `done`.

## Claim and work

1. Read the task and its parent context before acting.
2. Claim it by creating `work/<task-id>/<agent-id>` from the task's stated base branch and publishing that branch to the shared Git remote. Use a unique agent ID; do not claim work already assigned to another active branch.
3. Update the task status to `claimed` in the branch and add a short `WORKLOG.md` entry describing the intended approach.
4. Keep changes scoped to the task. Put durable outputs in that problem's `artifacts/` folder or the shared `artifacts/` folder, and link them from `WORKLOG.md`.
5. If the task needs decomposition, create child folders under the parent's `children/` directory. Give every child a `TASK.md`, a unique ID, and a `parent` value pointing to the parent ID. Claim and execute children with the same protocol.
6. Integrate completed child results, check every acceptance item, update the task to `done`, and leave a final summary in `WORKLOG.md`.

## Handoffs and blockers

Treat committed files as the handoff surface. A successor must be able to resume from the task, work log, branches, and linked artifacts without relying on chat history. If blocked, set status to `blocked`, state the dependency and the smallest next action in `WORKLOG.md`, and preserve partial work.

## Completion

A task is complete only when each acceptance item is addressed and outputs are committed or linked. The parent task owns the final integration and completion record. Agents do not require a human to run routine execution steps.
