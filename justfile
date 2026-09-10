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

[doc("Check that `uv.lock` agrees with `pyproject.toml`")]
check-lock:
    uv lock --check

[doc("Check the formatting and lint")]
lint:
    uv run ruff format --check .
    uv run ruff check .

[doc("Auto-fix lint findings, then reformat")]
format:
    uv run ruff check --fix-only .
    uv run ruff format .

[doc("Run the test suite")]
test:
    uv run pytest

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

[doc("Run everything CI runs")]
ci: lint test
