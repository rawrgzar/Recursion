# Architecture decisions

This scaffold records the decisions made for the first Recursion prototype.

## Coordination

Use a hybrid Git and artifact model. Git branches provide task ownership, reviewable changes, and history. Files in each problem folder and in `artifacts/` preserve outputs that should remain easy for agents to read and hand off.

## Runtime and claiming

Agents run in an external runtime; the repository defines the contract but does not launch agents. A task is claimed by creating a branch named `work/<task-id>/<agent-id>` from the current task base. The branch is the claim. Agents work without a human in the execution loop and must leave enough state in files for another agent to continue.

## Work descriptions

Use a hybrid task format: a short YAML front matter block for machine-readable identity and routing, followed by inline Markdown instructions and acceptance criteria. Keep the task self-contained in `TASK.md`.

## Autonomy

Delegation is recursive. An agent may split a task into child problem folders using the same task format and branch protocol. Children must point to their parent task. Parent agents integrate child results and record the outcome in their own task folder.

## First proofs

Build both compiler proofs:

1. **Cold start:** demonstrate that the prototype can be compiled or interpreted from its documented initial state without relying on generated compiler artifacts.
2. **Bootstrap:** demonstrate that the prototype can build the next compiler stage, then use that stage to rebuild itself or the agreed target.

The exact implementation language remains an inline prototype decision recorded with the task that implements it.
