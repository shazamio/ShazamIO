# Contributing

## Setup

You need [`uv`](https://docs.astral.sh/uv/) and [`just`](https://just.systems/)
on `PATH`, plus `ffmpeg`: the test suite decodes real audio files.

```sh
just install
```

`just --list` prints every recipe with what it does.

## Before opening a pull request

```sh
just ci
```

That is what the workflows gate on. `just format` applies what the linter can
fix by itself.

Committing runs some of the same recipes as git hooks; `.pre-commit-config.yaml`
lists which, and says why the suite is not among them. Every pull request runs
the suite instead, on each supported interpreter.

## When a method returns nothing

Shazam's API is undocumented and moves without notice. `just probe` asks every
URL the library calls what it answers, one request at a time, and marks each one
that does not answer as expected. Paste its output into the issue.

## Dependency constraints

Do not add or raise a bound by guessing. `pyproject.toml` documents what its
constraints mean, and `just test-floor` measures them.
