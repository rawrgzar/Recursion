# External agent runtime contract

The runtime is external to this repository. An adapter should provide an agent with the repository checkout, task ID, agent ID, and base branch, then preserve the agent's branch and artifacts.

At minimum, the runtime must:

- load the task's `TASK.md` and parent context;
- use the branch-claim protocol in `docs/protocol.md`;
- allow recursive child tasks in the same format;
- keep durable state in the repository rather than relying on a live conversation;
- report completion or blocker state through the task's files and branch.

The repository intentionally does not prescribe a vendor, API, or orchestration service.
