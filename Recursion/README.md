# Recursion

Recursion is a small, file-first scaffold for autonomous agents working on nested problems. Agents run in an external runtime and coordinate through Git branches and durable artifacts.

## Start here

1. Extract this folder and initialize it as a repository with `git init -b main`.
2. Make the initial commit so `main` exists as a base for task branches.
3. Read [`docs/architecture.md`](docs/architecture.md) and [`docs/protocol.md`](docs/protocol.md).
4. Copy [`problems/_template`](problems/_template) to a new folder under `problems/`.
5. Describe the task in that folder's `TASK.md`. Keep the metadata header and the human-readable instructions together.
6. Have an external agent claim the task on a branch, record its work, and leave artifacts in the task folder.

The `problems/hello-world` folder is a small example. The `compiler/` folder describes the two required compiler proofs: a cold start and a Bootstrap build.

## Folder map

- `agents/` — external runtime adapter contract and recursive delegation rules.
- `artifacts/` — shared durable outputs and indexes.
- `compiler/` — cold-start and Bootstrap proof plans.
- `docs/` — architecture and working protocol.
- `problems/` — problem collection, template, and example.
- `assets/` — project artwork.

This archive is a starter scaffold; it does not include an agent runtime or compiler implementation.
