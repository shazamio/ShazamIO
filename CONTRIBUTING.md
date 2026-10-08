# Contributing

## Setup

You need [`uv`](https://docs.astral.sh/uv/) and [`just`](https://just.systems/)
on `PATH`.

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
lists which. Every pull request runs the suite on each supported interpreter.

## Tests that call Shazam

`just test` never reaches the network. A test that calls Shazam or Apple is
marked `@pytest.mark.vcr` and replays the answers recorded for it, one cassette
per test under `tests/cassettes/<module>/<test>.yaml`. Any other test that
tries to connect fails with `RuntimeError: Network is disabled`; only
`127.0.0.1` is allowed, for the local test server.

Adding a test that calls a real service:

1. Mark it `@pytest.mark.vcr`.
2. Run `just test-update`. It records the cassettes that are missing and leaves
   the existing ones alone; pass a path or `-k` to narrow it down.
3. Run `just test` offline, then commit the cassette with the test.

`just test-rerecord` replaces every cassette with what the services answer
today. Use it when an answer changed on purpose, then review the diff.

Assert on the shape of an answer, not on values Shazam is free to change: a
track key is digits, a chart has entries. A re-recorded cassette then keeps
passing as long as the library still parses what comes back.

What a cassette keeps is decided in `tests/conftest.py`, and every rule there
says why:

- Request headers are dropped, so nothing a request carries is committed.
- Response headers are kept only where the library reads them
  (`Content-Type`, `Location`). The rest are CDN details that change on every
  recording, and some name the edge nearest to whoever recorded.
- HTML bodies are emptied; the library reads only their status and headers.
- `429` responses are left out, so replay does not sleep through retries.
- The recognize URL carries two random uuids, so requests match with them
  masked.

Check a new cassette for anything personal before committing it.

## When a method returns nothing

Shazam's API is undocumented and moves without notice. `just probe` asks every
URL the library calls what it answers, one request at a time, and marks each one
that does not answer as expected. Paste its output into the issue.

## Dependency constraints

Do not add or raise a bound by guessing. `pyproject.toml` documents what its
constraints mean, and `just test-floor` measures them.
