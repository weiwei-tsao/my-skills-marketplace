---
description: "Set up or upgrade an ai-engineering-workspace ticket workspace."
argument-hint: [WORKSPACE-PATH]
disable-model-invocation: true
---

You are setting up an ai-engineering-workspace ticket workspace.

This command may scaffold or upgrade workspace files, but it must not work on a
ticket phase and must not edit implementation repositories.

1. Choose `WORKSPACE_ROOT`:
   - If `$ARGUMENTS` names a path, use that path.
   - Otherwise, if the current dir contains `ecosystem.md` and `tickets/`,
     use that directory.
   - Otherwise ask the user where to create the workspace and stop until they
     answer.
2. Locate this plugin's workspace templates:
   `${CLAUDE_PLUGIN_ROOT}/skills/ai-engineering-workspace/templates/` when that
   variable is available, otherwise `skills/ai-engineering-workspace/templates/`
   under the plugin root.
3. If `WORKSPACE_ROOT` is new or does not contain both `ecosystem.md` and
   `tickets/`, interview only for missing setup facts, following the
   "Scaffolding a workspace" section of the `ai-engineering-workspace` skill:
   scope, repo ownership, request/data flow, ticket ID format and ticket source
   command, stages/acceptance, branch/commit/PR conventions, verification
   commands, notes repo automation, and workspace location.
4. Scaffold from the templates:
   - `ecosystem.md`
   - `conventions.md`
   - `tickets/_template/*`
   - `scripts/new-ticket.sh`
   Then make `scripts/new-ticket.sh` executable.
   Fill `ecosystem.md` and `conventions.md` from the user's answers; do not
   leave placeholders for facts the user already supplied.
5. If `WORKSPACE_ROOT` already exists, run an upgrade check before writing:
   compare each file under this plugin's `templates/tickets/` with the matching
   file under `$WORKSPACE_ROOT/tickets/_template/`, and compare
   `templates/scripts/new-ticket.sh` with
   `$WORKSPACE_ROOT/scripts/new-ticket.sh`.
   Report each file as:
   - `current` when identical
   - `missing` when absent from the workspace
   - `different` when content differs
6. For existing workspaces, ask for confirmation before overwriting any
   `different` file. Missing template files may be copied after reporting them.
   Never overwrite `ecosystem.md`, `conventions.md`, or any
   `$WORKSPACE_ROOT/tickets/<TICKET-ID>/` ticket evidence file during upgrade.
7. Finish by reporting:
   - `WORKSPACE_ROOT`
   - files created
   - template files updated or intentionally left unchanged
   - remaining placeholders the user still needs to fill
   - the next useful command, usually
     `/ai-engineering-workspace:ticket-understand <TICKET-ID>`
