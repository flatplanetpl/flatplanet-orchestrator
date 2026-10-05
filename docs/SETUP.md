# Setup, verification and troubleshooting

[Project README](../README.md) · [Skill policies](../.agents/skills/flatplanet-orchestrator/SKILL.md) · [Benchmark harness](../benchmark/HARNESS.md)

## Compatibility boundaries

The installer/updater target **Linux with Bash, Git and GNU coreutils**. They use GNU options such as `realpath -m` and `cp --remove-destination`; a shell called Bash on another operating system does not by itself establish compatibility. Native Windows/PowerShell, macOS and WSL have no verified support matrix in the supplied benchmark record. Python 3 is needed only for the offline installer tests.

The [Luna 6 setup record](../benchmark/runs/2026-09-25-GR-UX-01-luna6.md) records Codex CLI **0.157.0**, a `/home/ubuntu/...` workspace and a specific historical skill hash. Treat that as provenance for that run, not proof that the current skill has passed end-to-end testing on that release, a minimum supported version, or a promise of current model access.

Codex must be installed and signed in separately. Confirm repository-skill discovery, subagent tools, explicit model/effort selection, and the long-wait capabilities required by the skill. The configured model IDs and reasoning levels must be available to your account and client. Do not silently map an unavailable GPT-5.6 model to a GPT-6 model or replace missing delegation with root implementation.

For current client behavior consult OpenAI's [skills documentation](https://developers.openai.com/codex/skills), [subagent configuration](https://developers.openai.com/codex/multi-agent) and [CLI reference](https://developers.openai.com/codex/cli/reference). Record your own `codex --version` and check `codex --help`; the skill does not supply or upgrade the client.

## Installation and root configuration

Follow the [quick start](../README.md#quick-start). The source clone and application repository must be different Git working trees. The target defaults to the current directory; a subdirectory is resolved to its Git root. The installer refuses an existing installation and rejects symlinked skill paths or special files.

The copy operation does not edit `.codex/config.toml`, `AGENTS.md` or other skills and does not stage or commit files. Configure the root when launching the client, for example when Astra / medium is available:

```bash
cd /path/to/application-repo &&
codex -m gpt-6-astra -c 'model_reasoning_effort="medium"'
```

The skill requests Astra as root; it cannot change the model of the session that is already interpreting it. `profile=cheap`, for example, selects the implementation worker, not the root or tester.

Custom agent files can take precedence over the model/effort requested at spawn. Check the effective settings rather than assuming that a skill parameter, accepted spawn call or root session identity proves the child's configuration. Configuration syntax and available diagnostics vary by client version; use the official subagent documentation for the version in use.

## First-run verification

After installation or update, inspect the application's working tree:

```bash
cd /path/to/application-repo &&
git status --short -- .agents/skills/flatplanet-orchestrator &&
git diff -- .agents/skills/flatplanet-orchestrator
```

`git diff` does not display the contents of newly untracked files; open those as well. Start a **new Codex session** from the application's root, then check:

1. **Discovery:** the skill is available and its loaded path is the application copy. Enter `$flatplanet-orchestrator ...` in Codex, not the shell. Check for disabled or duplicate same-name skills if discovery is ambiguous.
2. **Root:** the client's session settings show the intended root model and effort. The command above requests Astra / medium; inspect effective settings as well.
3. **Delegation:** for a bounded task that actually requires delegation, inspect the completed agent information or available session metadata. Confirm the worker's model/effort, ownership and completion, and required tester/reviewer roles. A trivial root-only task cannot validate delegation.
4. **Evidence limits:** separate requested settings from observed effective settings. If child metadata is unavailable, report **NOT VERIFIED**, not “confirmed”. A helper's export is supplementary evidence and still needs the [usage validation gate](../benchmark/HARNESS.md#usage-validation-gate) for benchmark claims. Keep raw logs and credentials private.

This is a manual verification procedure, not an automated model-access or billing check.

## Updating and backups

Finish active work first. Update the source checkout, then refresh the application:

```bash
git -C ~/flatplanet-orchestrator pull --ff-only &&
bash ~/flatplanet-orchestrator/scripts/update.sh /path/to/application-repo
```

The scripts copy from the local checkout and do not access the network themselves. A `git pull` alone updates only that source checkout. Any local edits in its skill directory are copied too, and the installer/updater reports this.

Before an update, the complete installed skill is backed up outside both repositories at:

```text
${XDG_STATE_HOME:-$HOME/.local/state}/flatplanet-orchestrator/backups/
```

The updater prints the exact backup path and source commit SHA. Matching files are replaced, not merged; new upstream files are added and local-only files remain. Recover local customizations from the backup and review obsolete local-only helpers yourself.

An update copy failure can leave a partially refreshed installation. Stop before using it, retain the printed full backup, compare it with the application copy, and restore the intended files before restarting Codex. Do not assume a failed update rolled back automatically. Do not restore a backup inside the skill-discovery tree as a second installed skill.

## Troubleshooting

| Symptom | Check or action |
|---|---|
| `Already installed` | Use `scripts/update.sh`; it backs up before replacement. |
| Skill missing or stale | Confirm application path and `SKILL.md`, check skill settings/duplicates, and start a new session. |
| Worker uses unexpected model/effort | Inspect custom-agent configuration and effective child metadata; do not treat the prompt or accepted spawn request as proof. |
| Model, effort or delegation tool unavailable | Report the compatibility blocker and choose a supported configuration explicitly; do not silently fall back. |
| Missing GNU command or unsupported option | Use the documented Linux/GNU environment; do not infer support from Bash alone. |
| Symlink or file/directory conflict | Inspect the reported path. Use a regular skill directory; do not bypass the safety check blindly. |
| Install/update lock exists | Check for another active installer before removing a genuinely stale lock. |
| Partial update | Use the complete backup printed in the error; verify recovery before running Codex. |

For script help and offline tests, run from the source checkout:

```bash
bash scripts/install.sh --help
bash scripts/update.sh --help
python3 -m unittest discover -s tests -p 'test_*.py'
```

These tests validate installer/updater behavior. They do not verify live Codex model access, actual delegation, benchmark accounting or application acceptance.
