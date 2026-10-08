# The one home of every command this project runs. A CI job and a local check are
#  the same string here rather than two copies that drift apart.

# `bash` on the CI runners and on a developer machine, so a recipe behaves the
#  same everywhere. The default is `sh`, which on Windows is whatever Git happens
#  to have put on `PATH`.
set shell := ["bash", "-uc"]

# The oldest interpreter this package supports, read from `requires-python` in
#  `pyproject.toml` so the two cannot drift.
python_floor := `sed -n 's/^requires-python = ">=\([0-9]*\.[0-9]*\).*/\1/p' pyproject.toml`

[doc("Show the recipes")]
default:
    @just --list

[group("setup")]
[doc("Install the dependencies exactly as locked, plus the git hooks")]
install:
    #!/usr/bin/env bash
    set -euo pipefail

    uv sync --locked

    # The hooks gate a commit, and CI has none to gate: it calls the same
    #  recipes as workflow steps. Building their environments there would cost a
    #  download per hook for nothing.
    if [[ -z "${CI:-}" ]]; then
        uv run pre-commit install --install-hooks
    fi

[group("check")]
[doc("Check that `uv.lock` agrees with `pyproject.toml`")]
check-lock:
    uv lock --check

[group("check")]
[doc("Check the formatting and lint")]
lint:
    uv run ruff format --check .
    uv run ruff check .

[group("check")]
[doc("Auto-fix lint findings, then reformat")]
format:
    uv run ruff check --fix-only .
    uv run ruff format .

[group("test")]
[doc("Run the test suite offline, replaying the recorded answers in `tests/cassettes/`")]
test *args:
    uv run pytest {{ args }}

[group("test")]
[doc("Record the missing cassettes against the real services, keeping the rest")]
test-update *args:
    uv run pytest --record-mode=once {{ args }}

[group("test")]
[doc("Re-record every cassette against the real services")]
test-rerecord *args:
    uv run pytest --record-mode=rewrite {{ args }}

[group("test")]
[doc("Run the test suite against the oldest dependency versions the floors allow")]
test-floor:
    #!/usr/bin/env bash
    set -euo pipefail

    # `--resolution lowest-direct` rewrites `uv.lock`; keep the real one aside
    #  and restore it whatever the suite says.
    lock_backup="$(mktemp)"
    cp uv.lock "${lock_backup}"
    trap 'mv "${lock_backup}" uv.lock && uv sync' EXIT

    # Floors bind hardest on the oldest supported interpreter. `--upgrade` is
    #  what makes the strategy apply: without it the resolver keeps the locked
    #  versions, which already satisfy the floors.
    uv sync --python {{ python_floor }} --upgrade --resolution lowest-direct
    uv run --no-sync --python {{ python_floor }} pytest

[group("test")]
[doc("Ask every Shazam URL the library calls what it answers; live, never part of `ci`")]
probe:
    uv run python scripts/probe_endpoints.py

[group("check")]
[doc("Run everything CI runs")]
ci: lint test
